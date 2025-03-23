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
            print(f" Wallet '{wallet_name}' loaded.")
        except JSONRPCException:
            rpc_connection.createwallet(wallet_name)
            print(f" Wallet '{wallet_name}' created.")

    # Switch to the loaded wallet
    rpc_connection = AuthServiceProxy(f"{rpc_url}/wallet/{wallet_name}")

    # 2️⃣ Generate Three P2SH-SegWit Addresses: A', B', C'
    addr_Ap = rpc_connection.getnewaddress("A", "p2sh-segwit")
    addr_Bp = rpc_connection.getnewaddress("B", "p2sh-segwit")
    addr_Cp = rpc_connection.getnewaddress("C", "p2sh-segwit")

    print(f" P2SH-SegWit Address A: {addr_Ap}")
    print(f" P2SH-SegWit Address B: {addr_Bp}")
    print(f" P2SH-SegWit Address C: {addr_Cp}")

    # 3️⃣ Fund Address A' (Mine Blocks + Send BTC)
    rpc_connection.generatetoaddress(101, addr_Ap)  # Mine 101 blocks to unlock funds
    txid_fund = rpc_connection.sendtoaddress(addr_Ap, Decimal("10.0"))  # Send 10 BTC to A'
    print(f" Funded Address A with 10 BTC: {txid_fund}")

    # 🛠 FIX: Mine 1 more block to confirm funding transaction
    rpc_connection.generatetoaddress(1, addr_Ap)  # Confirm the 10 BTC transaction

    # 4️⃣ Ensure UTXOs Exist
    utxos = rpc_connection.listunspent(1, 9999999, [addr_Ap])
    if not utxos:
        raise Exception(" No UTXOs found in Address A! Try mining another block.")

    input_utxo = utxos[0]  # Select the first available UTXO

    # 5️⃣ Create & Broadcast Transaction (A' → B')
    fee = Decimal("0.0001")
    send_amount = Decimal("4.8")  # Slightly reduce amount to cover fee
    change_amount = input_utxo["amount"] - send_amount - fee

    if change_amount <= 0:
        raise Exception(" Not enough balance after fees!")

    outputs = {addr_Bp: send_amount, addr_Ap: change_amount}
    raw_tx = rpc_connection.createrawtransaction([{"txid": input_utxo["txid"], "vout": input_utxo["vout"]}], outputs)
    signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx)

    if not signed_tx["complete"]:
        raise Exception(" Transaction signing failed!")

    txid_broadcast = rpc_connection.sendrawtransaction(signed_tx["hex"])
    print(f" Broadcasted Transaction ID for A to B: {txid_broadcast}")

    # 6️⃣ Mine a Block to Confirm Transaction
    rpc_connection.generatetoaddress(1, addr_Ap)

    # 7️⃣ Fetch UTXOs for Address B'
    utxos_B = rpc_connection.listunspent(1, 9999999, [addr_Bp])
    if not utxos_B:
        raise Exception(" No UTXOs found in Address B! Try mining another block.")

    input_utxo_B = utxos_B[0]  # Select first UTXO

    # 8️⃣ Create & Broadcast Transaction (B' → C')
    send_amount_B = Decimal("4.7")  # Slightly less to cover fees
    change_amount_B = input_utxo_B["amount"] - send_amount_B - fee

    outputs_B = {addr_Cp: send_amount_B, addr_Bp: change_amount_B}
    raw_tx_B = rpc_connection.createrawtransaction([{"txid": input_utxo_B["txid"], "vout": input_utxo_B["vout"]}], outputs_B)
    signed_tx_B = rpc_connection.signrawtransactionwithwallet(raw_tx_B)

    if not signed_tx_B["complete"]:
        raise Exception(" Transaction signing failed!")

    txid_broadcast_B = rpc_connection.sendrawtransaction(signed_tx_B["hex"])
    print(f" Broadcasted Transaction ID for B to C: {txid_broadcast_B}")

    # 9️⃣ Decode and Analyze Transactions
    decoded_tx_AtoB = rpc_connection.decoderawtransaction(signed_tx["hex"])
    decoded_tx_BtoC = rpc_connection.decoderawtransaction(signed_tx_B["hex"])

    print(f" Decoded A to B Transaction:\n{decoded_tx_AtoB}")
    print(f" Decoded B to C Transaction:\n{decoded_tx_BtoC}")

    #  Extract Locking and Unlocking Scripts
    scriptPubKey_B = decoded_tx_AtoB["vout"][0]["scriptPubKey"]["hex"]
    scriptPubKey_C = decoded_tx_BtoC["vout"][0]["scriptPubKey"]["hex"]

    print(f" ScriptPubKey for A to B: {scriptPubKey_B}")
    print(f" ScriptPubKey for B to C: {scriptPubKey_C}")

    # Extract Unlocking Scripts (scriptSig or witness)
    unlocking_scripts_AtoB = []
    unlocking_scripts_BtoC = []

    for vin in decoded_tx_AtoB["vin"]:
        if "scriptSig" in vin:
            unlocking_scripts_AtoB.append(vin["scriptSig"]["hex"])
        if "witness" in vin:
            unlocking_scripts_AtoB.extend(vin["witness"])

    for vin in decoded_tx_BtoC["vin"]:
        if "scriptSig" in vin:
            unlocking_scripts_BtoC.append(vin["scriptSig"]["hex"])
        if "witness" in vin:
            unlocking_scripts_BtoC.extend(vin["witness"])

    print(f" ScriptSig for A to B: {unlocking_scripts_AtoB}")
    print(f" ScriptSig for B to C: {unlocking_scripts_BtoC}")

except Exception as e:
    print(f"⚠ Error: {e}")