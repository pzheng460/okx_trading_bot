import logging
import threading
import time
import traceback

from okx.exceptions import OkxAPIException, OkxParamsException, OkxRequestException
from okx.MarketData import MarketAPI
from okx.PublicData import PublicAPI
from okx_market_maker.market_data_service.model.MarkPx import MarkPxCache
from okx_market_maker.config.settings import IS_DEMO_TRADING
from okx_market_maker import tickers_container, mark_px_container
from okx_market_maker.market_data_service.model.Tickers import Tickers
from okx_market_maker.utils.OkxEnum import InstType

logger = logging.getLogger(__name__)

class RESTMarketDataService(threading.Thread):
    def __init__(
        self, 
        is_demo_trading: bool = IS_DEMO_TRADING
    ) -> None:
        """
        这个类用于封装REST市场数据服务的相关函数。

        Args:
            is_demo_trading (bool): 是否为模拟交易
        """
        super().__init__()
        # 创建API服务实例
        self.market_api = MarketAPI(flag='0' if not is_demo_trading else '1', debug=False)
        self.public_api = PublicAPI(flag='0' if not is_demo_trading else '1', debug=False)
        # 初始化交易对容器，
        if not tickers_container:
            tickers_container.append(Tickers())
        # 初始化标记价格缓存
        if not mark_px_container:
            mark_px_container.append(MarkPxCache())

    def run(self) -> None:
        """
        运行REST市场数据服务，获取市场数据并更新数据容器。
        """
        while 1:
            try:
                json_response = self.market_api.get_tickers(instType=InstType.SPOT.value)
                tickers: Tickers = tickers_container[0]
                tickers.update_from_json(json_response)
                mark_px_cache: MarkPxCache = mark_px_container[0]
                json_response = self.public_api.get_mark_price(instType=InstType.MARGIN.value)
                mark_px_cache.update_from_json(json_response)
                json_response = self.public_api.get_mark_price(instType=InstType.SWAP.value)
                mark_px_cache.update_from_json(json_response)
                json_response = self.public_api.get_mark_price(instType=InstType.FUTURES.value)
                mark_px_cache.update_from_json(json_response)
                json_response = self.public_api.get_mark_price(instType=InstType.OPTION.value)
                mark_px_cache.update_from_json(json_response)
                time.sleep(2)
            except KeyboardInterrupt:
                break
            except (OkxAPIException, OkxParamsException, OkxRequestException):
                logger.warning(traceback.format_exc())
                time.sleep(10)


if __name__ == "__main__":
    rest_mds = RESTMarketDataService()
    rest_mds.start()
