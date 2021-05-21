from .coin_methods import eggchain
from .script import call_chain
import schedule
schedule.every(10).minutes.do(call_chain)
"""while True:
  eggchain.mine()"""