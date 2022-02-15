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
# Khai báo bộ biên dịch ngôn ngữ Solidity
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
# Để deploy contract (nghĩa là đưa contract lên mạng lưới Ethereum),
# ta cần bytecode và ABI của contract đó

# Get bytecode - Lấy bytecode
bytecode = compiled_sol["contracts"]["SimplestorageofSol.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# Get ABI - Lấy ABI
abi = compiled_sol["contracts"]["SimplestorageofSol.sol"]["SimpleStorage"]["abi"]

# For connecting to rinkeby
# Ta sẽ sử dụng infura (https://infura.io/) như công cụ để deploy lên mạng testnet
# Trong trường hợp này là mạng rinkeby.
# Ta sử dụng web3 để tương tác với các smart contract
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/7723014b031348d686dc1ff75338d63c")
)
chain_id = 4
private_key = os.getenv("PRIVATE_KEY")
my_address = os.getenv("MY_ADDRESS")

# Create the contract in python - Tạo contract bằng web3

# contract object - đối tượng contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the lastest transaction - Lấy transaction mới nhất của một tài khoản - address
# Số nonce của một account trong Ethereum đại diện cho số transaction mà account này đã thực hiện
# => Dựa vào số đó ta có thể biết transaction nào là mới nhất
nonce = w3.eth.getTransactionCount(my_address)

# -------------------------------------------------------------------------------------
# Các bước thao tác với transaction như sau:
# 1. Build a transaction - Khởi tạo transaction
# 2. Sign a transaction - Ký transaction
# 3. Send a transaction - Gửi transaction

# 1. Build a transaction - Khởi tạo transaction
# Note: Các function contructor(), buildTransaction() có thể tìm thấy ở thư viện web3 https://web3js.readthedocs.io/en/v1.7.0/
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price,
    }
)

# 2. Sign a transaction - Ký transaction
# Ký transaction có params là transaction và private key của người gửi
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# 3. Send a transaction - Gửi transaction
print("Deploying...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# Đợi transaction được validate bởi các miner trên mạng lưới ta deploy smart contract lên
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

# -----------------------------------------------------------------------------------

# Working with the contract, you always need
# Contract Address
# Contract ABI

# Khi ta muốn tương tác với contract (Gọi các hàm trong smart contract), ta cần 2 thứ:
# Địa chỉ contract
# ABI của contract
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change
# Ta cần chú ý 2 hàm hay sử dụng và sự tác động của nó vào Ethereum State:
#   Call => Chỉ gọi đến hàm trong contract và lấy giá trị trả về (Không làm thay đổi Ethereum State)
#   Transact => Gọi đến hàm trong contract và thay đổi Ethereum State

# Initial value of favoriteNumber - Giá trị ban đầu của favoriteNumber
print(simple_storage.functions.retrieve().call())

# Khởi tạo 1 transaction thực hiện hàm store(511) trong contract SimplestorageofSol
# Change favorite number to 511 - Thay đổi giá trị của favoriteNumber -> Thay đổi Ethereum State
simple_storage_store = simple_storage.functions.store(511).buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
        "gasPrice": w3.eth.gas_price,
    }
)

# Ký transaction bằng private key của người gửi
signed_simple_storage_store = w3.eth.account.sign_transaction(
    simple_storage_store, private_key=private_key
)

# Deploy transaction lên mạng lưới Ethereum trong trường hợp này là mạng rinkerby
print("Updating...")
tx_store_hash = w3.eth.send_raw_transaction(signed_simple_storage_store.rawTransaction)
tx_store_receive = w3.eth.wait_for_transaction_receipt(tx_store_hash)
print("Updated!")

# Gọi lại hàm retrieve() để kiểm chứng kết quả
print(simple_storage.functions.retrieve().call())

# Để kiểm tra lại transaction vừa gửi, ta truy cập trang web https://rinkeby.etherscan.io/
# Nhập địa chỉ người gửi hoặc transaction hash để xem chi tiết transaction đã được deploy lên mạng lưới rinkeby
