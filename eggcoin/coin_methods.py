# day 1 - I'm going to bed now. Tomorrow I work on the mining function(done) and the checking of the blockchain (done) and the transactions.(done) Perhaps day after is when I'll get to the finding of unspent coins(done). checking of unspent coins must be done after mining a block, even if you have mined it. 
# day 2 - done most of all this, just need to now add a database for unspent coins of entire blockchain, owned coins, entire blockchain and JSON file for private and public key. I'll think over what I have just done and see if there are any errors.done with all this in day 2 only. Ok tomorrow is for testing... the worst part... ima run it.
#day 3 - I tested it. IT WORKS! I was half not expecting it to do anything. A few minor issues to sort out and it's working just fine! Happy time!
#day 4 i have to test it again... want to be 100% sure before moving to the next phase
# after many days of exams, I'm bacc. lets call this day 5. Added method for adding a recieved transaction
import requests
import time
import rsa
from rsa import PublicKey, PrivateKey
import random
import hashlib
import json
class Blockchain():
  def __init__(self):
    self.difficulty = 5
    self.read_personal_data()
    self.current_transactions = []
    self.nonce=0
    try:
      keys = self.read_keys()
      self.public_key = PublicKey(keys["public_key"][0],keys["public_key"][1])
      self.private_key = PrivateKey(keys["private_key"][0],keys["private_key"][1],keys["private_key"][2],keys["private_key"][3],keys["private_key"][4])
      self.coins = self.read_owned_coins()
      self.chain = self.read_blockchain()
      self.current_transactions = self.chain[-1]["transactions"]
      self.unspent_coins = self.read_unspent_coins()
      self.read_personal_data
    except:
      print("hey")
      self.chain = []
      self.chain.append({
          "index":1,
          "prev_hash":self.hash_txt("egg"),
          "nonce":None,
          "timestamp":time.time(),
          "transactions":[],
          "message":"hi guys, this is an academic project, just to learn about blockchains. Have fun with it!"
        })
      self.unspent_coins = []
      (self.public_key, self.private_key) = rsa.newkeys(1024)
      self.first_transaction_in_block()
      self.chain[-1]["transactions"] = self.current_transactions
      self.write_keys({
        "public_key":[self.public_key.n,self.public_key.e],
        "private_key":[self.private_key.n,self.private_key.e,self.private_key.d,self.private_key.p,self.private_key.q]
      })
      self.write_blockchain()
      self.coins = []
      self.write_owned_coins()
      self.write_unspent_coins()
      self.peers=[]
      self.personal_data={}
      self.read_peers()
    self.read_peers()
    self.ping_all_peers()
    self.write_owned_coins()
    self.write_unspent_coins()
    self.blockchain_checking()
  
  def mine(self):
    if self.chain[-1]["nonce"] == None:
      mined = False
      prev_hash = self.chain[-1]["prev_hash"]
      counter = random.randint(1,1*10^5)
      while mined == False:
        hash_made = self.hash_txt(prev_hash+str(counter))
        if hash_made[:self.difficulty] == self.generate_zero_string(self.difficulty):
          self.chain[-1]["nonce"] = counter
          self.new_block_mined()
          print("nonce found! mining successful!")
          return True
        counter +=1
        self.nonce=counter
        print("mine with nonce "+str(counter)+" unsuccessful")
    else:
      self.nonce=0
      self.new_block_mined()
    
      
  def new_block_mined(self):
    if self.chain[-1]["nonce"] != None:
      if self.check_single_block(self.chain[-1]):
        if self.current_transactions!=[]:
          self.chain[-1]['transactions'] = self.current_transactions
        self.current_transactions = []
        self.chain.append({
          "index":len(self.chain)+1,
          "prev_hash":self.calculate_transaction_hash(self.chain[-1]),
          "nonce":None,
          "timestamp":time.time(),
          "transactions":[]
        })
        self.first_transaction_in_block()
        #logic here for broadcasting the block around the network
        if not(self.broadcast_block_mined(self.chain[-1])):
          self.current_transactions=[]
          self.chain.pop(-1)
          self.chain[-1]["nonce"]=None
          self.unspent_coins=[]
          self.coins=[]
          self.log_all_blockchain_transactions(self.chain)
          self.write_blockchain()
          self.write_owned_coins()
          self.write_unspent_coins()
          return False
        else:
          self.write_blockchain()
          self.write_owned_coins()
          self.write_unspent_coins()
          return True
      else:
        self.unspent_coins=[]
        self.coins=[]
        self.log_all_blockchain_transactions(self.chain)
        self.write_blockchain()
        self.write_owned_coins()
        self.write_unspent_coins()
        return False


  def new_block_recieved(self,proof_recieved,transactions_recieved,time_stamp,transactions_gifted):
    self.chain[-1]["nonce"] = proof_recieved
    self.chain[-1]["transactions"] = transactions_recieved
    self.current_transactions = []
    check = self.check_single_block(self.chain[-1])
    if check:
      self.chain.append({
        "index":len(self.chain)+1,
        "prev_hash":self.calculate_transaction_hash(self.chain[-1]),
        "nonce":None,
        "timestamp":time_stamp,
        "transactions":transactions_gifted
      })
      self.write_blockchain()
      self.write_owned_coins()
      self.write_unspent_coins()
    else:
      return False
    return True


  def add_recieved_transaction(self, transaction):
    if self.check_singular_transaction(transaction):
      print("yes")
      self.current_transactions.append(transaction)
      self.chain[-1]["transaction"] = self.current_transactions
      self.write_blockchain()
      return True
    return False


  def new_transaction(self, amount,reciever_public_key):
    """#inputs have to be the outputs of the previous coins and the amount of money they want to spend
    #outputs have to be the hash of the public key of reciever and previous hash and the amount of the coin recieved and public key of each person its being sent to (this makes sure that the sender can send a fraction of their coin and still have the other fraction as an unspent output) and signature
    # each output must be added to the database of unspent coins and each input must be removed from the database. Before it is removed, it must be refered to as the total so that the new output can be generated.
    #inputs - {"hash","amount","signature","public key"}
    #someone fix this code and make it more efficient and less klunky"""
    self.read_owned_coins()
    self.read_unspent_coins()
    if (amount-int(amount)) == 0:
      reciever_public_key = self.pythonify_public_key(reciever_public_key)
      balance = 0
      coins_to_use = []
      last_index = 0
      outputs=[]
      for v,i in enumerate(self.coins):
        balance+=int(i["amount"])
        i["owner_public_key"] = self.jsonify_public_key(self.public_key)
        coins_to_use.append(i)
        if amount<=balance:
          last_index=v
          break
      full_balance=0
      for i in self.coins:
        full_balance+=int(i["amount"])
      if full_balance<amount:
        return False  #broke moment
      """
      if amount < balance:
        money_needed = balance-amount
        print(money_needed)
        #self.coins[last_index]["amount"] -= money_needed
        outputs.append(coins_to_use[-1])
        outputs[0]["amount"] = money_needed
        outputs[0]["owner_public_key"] = self.jsonify_public_key(self.public_key)
        outputs[0]["hash"] =self.hash_txt(str(coins_to_use[-1]["hash"])+str(self.public_key))
        outputs[0]["signature"] = str(self.signature_making(outputs[0]["hash"], self.private_key))
        #self.coins.pop(last_index)
      """
      for i in coins_to_use:
        outputs.append({
          "owner_public_key":self.jsonify_public_key(reciever_public_key),
          "amount":i["amount"],
          "hash":self.hash_txt(i["hash"]+str(reciever_public_key)),
          "signature": str(self.signature_making(self.hash_txt(i["hash"]+str(reciever_public_key)), self.private_key))
        })
      self.current_transactions.append({
        "inputs":coins_to_use,
        "outputs":outputs
      })
      self.chain[-1]["transactions"] = self.current_transactions
      self.write_blockchain()
      # the coins db and the unspent coins DB will be updated once the next block is mined
      """
      for i,v in enumerate(coins_to_use):
        self.coins.pop(i)
      """
      #broadcast the transmission
      self.broadcast_transaction(self.current_transactions[-1])
      return True
    print("we do not deal in decimal numbers")
    return False

  def recieved_transaction(self,transaction):
    #check if transaction syntax is correct
    if transaction.keys()>= {"inputs","outputs"}:
      for i in transaction["inputs"]:
        if not(i.keys()>={"owner_public_key","amount","hash","signature"}):
          return False
      for i in transaction["outputs"]:
        if not(i.keys()>={"owner_public_key","amount","hash","signature"}):
          return False
      return True


  def check_singular_transaction(self,transaction):
    for index, value in enumerate(transaction["inputs"]):
            if not(value in self.unspent_coins):
              return False
    if self.recieved_transaction(transaction) == True:
      return True
    return False


  def first_transaction_in_block(self):
    if len(self.current_transactions) == 0:
      inputs = []
      outputs = []
      for i in range(50):
        inputs.append({
          "owner_public_key":"egg",
          "amount":1,
          "hash":self.hash_txt("".join([str(len(self.chain)),str(1),str(i)])),
          "signature":"egg"
        })
        outputs.append({
          "owner_public_key":self.jsonify_public_key(self.public_key),
          "amount":1,
          "hash":self.hash_txt("".join([str(len(self.chain)),str(1),str(i),str(self.public_key)])),
          "signature":"egg"#rsa.encrypt(self.hash_txt(str(len(self.chain)+1)).encode('utf8'), self.private_key)
        })
      self.current_transactions.append({
        "inputs":inputs,
        "outputs":outputs
      })
      self.chain[-1]["transactions"] = self.current_transactions
      self.write_blockchain()
      """
      for i in outputs:
        self.coins.append(i)
      """
      self.broadcast_transaction(self.current_transactions[-1])
  @staticmethod
  def hash_txt(text):
    m = hashlib.sha256()
    m.update(text.encode("ascii"))
    return m.hexdigest()


  @staticmethod
  def signature_making(text,key):
    return rsa.encrypt(text.encode("utf8"), key)
  

  def broadcast_transaction(self,transaction):
    self.read_peers()
    for i in self.peers:
      try:
        requests.post(i+"/new_transaction",{"transaction":json.dumps(transaction)})
      except:
        print("peer "+i+" is offline or has an incorrect address")
    #play function. a dummy function until i set up the API
    print("Broadcasted transaction to all peers!")


  def broadcast_block_mined(self,block):
    self.read_peers()
    response=""
    false_tally=0
    true_tally=0
    for i in self.peers:
      if not(i == "http://"+self.personal_data['repl_name']+"."+self.personal_data['username']+".repl.co"):
        try:
          response = requests.post(i+"/new_block",{"block":json.dumps(block),"prevblock":json.dumps(self.chain[-2])}).text
          if response == "true":
            true_tally+=1
          elif response=="false":
            false_tally+=1
        except:
          print("peer "+i+" is offline or has an incorrect address")
    #play function. a dummy function until i set up the API
    print("Block broadcasted. Lets hope it gets accepted!")
    if (true_tally+false_tally) == 0:
      print("true")
      return True
    elif true_tally<false_tally:
      return False
    else:
      return True
  

  def calculate_transaction_hash(self,block):
    transactions = str(block["transactions"])
    return self.hash_txt(transactions)


  @staticmethod
  def generate_zero_string(num):
    string = ""
    for i in range(num):
      string+="0"
    return string
  
  def check_single_block(self,block):
    if (block["prev_hash"] == self.calculate_transaction_hash(self.chain[int(block["index"])-2])) or (block["index"] == 1):
      print('ye')
      if self.hash_txt(block["prev_hash"]+str(block["nonce"]))[:self.difficulty] != self.generate_zero_string(self.difficulty):
        return False
    else:
      return False
    self.log_transactions(block)
    return True


  #work on heavy check later... after release of v1
  def check_blocks_light(self,chain):
    for i,v in enumerate(chain):
      if (i>0) and (i<(int(chain[-1]['index'])-1)):
        if v["prev_hash"] == self.calculate_transaction_hash(chain[i-1]):
          if self.hash_txt(v["prev_hash"]+str(v["nonce"]))[:self.difficulty] != self.generate_zero_string(self.difficulty):
            return False
            break
        else:
          return False
          break
    return True
  
  # make this better on version 1 or whatever they call the nex one - 0.0.2??? LOL
  def check_transactions(self,block):
    try:
      for i,v in enumerate(block["transactions"]):
        if i>0:
          for index, value in enumerate(v["inputs"]):
            if not(value in self.unspent_coins):
              return False
      return True
    except:
      return False

  
  def log_transactions(self,block):
    #assume all transactions are checked
    self.read_unspent_coins()
    self.read_owned_coins()
    spent = []
    recieved = []
    for i in block["transactions"]:
      for v in i["inputs"]:
        spent.append(v)
      for v in i["outputs"]:
        recieved.append(v)
    to_remove = []
    for j,i in enumerate(self.unspent_coins):
      self.unspent_coins[j]["owner_public_key"] = self.jsonify_public_key(i["owner_public_key"])
      for v in spent:
        if i == v:
          to_remove.append(j)
    for i in to_remove:
      self.unspent_coins.pop(i)
    for i in recieved:
      self.unspent_coins.append(i)
    pub_key = self.jsonify_public_key(self.public_key)
    self.coins=[]
    for i in self.unspent_coins:
      if i["owner_public_key"] == pub_key:
        self.coins.append(i)
    self.write_unspent_coins()
    self.write_owned_coins()
  
  
  def log_all_blockchain_transactions(self,chain):
    for i in chain:
      self.log_transactions(i)
  

  def broadcast_non_accept_block(self):
    print("BLOCK IS WRONG. TRANSACTION IS FAILURE.")


  def write_blockchain(self):
    with open("blockchain.json", "w") as outfile:
      json.dump(self.chain, outfile)


  def write_keys(self,keys):
    with open("keys.json", "w") as outfile:
      json.dump(keys, outfile)
  

  def write_owned_coins(self):
    with open("owned_coins.json", "w") as outfile:
      json.dump(self.coins, outfile)
  

  def write_unspent_coins(self):
    with open("unspent_coins.json", "w") as outfile:
      json.dump(self.unspent_coins, outfile)
  

  def read_blockchain(self):
    with open("blockchain.json", "r") as outfile:
      return json.load(outfile)


  def read_keys(self):
    with open("keys.json", "r") as outfile:
      return json.load(outfile)
  

  def read_owned_coins(self):
    with open("owned_coins.json", "r") as outfile:
      return json.load(outfile)


  def read_unspent_coins(self):
    with open("unspent_coins.json", "r") as outfile:
      return json.load(outfile)


  def jsonify_public_key(self,key):
    try:
      return [key.n,key.e]
    except:
      return key
  

  def jsonify_private_key(self,key):
    try:
      return [key.n,key.e,key.d,key.p,key.q]
    except:
      return key
  

  def pythonify_public_key(self, key):
    try:
      return PublicKey(key[0],key[1])
    except:
      return key

  
  def pythonify_private_key(self,key):
    try:
      return PrivateKey(key[0],key[1],key[2],key[3],key[4])
    except:
      return key


  #peer argument is just peer ip address or url
  def write_new_peer(self,url):
    peer = url
    self.peers = []
    with open("peers.json", "r") as outfile:
        self.peers = json.load(outfile)
    for i in self.peers:
      if peer==i or not("http" in peer):
        return False
    self.peers.append(peer)
    with open("peers.json", "w") as outfile:
        json.dump(self.peers, outfile)
    return True


  def read_peers(self):
    self.peers = []
    with open("peers.json", "r") as outfile:
      self.peers = json.load(outfile)

  
  def read_personal_data(self):
    self.personal_data = {}
    with open("personal_data.json","r") as outfile:
      self.personal_data = json.load(outfile)
    self.write_new_peer("http://"+self.personal_data["repl_name"]+"."+self.personal_data["username"]+".repl.co")
    return True


  def blockchain_checking(self):
    try:
      self.read_peers()
      chains_obj = []
      for i in self.peers:
        if i != ("http://"+self.personal_data['repl_name']+"."+self.personal_data['username']+".repl.co"):
          try:
            foreign_chain = json.loads(requests.get(i+"/blockchain").text)
            if foreign_chain[-1]["index"]>self.chain[-1]["index"]:
              if self.check_blocks_light(foreign_chain):
                is_in = False
                for i in chains_obj:
                  if (i["chain"][-2] == foreign_chain[-2]) and (i["chain"][-1]["index"] == foreign_chain[-1]["index"]):
                    i["count"]+=1
                    is_in=True
                if is_in == False:
                  chains_obj.append({"chain":foreign_chain,"count":1})
          except:
            print("die lol")
      if len(chains_obj)>0:
        index=0
        highest=0
        for v,i in enumerate(chains_obj):
          if i["count"]>highest:
            index = v
            highest = i["count"]
        self.chain=chains_obj[index]['chain']
        self.write_blockchain()
        chains_obj={}
    except:
      print("die")

  def ping_all_peers(self):
    for i in self.peers:
      try:
        if i != ("http://"+self.personal_data['repl_name']+"."+self.personal_data["username"]+".repl.co"):
          peers = json.loads(requests.post(i+"/new_peer",{"repl_name":self.personal_data["repl_name"],"username":self.personal_data["username"]}).text)
          for v in peers:
            self.write_new_peer(v)
      except:
        print("lol2")

  def balance_everything(self,chain):
    unspent_coins=[]
    for v in chain:
      for b in v['transactions']:
        for m in b['inputs']:
          try:
            unspent_coins.remove(m)
          except:
            print("coin not found")
      for b in v['transactions']:
        for m in b['outputs']:
          unspent_coins.append(m)
    owned_coins = []
    pub_key = self.jsonify_public_key(self.public_key)
    for i in unspent_coins:
      if self.jsonify_public_key(i['owner_public_key']) == pub_key:
        owned_coins.append(i)
    return (owned_coins,unspent_coins)
      
eggchain = Blockchain()

#copyright generationxcode & graphegg 2021