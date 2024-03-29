# -*- coding: utf-8 -*-
import datetime 
import hashlib
import re
import ecdsa
import time
from random import randint
UTXO_DB={}
mempool=[]
last_block_hash=""
difficulty=1
block_chain={}
total_blocks=0
accepted_block_reward=50
block_no=0
mining=False
users_list={}

class user:
    def __init__(self):
        # SECP256k1 is the Bitcoin elliptic curve 
        self.priv_k = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) 
        self.pub_k=self.priv_k.get_verifying_key()
        m=hashlib.sha256(bytes(self.pub_k.to_string())) # Hashing the generated public key with SHA256
        self.pub_key_hash = m.hexdigest() # Storing the hashed public key
        self.priv_k_string=self.priv_k.to_string()
        self.pub_k_string=self.pub_k.to_string()
        # sig = sk.sign(b"message")
        # vk.verify(sig, b"message") # True

# coinbase=user()

# class txIn:
#     def __init__(self,sender_addr,details,val,pkScript,sigScript):
#         self.sender_addr=sender_addr
#         self.details=details
#         self.val=val
#         self.pkScript=pkScript
#         self.sigScript=sigScript
    
#     def display(self):
#         print("\nAddress :",self.sender_addr,"\nDetails :",self.details,"\nValue :",self.val)

class txOut:
    def __init__(self,receiver_addr,details,val,r_pkScript,s_pkScript,sigScript):
        self.receiver_addr=receiver_addr
        self.details=details
        self.val=val
        self.r_pkScript=r_pkScript
        self.s_pkScript=s_pkScript
        self.sigScript=sigScript
    
    def display(self):
        print("\nAddress :",self.receiver_addr,"\nDetails :",self.details,"\nValue :",self.val)
        

class unconfirmed_tx:
    def __init__(self,sender,receiver,amount,r_pkScript,sigScript): #tx hash? add timestamp
        self.sender=sender
        self.receiver=receiver
        self.amount=amount
        self.r_pkScript=r_pkScript
        self.sigScript=sigScript
        self.tx_hash=sigScript.sig
    
    def display(self):
        print("Sender : ",self.sender)
        print("Receiver : ",self.receiver)
        print("Amount : ",self.amount)

class valid_transaction: 

    def __init__(self,inputs,outputs,tx_hash):
        self.sender=inputs[0].receiver_addr #Sender Public Key
        self.receiver=outputs[0].receiver_addr #Reciever Public Key
        self.timestamp=datetime.datetime.now() 
        self.inputs=inputs
        self.outputs=outputs
        # self.tx_string=str(self.sender)+str(self.receiver)+str(inputs[0].val)+str(outputs[0].val)+str(self.timestamp)
        # m=hashlib.sha256(self.tx_string.encode())
        # self.tx_hash= str(m.hexdigest()) # Transaction Hash
        self.tx_hash=tx_hash
        mempool.append(self)
    
    def display(self):
        print("\nTransaction Hash :",self.tx_hash,"\nTimeStamp :",self.timestamp)
        print("\n Inputs :")
        for ip in self.inputs:
            print(ip.display())
        print("\n Outputs :")
        for op in self.outputs:
            op.display()
        print("------------------\n")



# class block:
#     def __init__(self,tx_list,miner_pub,nonce,block_hash,timestamp):
#         self.tx_list=tx_list
#         self.miner=miner_pub
#         self.block_hash=block_hash
#         self.nonce=nonce
#         self.timestamp=timestamp

    
class scriptPubKey:
    def __init__(self,pubk_hash):
        self.pubk_hash=pubk_hash

class scriptSig:
    def __init__(self,pub_key,sig):
        #print("Pub key :",pub_key)
        self.pub_key=pub_key
        self.sig=sig


    
def p2pkhScript(scriptPubKey,scriptSig,message):
    dup_pubKey=scriptSig.pub_key
    print("[DONE] DUP")
    m=hashlib.sha256(bytes(dup_pubKey.to_string()))
    print("[DONE] HASH256")
    dup_pubk_hash = m.hexdigest() 
    if dup_pubk_hash==scriptPubKey.pubk_hash:
        print("[DONE] EQUALVERIFY")
        CHECKSIG=scriptSig.pub_key.verify(scriptSig.sig,message,hashfunc=hashlib.sha256)
        if CHECKSIG==True:
            print("[DONE] CHECKSIG")
            return True
        else:
            print("CHECKSIG Failed")
            return False
    else:
        print("ORIGINAL :",scriptPubKey.pubk_hash)
        print("DUPKEY :",dup_pubk_hash)
        print("EQUALVERIFY Failed")
        return False

def tx_validation(unc_tx):
    print("[BEGIN] Transaction Validation")
    amt=unc_tx.amount
    sender_pkh=unc_tx.sender
    receiver_pkh=unc_tx.receiver
    r_pkScript=unc_tx.r_pkScript
    sigScript=unc_tx.sigScript
    data=bytes(sender_pkh+receiver_pkh+str(amt),encoding="utf-8")
    inputs=[]
    in_sum=0
    #print(sender_pkh)
    if sender_pkh in UTXO_DB:
        for tx in UTXO_DB[sender_pkh]:
            #print("Here",tx.val)
            if in_sum<=amt:
                 inputs.append(tx) # Write code to remove from UTXO once valid
                 in_sum+=tx.val
    if in_sum<amt:
        print("[INVALID] Insufficient Balance ", in_sum, " Required : ",amt)
        return False # Insufficient Balence, Invalid Transaction
    outputs=[txOut(receiver_pkh,"Unspent",amt,r_pkScript,scriptPubKey(sender_pkh),sigScript)]
    if in_sum>amt:
        outputs.append(txOut(sender_pkh,"Unspent",in_sum-amt,scriptPubKey(sender_pkh),scriptPubKey(sender_pkh),sigScript)) # change
    #utxo_bin=[]
    for i in range(len(inputs)):
        ip=inputs[i]
        #print("\n------------------\nSender :",sender_pkh,"\nReceiver :",receiver_pkh)
        
        val=p2pkhScript(ip.r_pkScript,sigScript,data)
        if val==False:
            # for tb in utxo_bin:
            #     UTXO_DB[tb.sender_addr].append(tb)
            print("[INVALID] P2PKH Script verifiction failed")
            return False 
            
        inputs[i].details="Output"
        # UTXO_DB[ip.receiver_addr].remove(ip) 
        # utxo_bin.append(ip)
    # for tx in outputs:
    #     UTXO_DB[tx.receiver_addr].append(tx)
    m=hashlib.sha256(data)
    valid_transaction(inputs,outputs,m.hexdigest())
    print("[VALID] Added to Mempool")
    return True


def coinbase_transaction(receiver):
    pks=scriptPubKey(receiver)
    ti=txOut("COINBASE","output",accepted_block_reward,0,0,"")
    to=txOut(receiver,"Unspent",accepted_block_reward,pks,"","")
    m=hashlib.sha256(bytes("COINBASE"+receiver+str(datetime.datetime.now()),encoding='utf-8'))
    tx=valid_transaction([ti],[to],m.hexdigest())
    
    return tx
    

class block:
    def __init__(self,miner,prev_hash,block_hash,transactions,nonce,timestamp):
        global total_blocks
        self.difficulty=difficulty
        self.block_no=total_blocks
        total_blocks+=1
        self.no_of_transactions=len(transactions)+1
        self.timestamp=timestamp
        self.miner=miner
        # self.hash_string=str(self.no_of_transactions)+self.miner+str(self.timestamp)+str(nonce)
        self.block_hash=block_hash
        self.prev_hash=prev_hash
        self.next_hash=-1
        self.nonce=nonce
        self.block_reward=accepted_block_reward
        self.transactions=transactions
    
    def display(self):
        print("\n------------------------\nBlock No : ",self.block_no)
        print("Hash : ",self.block_hash)
        print("Prev Block Hash :",self.prev_hash)
        print("Difficulty : ",self.difficulty)
        print("Miner : ",self.miner)
        print("Nonce : ",self.nonce)
        print("Block Reward :",self.block_reward)
        print("Transactions : \n")
        for tx in self.transactions:
            tx.display()

def create_userslist():
    print("Executing")
    users_list={
        "1": user(),
        "2":user(),
        "3":user(),
        "4":user(),
        "5":user(),
        "6":user()
    }
    for usr in users_list:
        val=coinbase_transaction(users_list[usr].pub_key_hash)
    return users_list

def random_transactions(users_list):
    sender=users_list[str(randint(1,5))]
    receiver=users_list[str(randint(1,5))]
    #print("Sender : ",sender.pub_k,"\nReceiver :",receiver.pub_key_hash)
    amt= randint(1,accepted_block_reward)
    data=bytes(sender.pub_key_hash+receiver.pub_key_hash+str(amt),encoding="utf-8")
    signed_hash=sender.priv_k.sign(data,hashfunc=hashlib.sha256) #Signed hash
    s_sigScript=scriptSig(sender.pub_k,signed_hash)
    r_pks=scriptPubKey(receiver.pub_key_hash)
    unc_tx=unconfirmed_tx(sender.pub_key_hash,receiver.pub_key_hash,amt,r_pks,s_sigScript)
    res=tx_validation(unc_tx)
    if res==False:
        print("invalid transaction")
        unc_tx.display()
    else:
        print("Generated Valid Transaction : \n")
        mempool[-1].display()

def gen_transaction(sender,receiver_pkh,amt):
    data=bytes(sender.pub_key_hash+receiver_pkh+str(amt),encoding="utf-8")
    signed_hash=sender.priv_k.sign(data,hashfunc=hashlib.sha256) #Signed hash
    s_sigScript=scriptSig(sender.pub_k,signed_hash)
    r_pks=scriptPubKey(receiver_pkh)
    unc_tx=unconfirmed_tx(sender.pub_key_hash,receiver_pkh,amt,r_pks,s_sigScript)
    res=tx_validation(unc_tx)
    if res==False:
        print("invalid transaction")
        unc_tx.display()
    else:
        print("Generated Valid Transaction : \n")
        mempool[-1].display()

def mine():
    global last_block_hash, users_list
    print("Mining")
    miner=users_list[str(randint(1,5))]
    tx_list=[coinbase_transaction(miner.pub_key_hash)]
    mempool.remove(tx_list[0])
    no_tx= randint(0,len(mempool)//2+1) #no of transactions the block will have
    if len(mempool)==0:
        return "No Transactions in Mempool"
    for i in range(no_tx):
        tx = mempool[0]
        tx_list.append(tx)
        
        for ip in tx.inputs:
            if ip.receiver_addr!="COINBASE":
                UTXO_DB[ip.receiver_addr].remove(ip) 
        for op in tx.outputs:
            if op.receiver_addr in UTXO_DB:
                UTXO_DB[op.receiver_addr].append(op)
            else:
                UTXO_DB[op.receiver_addr]=[op]
            
        mempool.remove(tx)
        
    finding=True
    nonce=0
    block_data=miner.pub_key_hash+str(no_tx)
    start=time.time()
    timestamp=-1
    block_hash=""
    while finding:
        timestamp=datetime.datetime.now()
        data=block_data+str(difficulty)+str(block_no)+str(nonce)+str(timestamp)+last_block_hash
        m=hashlib.sha256(bytes(data,encoding='utf-8'))
        block_hash=str(m.hexdigest())
        
        if block_hash[:difficulty]=='0'*difficulty:
            end=time.time()
            print("Time Taken : ",end-start)
            finding=False
        nonce+=1
    gb=block(miner=miner.pub_key_hash,transactions=tx_list,nonce=nonce,block_hash=block_hash,prev_hash=last_block_hash,timestamp=timestamp)
    block_chain[gb.block_hash]=gb
    last_block_hash=gb.block_hash
    print("[SUCCESS] Block Placed Successfully")

def mine_script():
    while len(mempool)>0:
        mine()
    return "Mining Ended"

def gen_cred():
    return users_list["6"]

def view_blockchain():
    for blk_hash in block_chain:
        block_chain[blk_hash].display()

def view_utxo():
    print("UTXO DB")
    for addr in UTXO_DB:
        print("\n------------------\n")
        print("UTXO's for ",addr,":")
        for utxo in UTXO_DB[addr]:
            utxo.display()

def view_mempool():
    print("\n-------------------Mempool---------------------\n")
    for tx in mempool:
        print("-----------------------------")
        tx.display()
        print("\n")

if __name__=="__main__":
    users_list=create_userslist()
    while True : 
        c=input("1. Generate Transactions\n2. View Mempool\n3. View UTXO DB\n4. Mine\n5.View Blockchain\n")
        if c=='1':
            #gen_transaction(users_list)
            random_transactions()
            # tIn=txIn(sender.pub_key_hash,"Output",in_amt,)
            # tx=transaction(sender.pub_k,reciever.pub_k,in_amt,sign_in,out_amt,sign_op)
            
        elif c=='2':
            view_mempool()

        elif c=='3':
            view_utxo()
        elif c=='4':
            mine()

        elif c=='5':
            view_blockchain()
        else:
            break






























