# Bitcoin-Scripting

## Team
Team-name: CryptoCrew<br>
Annamareddi Suhitha - cse230001008,<br>
Polathala Bhavana - mc230041026,<br>
Vangapally PranavaReddy - mc230041037.

## Description

This project demonstrates the process of creating, signing, and broadcasting Bitcoin transactions on a Bitcoin Core regtest network using Python scripts. It includes sending transactions between addresses, mining blocks to confirm transactions, and debugging them using btcdeb in two different type of transactions

## Features

- Automated Bitcoin transaction creation and signing.
- Uses Bitcoin Core's bitcoind in regtest mode.
- Generates addresses and manages wallets.
- Implements UTXO handling and change outputs.
- Debugging transactions with btcdeb.

## Prerequisites

1. *Install Bitcoin Core*
   - Download from [Bitcoin Core official site](https://bitcoincore.org/)
   - Install and configure bitcoind
2. *Install Python and Dependencies*
   - Python 3.x is required
   - Install dependencies using:
     pip install python-bitcoinrpc requests
     
3. *Bitcoin Configuration File (bitcoin.conf)
   Ensure bitcoin.conf contains:
   [regtest]
   regtest=1
   server=1
   rpcuser=Cryptocrew
   rpcpassword=abc123
   txindex=1
   fallbackfee=0.0002
   mintxfee=0.00001
   paytxfee=0.0001
   txconfirmtarget=6
   rpcallowip=127.0.0.1
   rpcbind=127.0.0.1
   testnet=1
   rpcport=18443
   

## Execution Steps

### 1. Start Bitcoin Regtest Mode
bitcoind -regtest -daemon

Verify if bitcoind is running:
bitcoin-cli -regtest getblockchaininfo


### 2. Run the First Script (P2PKH Transactions)
python first_script.py

- Generates three legacy addresses (A, B, C)
- Mines 101 blocks to unlock coinbase rewards
- Funds Address A and performs transactions
- Debug transactions

### 3. Change Address B in second_script.py

*Before running second_script.py, replace Address B in the script with the output from the first script.*

### 4. Run the Second Script (Continuing Transactions)

python legacy2.py

- Retrieves UTXO for Address B
- Sends funds from B to C
- Debug transactions
## Run the following command to SSH into the debugging environment:

bash
C:\Program Files\Bitcoin\bitcoin-28.1\bin>ssh -x guest@10.206.4.201
Enter the password(root1234) when prompted.
Upon successful login, you should see:

bash
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 6.8.0-52-generic x86_64)

### 5. Debug The Transactions(P2PKH)
Use the command,
btcdeb '[scriptSig] [scriptPubKey]'

Then, step through with:
btcdeb > step #continue till end


### 6. Restart bitcoind and Run the Third Script

Stop and restart bitcoind:

bitcoin-cli -regtest stop
bitcoind -regtest 

Then execute:
python p2sh.py

- Uses P2SH-SegWit transactions
- Sends transactions between new addresses (A', B', C')
- Mines blocks for confirmation

### 7. Debug the Third Script Transactions

To debug  the  transactions:
Use the command,
btcdeb '[] [scriptPubKey]'


Step through with:
btcdeb > step #continue till end


## Interpretation of Transactions

1. *Legacy Transaction(1st and 2nd scripts)*
   - Uses P2PKH (Pay-to-PubKey-Hash)
   - Requires scriptSig with a public key and signature
2. *SegWit Transactions (3rd Script)*
   - Uses P2SH-SegWit (Pay-to-Script-Hash with Segregated Witness)
   - Script execution differs, with witness data in separate fields

By following these steps, you can successfully execute and debug Bitcoin transactions in regtest mode.

## Sample Output Snippets
Legacy transaction from A to B
![Legacy_AtoB](Legacy.png)

Legacy transaction from B to C
![Legacy_BtoC](Legacy2.png)

Segwit transaction from A to B and B to C 
![Segwit](P2SH.png)

Legacy Debug for transaction A to B
![Legacy_Debug_AtoB](Legacydebug.png)

Legacy Debug for transaction B to C
![Legacy_Debug_BtoC](Legacy2debug.png)

Segwit Debug for transaction A to B and B to C
![Segwit_Debug](P2SHdebug.png)

