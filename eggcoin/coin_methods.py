# day 1 - I'm going to bed now. Tomorrow I work on the mining function(done) and the checking of the blockchain (done) and the transactions.(done) Perhaps day after is when I'll get to the finding of unspent coins(done). checking of unspent coins must be done after mining a block, even if you have mined it. 
# day 2 - done most of all this, just need to now add a database for unspent coins of entire blockchain, owned coins, entire blockchain and JSON file for private and public key. I'll think over what I have just done and see if there are any errors.done with all this in day 2 only. Ok tomorrow is for testing... the worst part... ima run it.
#day 3 - I tested it. IT WORKS! I was half not expecting it to do anything. A few minor issues to sort out and it's working just fine! Happy time!
#day 4 i have to test it again... want to be 100% sure before moving to the next phase
# after many days of exams, I'm bacc. lets call this day 5. Added method for adding a recieved transaction
import requests
import traceback
import time
import rsa
from rsa import PublicKey, PrivateKey
import random
import hashlib
import json
from .models import *
from django.utils import timezone
class Blockchain():

  def __init__(self):
    self.blocked_peers = []
    self.synchronizing = False
    self.write_new_peer("http://Eggcoin.generationxcode.repl.co")
    self.escape = False
    self.mine_stat = False
    self.difficulty = 4
    self.read_personal_data()
    self.current_transactions = []
    self.nonce=0
    my_key = 141638327098651051980236429566531385139887513213877681331588249666693161925951061679621171978404467963828545972024841729403600006316066852371527668330175115063986907527750636637196595355563540447655703193861061836141036750095102975578100977696695297067762021117228189080021077654700047788128382635627673436583
    keys = self.read_keys()
    self.public_key = PublicKey(keys["public_key"][0],keys["public_key"][1])
    self.private_key = PrivateKey(keys["private_key"][0],keys["private_key"][1],keys["private_key"][2],keys["private_key"][3],keys["private_key"][4])
    if (Block_chain.objects.all().count()>0) and (((int(keys['public_key'][0]) == my_key) and (self.personal_data['username'] == "generationxcode") and (self.personal_data['repl_name']=="Eggcoin")) or ((int(keys['public_key'][0]) != my_key))):
      keys = self.read_keys()
      self.public_key = PublicKey(keys["public_key"][0],keys["public_key"][1])
      self.private_key = PrivateKey(keys["private_key"][0],keys["private_key"][1],keys["private_key"][2],keys["private_key"][3],keys["private_key"][4])
      self.current_transactions = self.read_from_blockchain_latest()["transactions"]
      self.unspent_coins = self.read_unspent_coins()
      self.blockchain_checking()
    else:
      self.chain = []
      print("hey")
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
      print("keys synthesized")
      self.current_transactions = self.first_transaction_in_block(self.chain[-1])
      print("transaction made")
      self.write_keys({
        "public_key":[self.public_key.n,self.public_key.e],
        "private_key":[self.private_key.n,self.private_key.e,self.private_key.d,self.private_key.p,self.private_key.q]
      })
      print("keys written")
      self.chain[-1]['transactions'] = self.current_transactions
      self.log_transactions({
          "index":1,
          "prev_hash":self.hash_txt("egg"),
          "nonce":None,
          "transactions":self.current_transactions,
          "message":"hi guys, this is an academic project, just to learn about blockchains. Have fun with it!"
        })
      print("transactions logged")
      self.write_to_blockchain(self.chain[-1])
      print("blockchain logged")
      self.peers=[]
      self.personal_data={}
      self.read_peers()
    self.read_peers()
    self.ping_all_peers()
    self.blockchain_checking()


  def mine(self):
    if self.read_from_blockchain_latest()['nonce'] == "None":
      mined = False
      prev_hash = self.read_from_blockchain_latest()['prev_hash']
      counter = random.randint(1,1*10^5)
      while mined == False:
        self.mine_stat = True
        if self.escape == False:
          hash_made = self.hash_txt(prev_hash+str(counter))
          if hash_made[:self.difficulty] == self.generate_zero_string(self.difficulty):
            block_to_write = self.read_from_blockchain_latest()
            block_to_write['nonce'] = counter
            if self.current_transactions !=[]:
              block_to_write['transactions'] = self.current_transactions
            self.write_to_blockchain_index(block_to_write,block_to_write['index'])
            self.new_block_mined()
            print("nonce found! mining successful!")
            return True
          counter +=1
          self.nonce=counter
          print("mine with nonce "+str(counter)+" unsuccessful")
        else:
          self.mine_stat=False
          self.escape = False
          break
    else:
      self.mine_stat =False
      self.nonce=0
      print("yo")
      self.new_block_mined()
    
      
  def new_block_mined(self):
    if Block_chain.objects.latest('pub_date').nonce != "None":
      latest_block = Block_chain.objects.latest('pub_date')
      print('here')
      if self.check_single_block(self.read_from_blockchain_latest()):
        print('passed')
        self.current_transactions = self.first_transaction_in_block(self.read_from_blockchain_latest())
        blocc = {"index":int(latest_block.index)+1, "prev_hash":self.hash_txt(json.dumps(self.read_from_blockchain_latest())),"timestamp":time.time(),"transactions":self.current_transactions,"nonce":"None"}
        #logic here for broadcasting the block around the network
        if not(self.broadcast_block_mined(blocc)):
          print('no')
          self.current_transactions = self.current_transactions[0]
          self.mine_stat = False
          return False
        else:
          print('ye')
          self.log_transactions(self.read_from_blockchain_latest())
          self.write_to_blockchain(blocc)
          self.mine_stat = False
          return True
      else:
        self.unspent_coins=[]
        self.coins=[]
        return False


  def new_block_recieved(self,prev_blocck,new_blocck):
    self.chain = [prev_blocck]
    self.current_transactions = new_blocck['transactions']
    check = self.check_single_block(self.chain[-1])
    if check:
      self.write_to_blockchain_index(self.chain[-1],self.chain[-1]['index'])
      self.write_to_blockchain(new_blocck)
      self.blockchain_checking()
      #self.log_transactions(block)
      self.mine_stat = False
    else:
      return False
    return True


  def add_recieved_transaction(self, transaction):
    if self.check_singular_transaction(transaction):
      print("yes")
      self.current_transactions = [self.current_transactions]
      self.current_transactions.append(transaction)
      self.chain = [self.read_from_blockchain_latest()]
      self.chain[-1]["transaction"] = self.current_transactions
      self.write_blockchain()
      return True
    return False


  def new_transaction(self, amount,reciever_public_key):
    """* inputs have to be the outputs of the previous coins and the amount of money they want to spend
    * outputs have to be the hash of the public key of reciever and previous hash and the amount of the coin recieved and public key of each person its being sent to (this makes sure that the sender can send a fraction of their coin and still have the other fraction as an unspent output) and signature
    * each output must be added to the database of unspent coins and each input must be removed from the database. Before it is removed, it must be refered to as the total so that the new output can be generated.
    ` inputs - {"hash","amount","signature","public key"}`
    * someone fix this code and make it more efficient and les klunky"""
    if (amount-int(amount)) == 0:
      keys = self.read_keys()['public_key'][0]
      reciever_public_key = self.pythonify_public_key(reciever_public_key)
      balance = 0
      coins_to_use = []
      last_index = 0
      outputs=[]
      self.coins = self.read_from_owned_coins()
      for v,i in enumerate(self.coins):
        balance+=int(i["amount"])
        i["owner_public_key"] = self.jsonify_public_key(self.public_key)
        i['hash'] = str(i['hash'])
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
      print(str(reciever_public_key))
      print(self.hash_txt((str(i["hash"])+str(keys))))
      for i in coins_to_use:
        outputs.append({
          "owner_public_key":self.jsonify_public_key(reciever_public_key),
          "amount":i["amount"],
          "hash":str(self.hash_txt((str(i["hash"])+str(keys)))),
          "signature": str(self.signature_making(str(i["hash"]), self.private_key))
        })
      self.current_transactions.append({
        "inputs":coins_to_use,
        "outputs":outputs
      })
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
            if self.read_from_unspent_coins(value['hash']):
              return False
    if self.recieved_transaction(transaction) == True:
      return True
    return False


  def first_transaction_in_block(self,block):
      inputs = []
      outputs = []
      for i in range(50):
        inputs.append({
          "owner_public_key":"egg",
          "amount":1,
          "hash":str(self.hash_txt("".join([str(Block_chain.objects.all().count()),str(1),str(i)]))),
          "signature":"egg"
        })
        outputs.append({
          "owner_public_key":self.jsonify_public_key(self.public_key),
          "amount":1,
          "hash":str(self.hash_txt("".join([str(Block_chain.objects.all().count()),str(1),str(i),str(self.public_key)]))),
          "signature":"egg"#rsa.encrypt(self.hash_txt(str(len(self.chain)+1)).encode('utf8'), self.private_key)
        })
      return [{"inputs":inputs,"outputs":outputs}]

      """
      for i in outputs:
        self.coins.append(i)
      """

  def hash_txt(self,text):
    m = hashlib.sha256()
    m.update(text.encode("ascii"))
    return m.hexdigest()


  @staticmethod
  def signature_making(text,key):
    data =  rsa.encrypt(text.encode("utf8"), key)
    output = 0    
    size = len(data)
    for index in range(size):
        output |= data[index] << (8 * (size - 1 - index))
    return str(output)
  

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
          prev_block = self.read_from_blockchain_latest()
          response = requests.post(i+"/new_block",{"block":json.dumps(block),"prevblock":json.dumps(prev_block)}).text
          if response == "true":
            true_tally+=1
            print(i+" support me")
          elif response=="false":
            false_tally+=1
            print(i+" dont support me :(")
        except:
          traceback.print_exc()
          print("peer "+i+" is offline or has an incorrect address")
    #play function. a dummy function until i set up the API
    print("Block broadcasted. Lets hope it gets accepted!")
    print(true_tally)
    print(false_tally)
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
    print(self.difficulty)
    print(self.hash_txt(block["prev_hash"]+str(block["nonce"])))
    if self.hash_txt(block["prev_hash"]+str(block["nonce"]))[:self.difficulty] != self.generate_zero_string(self.difficulty):
      print("chain is fed u[p")
      return False
    return True


  #work on heavy check later... after release of v1
  # no longer required. Here as a showcase of my idiocy.
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
  
  # make this better on version 1 or whatever they call the nex one - 0.0.2??? LOL. v2 speaking -> nope. not being used
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
    pub_key = self.jsonify_public_key(self.public_key)
    try:
      block['transactions'] = json.loads(block['transactions'])
    except:
      block['transactions']=block['transactions']
    try:
      try:
        for i in block['transactions']:
          for v in i["inputs"]:
            try:
              self.remove_from_unspent_coins(v['hash'])
              if self.jsonify_public_key(v['owner_public_key']) == pub_key:
                self.remove_from_owned_coins(v['hash'])
            except:
              pass
          for v in i["outputs"]:
              self.write_to_unspent_coins(v)
              if (self.jsonify_public_key(v['owner_public_key']) == pub_key) and not(self.read_from_owned_coins_check(v['hash'])):
                self.write_to_owned_coins(v)
      except:
        for v in block['transactions']["inputs"]:
          try:
            self.remove_from_unspent_coins(v['hash'])
            if self.jsonify_public_key(v['owner_public_key']) == pub_key:
              self.remove_from_owned_coins(v['hash'])
          except:
            print('coin not found. Do not worry.')
        for v in block['transactions']["outputs"]:
          self.write_to_unspent_coins(v)
          if (self.jsonify_public_key(v['owner_public_key']) == pub_key) and not(self.read_from_owned_coins_check(v['hash'])):
            self.write_to_owned_coins(v)
    except:
      traceback.print_exc()
      print("error lollol")
  
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
      if self.read_from_blockchain_latest()['nonce'] != "None":
        self.current_transactions = self.first_transaction_in_block(self.read_from_blockchain_latest())
        blocc = {"index":int(self.read_from_blockchain_latest()['index'])+1, "prev_hash":self.hash_txt(json.dumps(self.read_from_blockchain_latest())),"timestamp":time.time(),"transactions":self.current_transactions,"nonce":"None"}
        self.write_to_blockchain(blocc)
        print("completed correcting blockchain latest block to allow user to mine")
      self.read_peers()
      chains_obj = []
      highest = int(self.read_from_blockchain_latest()['index'])
      peer = None
      for i in self.peers:
        if (i != ("http://"+self.personal_data['repl_name']+"."+self.personal_data['username']+".repl.co")) and not(i in self.blocked_peers):
          try:
            foreign_chain_len = int(requests.get(i+"/chain_length").text)
            if foreign_chain_len > highest:
              highest = foreign_chain_len
              peer = i
              is_in = False
          except:
            if i != "http://Eggcoin.generationxcode.repl.co":
              self.peers.remove(i)
              print("(die lol)The address "+i+" is wrong or offline. It has been removed from peers.")
      if highest == int(self.read_from_blockchain_latest()['index']):
        return True
      print(highest)
      print(self.read_from_blockchain_latest()['index'])
      if peer !=  None:
        try:
          if Block_chain.objects.all().count() > 0 :
            last_block_own = self.read_from_blockchain(int(self.read_from_blockchain_latest()['index'])-1)
            block = json.loads(requests.post(peer+"/block_num",{"index":last_block_own['index']}).text)

            if int(last_block_own['nonce']) == block['nonce']:
              for i in range(int(last_block_own['index'])+1,highest+1):
                self.synchronizing = True
                try:
                  block = json.loads(requests.post(peer+"/block_num",{"index":i}).text)
                  if self.check_single_block(block):
                    self.log_transactions(block)
                    self.write_to_blockchain(block)
                  else:
                    self.blocked_peers.append(peer)
                    return False
                  print("> block number "+str(i)+ " synchronised out of "+str(highest)+" number of blocks.")
                except:
                  print("Error, blockchain is corrupted, this is alright")
          else:
            Block_chain.objects.all().delete()
            owned_coins.objects.all().delete()
            unspent_coins.objects.all().delete()
            print("blockchain deleted, new blockchain synchronising")
            for i in range(1,highest+1):
              try:
                block = json.loads(requests.post(peer+"/block_num",{"index":i}).text)
                self.log_transactions(block)
                self.write_to_blockchain(block)
                print("> block number "+str(i)+ " synchronised out of "+str(highest)+" number of blocks.")
              except:
                print("Error, blockchain is corrupted, please stop and restart the repl or let it continue. Contact generationxcode about this error if it persists.")
        except:
          Block_chain.objects.all().delete()
          owned_coins.objects.all().delete()
          unspent_coins.objects.all().delete()
          print("blockchain deleted, new blockchain synchronising")
          for i in range(1,highest+1):
            try:
              block = json.loads(requests.post(peer+"/block_num",{"index":i}).text)
              self.log_transactions(block)
              self.write_to_blockchain(block)
              print("> block number "+str(i)+ " synchronised out of "+str(highest)+" number of blocks.")
            except:
              traceback.print_exc()
              print("Error, blockchain is corrupted, please stop and restart the repl or let it continue. Contact generationxcode about this error if it persists.")
      highest = Block_chain.objects.all().count()
      blockchain_count = Block_chain.objects.all().count()
      # sorry my CS teacher... I have failed you... I must now use recursion...
      for i in self.peers:
        if i != ("http://"+self.personal_data['repl_name']+"."+self.personal_data['username']+".repl.co"):
          try:
            foreign_chain_len = int(requests.get(i+"/chain_length").text)
            if self.read_from_blockchain_latest()['index'] > highest:
              print(highest)
              print(foreign_chain_len)
              self.blockchain_checking()
            else:
              self.synchronizing = False
          except:
            if i != "http://Eggcoin.generationxcode.repl.co":
              self.peers.remove(i)
              self.synchronizing = False
              pass
      
          
    except:
      traceback.print_exc()
      self.synchronizing = False
      print("die")


  def ping_all_peers(self):
    for i in self.peers:
      try:
        if i != ("http://"+self.personal_data['repl_name']+"."+self.personal_data["username"]+".repl.co"):
          peers = json.loads(requests.post(i+"/new_peer",{"repl_name":self.personal_data["repl_name"],"username":self.personal_data["username"]}).text)
          for v in peers:
            self.write_new_peer(v)
      except:
        if i !="http://Eggcoin.generationxcode.repl.co":
          self.peers.remove(i)
          with open("peers.json", "w") as outfile:
            json.dump(self.peers, outfile)
          pass

  # not going to use this - just a showcase of how stupid I am
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


  def read_from_blockchain_latest(self):
    block = Block_chain.objects.latest('pub_date')
    return {'transactions':json.loads(block.transactions),'index':block.index,'timestamp':float(block.timestamp),'prev_hash':block.previous_hash,'nonce':block.nonce}


  def read_from_blockchain(self,index):
    block = Block_chain.objects.get(index=str(index))
    return {'transactions':json.loads(block.transactions),'index':index,'timestamp':float(block.timestamp),'prev_hash':block.previous_hash,'nonce':block.nonce}


  def write_to_blockchain(self, block):
    try:
      if Block_chain.objects.get(index=str(block['index'])):
        Block_chain(index=str(block['index']),timestamp=str(block['timestamp']),previous_hash=block['prev_hash'],nonce=str(block['nonce']),transactions=json.dumps(block['transactions']),pub_date=timezone.now()).save()
        print("more than index :)")
      else:
        Block_chain(index=str(block['index']),timestamp=str(block['timestamp']),previous_hash=block['prev_hash'],nonce=str(block['nonce']),transactions=json.dumps(block['transactions']),pub_date=timezone.now()).save()
        print("done")
      return True
    except:
      Block_chain(index=str(block['index']),timestamp=str(block['timestamp']),previous_hash=block['prev_hash'],nonce=str(block['nonce']),transactions=json.dumps(block['transactions']),pub_date=timezone.now()).save()
      print("done")
      return False

  def write_to_blockchain_index(self,block,index):
    block_write = Block_chain.objects.get(index=str(index))
    block_write.timestamp=str(block['timestamp'])
    block_write.previous_hash=block['prev_hash']
    block_write.nonce=str(block['nonce'])
    block_write.transactions=json.dumps(block['transactions'])
    block_write.pub_date=timezone.now()
    block_write.save()
    return True


  def read_from_unspent_coins(self,hash):
    try:
      coin = unspent_coins.objects.get(hash=str(hash))
      if coin:
        return True
      return False
    except:
      return False


  def write_to_unspent_coins(self, block):
    unspent_coins(owner_public_key_p1=block['owner_public_key'][0],owner_public_key_p2=block['owner_public_key'][1],hash=block['hash'],amount=str(1),signature=block['signature'],pub_date=timezone.now()).save()
    return True


  def remove_from_unspent_coins(self, hash):
    unspent_coins.objects.get(hash=hash).remove()
    return True


  def read_from_owned_coins(self):
    coin = owned_coins.objects.all()
    coin_array = []
    for i in coin:
      coin_array.append({'owner_public_key':[int(i.owner_public_key_p1),int(i.owner_public_key_p2)],'hash':hash,'amount':1,'signature':i.signature})
    return coin_array


  def write_to_owned_coins(self, block):
    owned_coins(owner_public_key_p1=block['owner_public_key'][0],owner_public_key_p2=block['owner_public_key'][1],hash=block['hash'],amount=str(1),signature=block['signature'],pub_date=timezone.now()).save()
    return True


  def remove_from_owned_coins(self, hash):
    owned_coins.objects.get(hash=hash).remove()
    return True


  def read_from_owned_coins_check(self,hash):
    try:
      coin = owned_coins.objects.get(hash=str(hash))
      if coin:
        return True
      return False
    except:
      return False

eggchain = Blockchain()

#copyright generationxcode & graphegg 2021