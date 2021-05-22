from django.shortcuts import render
from django.http import HttpResponse
from.coin_methods import *
from django.shortcuts import  render,redirect

"""
syntax for post for adding new peer - 
{"repl_name":"name","username","username"}


syntax for post for adding new transaction - 
{"transaction":{#transaction}}

syntax for post for making a new transaction - 
{"amount":#amount,"reciever_public_keyp1":#public key,"reciever_public_keyp2"}
"""

def index(request):
  return HttpResponse("hey there")


def transaction_form(request):
  return render(request,"transaction_form.html")


def make_transaction(request):
  amount = request.POST['amount']
  reciever_public_keyp1 = request.POST['receiver_public_keyp1']
  reciever_public_keyp2 = request.POST['receiver_public_keyp2']
  transaction = eggchain.new_transaction(int(amount),[int(reciever_public_keyp1),int(reciever_public_keyp2)])
  if transaction:
    return redirect(request,'index')
  else:
    return HttpResponse("your transaction is invalid, go back to the <a href='../'>home page</a>")


def new_peer(request):
  eggchain.write_new_peer(request.POST['repl_name']+"."+request.POST['username']+".repl.co")
  json_data = ""
  with open("peers.json","r") as outfile:
    json_data=outfile
  return HttpResponse(json_data)


def new_transaction(request):
  transaction_recieved = eggchain.recieved_transaction(request.POST["transaction"])
  response = ""
  if transaction_recieved == True:
    response="true"
  else:
    response="false"
  return HttpResponse(response)


def new_block(request):
  block = eggchain.check_single_block(request.POST['block'])
  if block == True:
    return HttpResponse("true")
  else:
    return HttpResponse("false")


def blockchain_response(request):
  chain = eggchain.chain
  return HttpResponse(json.dumps(chain))


def mine(request):
  eggchain.mine()
  return HttpResponse("mining")

#copyright generationxcode & graphegg 2021
