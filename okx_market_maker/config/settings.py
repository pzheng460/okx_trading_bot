import os
import json

# 读取 api_key_demo.json 文件
with open(os.path.abspath(os.path.dirname(__file__) + "/api_key_demo.json"), "r") as file:
    api_keys = json.load(file)

# 提取 api_key、secret_key 和 passphrase
API_KEY = api_keys.get("api_key")
API_KEY_SECRET = api_keys.get("secret_key")
API_PASSPHRASE = api_keys.get("passphrase")

# trading flag
# 0: live trading, 1: demo trading
IS_DEMO_TRADING = True

# market-making instrument 市场做市产品
TRADING_INSTRUMENT_ID = "BTC-USDT-SWAP"
TRADING_MODE = "cross"  # "cash" / "isolated" / "cross"

# default latency tolerance level 默认延迟容忍级别
ORDER_BOOK_DELAYED_SEC = 60  # Warning if OrderBook not updated for these seconds, potential issues from wss connection
ACCOUNT_DELAYED_SEC = 60  # Warning if Account not updated for these seconds, potential issues from wss connection

# risk-free ccy 无风险计价货币
RISK_FREE_CCY_LIST = ["USDT", "USDC", "DAI"]

# params yaml path
PARAMS_PATH = os.path.abspath(os.path.dirname(__file__) + "/params.yaml")
