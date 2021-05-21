import threading
from eggcoin.coin_methods import eggchain

def set_interval(func,time):
    e = threading.Event()
    while not e.wait(time):
        func()


#function that calls blockchain_checking every 1 minute
def call_chain():
  eggchain.blockchain_checking()

