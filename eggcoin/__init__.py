from .coin_methods import eggchain
from .script import call_chain
import schedule
schedule.every(3).minutes.do(call_chain)
"""while True:
  eggchain.mine()"""