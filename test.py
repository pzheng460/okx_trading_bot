import json
import logging
from typing import Optional
import okx.Trade as Trade
import okx.Funding as Funding
import okx.MarketData as MarketData
import okx.Account as Account
import okx.PublicData as PublicData

import pandas as pd
import time

# 配置日志
logging.basicConfig(
    filename="trading_bot.log",  # 日志文件名
    level=logging.INFO,  # 日志级别
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式
    filemode='w' # 'w'表示覆盖写入，'a'表示追加写入
)

# 读取 api_key_demo.json 文件
with open("./okx_market_maker/config/api_key_demo.json", "r") as file:
    api_keys = json.load(file)

# 提取 api_key、secret_key 和 passphrase
api_key = api_keys.get("api_key")
secret_key = api_keys.get("secret_key")
passphrase = api_keys.get("passphrase")

flag = "1"  # live trading: 0, demo trading: 1

marketDataAPI = MarketData.MarketAPI(flag=flag)

accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)

PublicDataAPI = PublicData.PublicAPI(flag=flag)

def get_latest_price(instId: str) -> float:
    """
    获取最新价格

    Args:
        inst_id (str): 合约代码
    
    Returns:
        float: 最新价格
    """
    result = marketDataAPI.get_ticker(instId=instId)
    if result['code'] == '0':
        price = float(result['data'][0]['last'])
        logging.info(f"获取最新价格成功: {instId} 最新价格为 {price}")
        return price
    else:
        logging.error(f"获取行情失败：{result}")
        return None

def moving_average_crossover(
    instId: str, 
    short_window: int = 5, 
    long_window: int = 20
) -> None:
    """
    简单移动平均线交叉策略
    
    Args:
        instId (str): 合约代码
        short_window (int): 短期移动平均线窗口
        long_window (int): 长期移动平均线窗口

    Returns:
        None
    """
    candles = marketDataAPI.get_candlesticks(instId=instId, bar='1m', limit=long_window)
    if candles['code'] != '0':
        logging.error(f"获取K线数据失败：{candles}")
        return

    df = pd.DataFrame(candles['data'], columns=['ts', 'open', 'high', 'low', 'close', 'vol', 'volCcy', 'volCcyQuote', 'confirm'])
    df['close'] = df['close'].astype(float)
    df = df.iloc[::-1]  # 反转数据，使最新的数据在最后

    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()

    # 判断是否产生交易信号
    if df['short_ma'].iloc[-2] < df['long_ma'].iloc[-2] and df['short_ma'].iloc[-1] > df['long_ma'].iloc[-1]:
        logging.info("产生买入信号")
        place_order(instId, 'buy', 'market', sz='0.001')
    elif df['short_ma'].iloc[-2] > df['long_ma'].iloc[-2] and df['short_ma'].iloc[-1] < df['long_ma'].iloc[-1]:
        logging.info("产生卖出信号")
        place_order(instId, 'sell', 'market', sz='0.001')
    else:
        logging.info("无交易信号")

def place_order(
    instId: str, 
    side: str, 
    ordType: str, 
    px: Optional[float] = None, 
    sz: str ='0.001'
) -> None:
    """
    下单函数
    
    Args:
        instId (str): 合约代码
        side (str): 交易方向，'buy' 或 'sell'
        ordType (str): 订单类型，'limit' 或 'market'
        px (float, optional): 价格，仅在 ordType 为 'limit' 时需要
        sz (str): 下单数量

    Returns:
        None
    """
    order = {
        'instId': instId,
        'tdMode': 'cash',
        'side': side,
        'ordType': ordType,
        'sz': sz
    }
    if ordType == 'limit' and px is not None:
        order['px'] = px

    result = Trade.place_order(**order)
    if result['code'] == '0':
        logging.info(f"下单成功，订单ID：{result['data'][0]['ordId']}")
    else:
        logging.error(f"下单失败：{result}")

def get_account_balance() -> None:
    """
    查看当前账号余额

    Returns:
        None
    """
    try:
        result = accountAPI.get_account_balance()
        if result['code'] == '0':
            balances = result['data'][0]['details']
            for balance in balances:
                currency = balance['ccy']
                available = balance['availBal']
                logging.info(f"币种: {currency}, 可用余额: {available}")
        else:
            logging.error(f"获取账户余额失败：{result}")
    except Exception as e:
        logging.error(f"获取账户余额时出错：{e}")

def run_bot() -> None:
    instId = 'BTC-USDT'
    while True:
        try:
            moving_average_crossover(instId)
            time.sleep(1)  # 每1s运行一次
        except Exception as e:
            logging.error(f"运行出错：{e}")
            time.sleep(1)

if __name__ == "__main__":
    # 运行交易机器人
    logging.info("交易机器人启动")
    get_account_balance()  # 查看账户余额
    run_bot()