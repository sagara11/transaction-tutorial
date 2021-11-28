from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

install_solc("0.8.1")

with open("./SimplestorageofSol.sol", "r") as file:
    simple_storage_file = file.read()

# Compile Our Solidity
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimplestorageofSol.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.1",
)

with open("compiled_file.json", "w") as file:
    json.dump(compiled_sol, file)

# To deploy a contract, you need the bytecode and the ABI

# Get bytecode
bytecode = compiled_sol["contracts"]["SimplestorageofSol.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# Get api
abi = compiled_sol["contracts"]["SimplestorageofSol.sol"]["SimpleStorage"]["abi"]

# For connecting to ganache

w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
chain_id = 1337
private_key = os.getenv("PRIVATE_KEY")
my_address = os.getenv("MY_ADDRESS")

# Create the contract in python
# contract object
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the lastest transaction
nonce = w3.eth.getTransactionCount(my_address)
# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price,
    }
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# Send this signed transaction
print("Deploying...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

# Working with the contract, you always need
# Contract Address
# Contract ABI

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change

# Initial value of favoriteNumber
print(simple_storage.functions.retrieve().call())

# Change favorite number to 511
simple_storage_store = simple_storage.functions.store(511).buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
        "gasPrice": w3.eth.gas_price,
    }
)

signed_simple_storage_store = w3.eth.account.sign_transaction(
    simple_storage_store, private_key=private_key
)

print("Updating...")
tx_store_hash = w3.eth.send_raw_transaction(signed_simple_storage_store.rawTransaction)
tx_store_receive = w3.eth.wait_for_transaction_receipt(tx_store_hash)
print("Updated!")

print(simple_storage.functions.retrieve().call())
