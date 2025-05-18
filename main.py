from okx_market_maker.strategy.SampleMM import SampleMM
import logging

# 配置日志
logging.basicConfig(
    filename="trading_bot.log",  # 日志文件名
    level=logging.INFO,  # 日志级别
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式
    filemode='w' # 'w'表示覆盖写入，'a'表示追加写入
)

if __name__ == "__main__":
    strategy = SampleMM()
    strategy.run()