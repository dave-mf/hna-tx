import requests
import json
import logging
from web3 import Web3
import time
from colorama import init, Fore, Style
from datetime import datetime
import math
import random

init(autoreset=True)

print(Fore.CYAN + Style.BRIGHT + """t.me/dpangestuw""" + Style.RESET_ALL)
print(Fore.CYAN + Style.BRIGHT + """Auto Deposit Multi Network for HANAFUDA""" + Style.RESET_ALL)
print()

def refresh_access_token(refresh_token):
    api_key = "AIzaSyDipzN0VRfTPnMGhQ5PSzO27Cxm3DohJGY"
    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"

    headers = {
        "Content-Type": "application/json",
    }

    body = json.dumps({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    })

    response = requests.post(url, headers=headers, data=body)

    if response.status_code != 200:
        error_response = response.json()
        raise Exception(f"Failed to refresh access token: {error_response['error']}")

    return response.json()

def validate_tx_hash(tx_hash):
    if not isinstance(tx_hash, str) or not tx_hash.startswith('0x') or len(tx_hash) != 66:
        raise ValueError(f"Invalid transaction hash format: {tx_hash}")
    if any(c not in '0123456789abcdefABCDEF' for c in tx_hash[2:]):
        raise ValueError(f"Transaction hash contains invalid characters: {tx_hash}")

def sync_transaction(tx_hash, chain_id, access_token):
    url = "https://hanafuda-backend-app-520478841386.us-central1.run.app/graphql"
    query = """
        mutation SyncEthereumTx($chainId: Int!, $txHash: String!) {
          syncEthereumTx(chainId: $chainId, txHash: $txHash)
        }
    """
    variables = {
        "chainId": chain_id,
        "txHash": tx_hash
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {access_token}"
    }
    
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to sync transaction: {response.json()}")
    return response.json()

def load_refresh_token_from_file():
    try:
        with open("tokens.json", "r") as token_file:
            tokens = json.load(token_file)
            return tokens[0].get("refresh_token")
    except FileNotFoundError:
        logging.error("File 'tokens.json' not found.")
        print(Fore.RED + Style.BRIGHT + "File 'tokens.json' tidak ditemukan." + Style.RESET_ALL)
        exit()
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from 'tokens.json'.")
        exit()

def select_chain():
    print(Fore.YELLOW + Style.BRIGHT + "Select the blockchain network:" + Style.RESET_ALL)
    print(Fore.GREEN + "1. Base Mainnet" + Style.RESET_ALL)
    print(Fore.GREEN + "2. OP Mainnet" + Style.RESET_ALL)
    print(Fore.GREEN + "3. Blast Mainnet" + Style.RESET_ALL)
    print()
    choice = input(Fore.YELLOW + "Enter the number for your choice: " + Style.RESET_ALL)

    if choice == '1':
        rpc_url = "https://base-mainnet.public.blastapi.io"
        contact_address = "0xC5bf05cD32a14BFfb705Fb37a9d218895187376c" 
    elif choice == '2':
        rpc_url = "https://mainnet.optimism.io"
        contact_address = "0xC5bf05cD32a14BFfb705Fb37a9d218895187376c" 
    elif choice == '3':
        rpc_url = "https://rpc.ankr.com/blast"
        contact_address = "0x56Eff3c3F7bDdb4a58c7241b7695a72762D01baE" 
    else:
        print(Fore.RED + "Invalid choice. Exiting..." + Style.RESET_ALL)
        exit()

    return rpc_url, contact_address

RPC_URL, CONTACT_ADDRESS = select_chain()  

web3 = Web3(Web3.HTTPProvider(RPC_URL))
chain_id = web3.eth.chain_id
amount = 0.000000000000000001
value_in_wei = web3.to_wei(amount, 'ether')

num_transactions = int(input(Fore.YELLOW + "Enter the number of transactions to be executed: " + Style.RESET_ALL))

private_keys = [line.strip() for line in open("pvkey.txt") if line.strip()]

contract_abi = '''
[
    {
        "constant": false,
        "inputs": [],
        "name": "depositETH",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]
'''

contract = web3.eth.contract(address=CONTACT_ADDRESS, abi=json.loads(contract_abi))

nonces = {key: web3.eth.get_transaction_count(web3.eth.account.from_key(key).address) for key in private_keys}
tx_count = 0

refresh_token = load_refresh_token_from_file()

def get_latest_nonce(web3, address):
    return web3.eth.get_transaction_count(address, 'pending')

def wait_for_transaction(web3, tx_hash, timeout=120):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            receipt = web3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return receipt
        except Exception:
            pass
        time.sleep(1)
    raise TimeoutError(f"Transaction not mined after {timeout} seconds")

def send_transaction_with_retry(web3, transaction, private_key, max_retries=3):
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Reset nonce setiap retry
            current_nonce = web3.eth.get_transaction_count(web3.eth.account.from_key(private_key).address, 'pending')
            transaction['nonce'] = current_nonce
            
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Tunggu konfirmasi dengan timeout yang lebih pendek
            for _ in range(30):  # 30 detik timeout
                try:
                    receipt = web3.eth.get_transaction_receipt(tx_hash)
                    if receipt is not None:
                        return receipt
                except Exception:
                    pass
                time.sleep(1)
            
            # Jika tidak ada receipt setelah 30 detik, raise exception
            raise TimeoutError("Transaction stuck: no receipt after 30 seconds")
            
        except Exception as e:
            last_error = e
            print(Fore.YELLOW + f"\nRetrying transaction (attempt {attempt + 1}/{max_retries})..." + Style.RESET_ALL)
            time.sleep(2 ** attempt)  # Exponential backoff
            continue
    
    raise Exception(f"Failed after {max_retries} attempts. Last error: {str(last_error)}")

def get_low_priority_gas_fee(web3):
    try:
        # Mendapatkan base fee dari block terbaru
        base_fee = web3.eth.get_block('latest').baseFeePerGas
        gas_price = web3.eth.gas_price
        
        # Menggunakan base fee sebagai minimum dan menambahkan sedikit tip
        max_fee_per_gas = base_fee + (gas_price // 10)  # base fee + 10% dari gas price sebagai tip
        
        return max_fee_per_gas, max_fee_per_gas
    except Exception as e:
        # Fallback ke gas price standar jika gagal mendapatkan base fee
        gas_price = web3.eth.gas_price
        return gas_price, gas_price

def calculate_transaction_estimate(web3, address, gas_price):
    balance = web3.eth.get_balance(address)
    gas_cost = gas_price * 50000  # 50000 adalah gas limit yang kita gunakan
    transaction_cost = gas_cost + value_in_wei
    
    # Estimasi dengan asumsi gas fee bisa naik 2x lipat
    conservative_cost = transaction_cost * 2
    
    # Sisakan 10% saldo untuk jaga-jaga
    usable_balance = balance * 0.9
    
    max_transactions = int(usable_balance / conservative_cost)
    return balance, max_transactions, gas_cost

def display_transaction_info(web3, address, gas_price):
    balance, max_tx, gas_cost = calculate_transaction_estimate(web3, address, gas_price)
    
    print(Fore.YELLOW + "\n=== Informasi Transaksi ===" + Style.RESET_ALL)
    print(Fore.CYAN + f"Saldo: {web3.from_wei(balance, 'ether'):.8f} ETH" + Style.RESET_ALL)
    print(Fore.CYAN + f"Estimasi Gas Fee: {web3.from_wei(gas_cost, 'ether'):.12f} ETH per transaksi" + Style.RESET_ALL)
    print(Fore.CYAN + f"Estimasi Jumlah Transaksi yang Bisa Dilakukan: {max_tx:,}" + Style.RESET_ALL)
    
    # Warning jika saldo sudah rendah
    if balance < (gas_cost * 10):
        print(Fore.RED + "⚠️ PERINGATAN: Saldo sangat rendah, hanya cukup untuk < 10 transaksi!" + Style.RESET_ALL)
    elif balance < (gas_cost * 50):
        print(Fore.YELLOW + "⚠️ Perhatian: Saldo cukup untuk < 50 transaksi" + Style.RESET_ALL)

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.0f} detik"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.0f} menit"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} jam"

def display_progress(current, total, start_time):
    now = time.time()
    elapsed = now - start_time
    if current > 0:
        est_total_time = (elapsed / current) * total
        remaining = est_total_time - elapsed
        progress = (current / total) * 100
        
        print(Fore.CYAN + f"\rProgress: [{current}/{total}] {progress:.1f}% | " +
              f"Waktu: {format_time(elapsed)} | " +
              f"Estimasi Selesai: {format_time(remaining)}" + Style.RESET_ALL, end="")

def safety_check(web3, address, num_transactions, gas_price):
    balance, max_tx, gas_cost = calculate_transaction_estimate(web3, address, gas_price)
    
    if num_transactions > 1000:
        print(Fore.YELLOW + "\n=== Peringatan Transaksi Besar ===" + Style.RESET_ALL)
        print(Fore.YELLOW + f"Anda akan melakukan {num_transactions:,} transaksi" + Style.RESET_ALL)
        print(Fore.CYAN + f"Estimasi waktu: {format_time(num_transactions * 1.5)}" + Style.RESET_ALL)
        
        if num_transactions > max_tx:
            print(Fore.RED + f"\n⚠️ PERINGATAN: Saldo tidak cukup untuk {num_transactions:,} transaksi!")
            print(f"Maksimum transaksi yang bisa dilakukan dengan saldo saat ini: {max_tx:,}" + Style.RESET_ALL)
            
        confirm = input(Fore.YELLOW + "\nLanjutkan transaksi? (y/n): " + Style.RESET_ALL)
        if confirm.lower() != 'y':
            print(Fore.RED + "Transaksi dibatalkan." + Style.RESET_ALL)
            exit()

# Tambahkan safety check sebelum memulai transaksi
safety_check(web3, web3.eth.account.from_key(private_keys[0]).address, num_transactions, web3.eth.gas_price)

start_time = time.time()
success_count = 0
error_count = 0

for i in range(num_transactions):
    for private_key in private_keys:
        from_address = web3.eth.account.from_key(private_key).address
        short_from_address = from_address[:4] + "..." + from_address[-4:]

        try:
            # Get fresh nonce setiap transaksi
            nonces[private_key] = web3.eth.get_transaction_count(from_address, 'pending')
            
            max_fee_per_gas, max_priority_fee_per_gas = get_low_priority_gas_fee(web3)
            
            if i == 0:
                display_transaction_info(web3, from_address, max_fee_per_gas)
                print(Fore.GREEN + "\nMemulai transaksi..." + Style.RESET_ALL)
            
            access_token_info = refresh_access_token(refresh_token)
            access_token = access_token_info["access_token"]
            refresh_token = access_token_info.get("refresh_token", refresh_token)

            transaction = contract.functions.depositETH().build_transaction({
                'from': from_address,
                'value': value_in_wei,
                'gas': 50000,
                'maxFeePerGas': max_fee_per_gas,
                'maxPriorityFeePerGas': max_priority_fee_per_gas,
                'type': 2,
                'nonce': nonces[private_key],
            })

            # Kirim transaksi dengan retry
            receipt = send_transaction_with_retry(web3, transaction, private_key)
            tx_hash_hex = receipt['transactionHash'].hex()
            
            if not tx_hash_hex.startswith('0x'):
                tx_hash_hex = '0x' + tx_hash_hex

            validate_tx_hash(tx_hash_hex)
            
            # Sync transaksi dengan retry
            sync_response = sync_transaction(tx_hash_hex, chain_id, access_token)
            
            if sync_response.get('data', {}).get('syncEthereumTx'):
                success_count += 1
                display_progress(i + 1, num_transactions, start_time)
            else:
                raise Exception("Sync failed")

            # Tambah delay random untuk menghindari rate limiting
            time.sleep(random.uniform(1.0, 2.0))

        except Exception as e:
            error_count += 1
            print(Fore.RED + f"\nError pada transaksi {i + 1}: {str(e)}" + Style.RESET_ALL)
            
            if error_count >= 5:
                print(Fore.RED + "\n⚠️ Terlalu banyak error berturut-turut, menghentikan proses..." + Style.RESET_ALL)
                break
            
            # Tunggu lebih lama jika terjadi error
            time.sleep(5)

total_time = time.time() - start_time
print(Fore.GREEN + f"\n\nTransaksi selesai!" + Style.RESET_ALL)
print(Fore.CYAN + f"Total waktu: {format_time(total_time)}")
print(f"Transaksi berhasil: {success_count}")
print(f"Transaksi gagal: {error_count}" + Style.RESET_ALL)
