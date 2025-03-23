import requests
import json

# RPC Configuration
RPC_USER = "Cryptocrew"
RPC_PASSWORD = "abc123"
RPC_PORT = 18443
RPC_URL = f"http://{RPC_USER}:{RPC_PASSWORD}@localhost:{RPC_PORT}"

def rpc_call(method, params=[]):
    """Helper function to make RPC calls to bitcoind."""
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"jsonrpc": "1.0", "id": "python", "method": method, "params": params})
    response = requests.post(RPC_URL, headers=headers, data=payload)
    return response.json()

# Step 1: Get UTXO for Address B
utxos = rpc_call("listunspent", [1, 9999999, [" myGWbh8Qco2ruabgtd5gwPiGhHamVUMeAt"]])
if not utxos["result"]:
    print(" No UTXOs found for Address B. Ensure the previous transaction is confirmed.")
    exit()

utxo = utxos["result"][0]  # Take the first available UTXO
txid = utxo["txid"]
vout = utxo["vout"]
amount = utxo["amount"]

print(" Wallet is loaded")
print(f" Found UTXO for Address B: TXID {txid}, Amount {amount} BTC")

# Step 2: Create a Transaction from B to C
address_C = "mzR3K2h4rXzAuRhzJE8fhyLVQaqRG3m9nQ"
send_amount = amount - 0.0001  # Deduct fee

raw_tx = rpc_call("createrawtransaction", [[{"txid": txid, "vout": vout}], {address_C: send_amount}])
print(f"Raw Transaction: {raw_tx['result']}")

# Step 3: Sign the Transaction
signed_tx = rpc_call("signrawtransactionwithwallet", [raw_tx["result"]])
if not signed_tx["result"]["complete"]:
    print(" Transaction signing failed.")
    exit()
signed_tx_hex = signed_tx["result"]["hex"]
print(f" Signed Transaction HEX: {signed_tx_hex}")

# Step 4: Decode and Format the Transaction in One Line
decoded_tx = rpc_call("decoderawtransaction", [signed_tx_hex])
decoded_tx_one_line = json.dumps(decoded_tx["result"], separators=(",", ":"))
print(f" Decoded Transaction: {decoded_tx_one_line}")

# Print the Amount Transferred from B to C
print(f" Amount Sent from B to C: {send_amount} BTC")

# Step 5: Extract and Compare ScriptSig & ScriptPubKey
vin = decoded_tx["result"]["vin"][0]
scriptSig = vin["scriptSig"]["hex"]

vout_data = decoded_tx["result"]["vout"][0]
scriptPubKey = vout_data["scriptPubKey"]["hex"]

print(f" ScriptSig for B → C: {scriptSig}")
print(f" ScriptPubKey for B → C: {scriptPubKey}")

# Step 6: Broadcast the Transaction
broadcast_tx = rpc_call("sendrawtransaction", [signed_tx_hex])
print(f" Broadcasted Transaction ID: {broadcast_tx['result']}")
