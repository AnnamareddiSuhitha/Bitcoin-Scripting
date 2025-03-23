from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal

# 🔗 Connect to Bitcoin Core RPC
rpc_user = "Cryptocrew"
rpc_password = "abc123"
rpc_url = f"http://{rpc_user}:{rpc_password}@127.0.0.1:18443"
rpc_connection = AuthServiceProxy(rpc_url)

try:
    # 1️⃣ Load or Create a Wallet
    wallet_name = "testwallet"
    wallets = rpc_connection.listwallets()

    if wallet_name not in wallets:
        try:
            rpc_connection.loadwallet(wallet_name)
        except JSONRPCException:
            rpc_connection.createwallet(wallet_name)

    print(" Wallet is loaded")

    #  Use the wallet RPC URL after loading/creating it
    rpc_connection = AuthServiceProxy(f"{rpc_url}/wallet/{wallet_name}")

    # 2️⃣ Generate Three Legacy Addresses: A, B, C
    addr_A = rpc_connection.getnewaddress("A", "legacy")
    addr_B = rpc_connection.getnewaddress("B", "legacy")
    addr_C = rpc_connection.getnewaddress("C", "legacy")

    print(f" Address A: {addr_A}")
    print(f" Address B: {addr_B}")
    print(f" Address C: {addr_C}")

    # 3️⃣ Mine 101 Blocks to Unlock Coinbase Rewards BEFORE Funding A
    rpc_connection.generatetoaddress(101, addr_C)  
    print("  Mined 101 blocks to unlock funds")

    # 4️⃣ Fund Address A (Send 10 BTC)
    txid_fund = rpc_connection.sendtoaddress(addr_A, Decimal("10.0"))
    print(f" Funded Address A with 10 BTC")

    # 5️⃣ Wait for the transaction to be mined (1 block)
    rpc_connection.generatetoaddress(1, addr_C)

    # 6️⃣ Get UTXO from Address A
    utxos = rpc_connection.listunspent(1, 9999999, [addr_A])
    if not utxos:
        raise Exception("No UTXOs found in Address A!")

    input_utxo = utxos[0]  # Select the first available UTXO
    inputs = [{"txid": input_utxo["txid"], "vout": input_utxo["vout"]}]

    # 7️⃣ Create a Raw Transaction (Send 5 BTC from A → B, rest as change to A)
    amount_to_B = Decimal("5.0")  # Amount being sent to B
    amount_to_A = input_utxo["amount"] - Decimal("5.0001")  # Change to A (subtracting fee)

    outputs = {
        addr_B: amount_to_B,  # Send 5 BTC to B
        addr_A: amount_to_A  # Change back to A
    }

    raw_tx = rpc_connection.createrawtransaction(inputs, outputs)
    print(f" Raw Transaction: {raw_tx}")

    # 8️⃣ Let Bitcoin Core Adjust the Fee Automatically
    funded_tx = rpc_connection.fundrawtransaction(raw_tx)
    raw_tx_funded = funded_tx["hex"]

    #  Sign the Transaction
    signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx_funded)
    if not signed_tx["complete"]:
        raise Exception(" Transaction signing failed!")

    signed_hex = signed_tx["hex"]
    print(f" Signed Transaction HEX: {signed_hex}")

    # 9️⃣ Decode & Analyze Transaction
    decoded_tx = rpc_connection.decoderawtransaction(signed_hex)
    print(f" Decoded Transaction:\n{decoded_tx}")

    #  Print the Amount Transferred from A to B
    print(f" Amount Sent from A to B: {amount_to_B} BTC")

    # Extracting and Printing the ScriptSig (Unlocking Script)
    scriptSig = decoded_tx["vin"][0]["scriptSig"]["hex"]
    print(f" ScriptSig for A to B: {scriptSig}")

    # Extract and print the ScriptPubKey for Address B
    scriptPubKey_B = decoded_tx["vout"][0]["scriptPubKey"]["hex"]
    print(f" ScriptPubKey for A to B: {scriptPubKey_B}")

    # Broadcast the Transaction
    txid_broadcast = rpc_connection.sendrawtransaction(signed_hex)
    print(f" Broadcasted Transaction ID: {txid_broadcast}")

    # Mine a Block to Confirm the Transaction
    rpc_connection.generatetoaddress(1, addr_C)

except Exception as e:
    print(f" Error: {e}")
