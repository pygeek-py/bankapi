from web3 import Web3
import os
from dotenv import load_dotenv
import json
from django.http import JsonResponse

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER")))

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]

backend_address = os.getenv("BACKEND_ADDRESS")
backend_private_key = os.getenv("BACKEND_PRIVATE_KEY")
vault_address = os.getenv("VAULT_CONTRACT_ADDRESS")

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Build the absolute path to TokenVault.json
abi_path = os.path.join(current_dir, "TokenVault.json")

tokens_list = os.path.join(current_dir, "token_list.json")

with open(abi_path) as f:
    vault_abi = json.load(f)

with open(tokens_list) as f:
    list_token = json.load(f)

vault = w3.eth.contract(address=vault_address, abi=vault_abi)

def withdraw_token(token_address, recipient, user, amount, decimals=18):
    try:
        parsed_amount = int(amount * (10 ** decimals))

        print(parsed_amount)
        
        tx = vault.functions.withdraw(
            token_address,
            recipient,
            user,
            parsed_amount
        ).build_transaction({
            "from": backend_address,
            "nonce": w3.eth.get_transaction_count(backend_address),
            "gas": 600000,
            "gasPrice": w3.eth.gas_price,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, backend_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            return {"status": "success", "tx_hash": w3.to_hex(tx_hash)}
        else:
            return {"status": "failed", "tx_hash": w3.to_hex(tx_hash)}

    except Exception as e:
        return { "status": "error", "message": str(e)}

def transfer_within(token_address, from_address, to_address, amount, decimals=18):
    try:
        parsed_amount = int(amount * (10 ** decimals))

        print(parsed_amount)

        tx = vault.functions.transferWithin(
            token_address,
            from_address,
            to_address,
            parsed_amount
        ).build_transaction({
            "from": backend_address,
            "nonce": w3.eth.get_transaction_count(backend_address),
            "gas": 600000,
            "gasPrice": w3.eth.gas_price,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, backend_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            return {"status": "success", "tx_hash": w3.to_hex(tx_hash)}
        else:
            return {"status": "failed", "tx_hash": w3.to_hex(tx_hash)}
    except Exception as e:
        return { "status": "error", "message": str(e)}

def get_all_user_balances(user_address: str):
    """
    Calls getAllUserTokenBalance from TokenVault
    """
    tokens, balances = vault.functions.getAllUserTokenBalance(user_address).call()
    
    result = []
    for token, balance in zip(tokens, balances):
        try:
            # Get token decimals & symbol
            token_contract = w3.eth.contract(address=token, abi=ERC20_ABI)
            decimals = token_contract.functions.decimals().call()
            symbol = token_contract.functions.symbol().call()
            
            # Convert balance
            human_balance = balance / (10 ** decimals)
            
            result.append({
                "token": token,
                "symbol": symbol,
                "raw_balance": str(balance),
                "human_balance": human_balance
            })
        except Exception:
            # fallback in case token doesn’t follow ERC20
            result.append({
                "token": token,
                "symbol": "UNKNOWN",
                "raw_balance": str(balance),
                "human_balance": balance
            })
    return result

