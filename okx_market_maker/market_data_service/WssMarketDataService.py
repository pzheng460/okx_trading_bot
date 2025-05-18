import threading
from typing import Dict, List
import time
import asyncio
import json
import logging
from okx_market_maker import order_books
from okx_market_maker.market_data_service.model.OrderBook import OrderBook, OrderBookLevel
from okx.websocket.WsPublicAsync import WsPublicAsync

logger = logging.getLogger(__name__)

class WssMarketDataService(WsPublicAsync):
    """
    这个类用于封装WebSocket市场数据服务的相关函数。
    主要用于处理WebSocket连接、订阅和取消订阅市场数据等功能。
    继承自WsPublic类，提供了WebSocket连接的基本功能。
    """
    def __init__(
        self, 
        url: str, 
        inst_id: str, 
        channel: str = "books5"
    ) -> None:
        """
        初始化 WssMarketDataService 类。

        Args:
            url (str): WebSocket 连接的 URL。
            inst_id (str): 交易对的 ID。
            channel (str): 订阅的频道，默认为 "books5"。
        """
        super().__init__(url)
        self.inst_id = inst_id
        self.channel = channel
        order_books[self.inst_id] = OrderBook(inst_id=inst_id)
        self.args = []

    async def run_service(self) -> None:
        """
        运行服务。
        """
        args = self._prepare_args()
        print(args)
        print("subscribing")
        await self.subscribe(args, _callback)
        self.args += args

    async def stop_service(self) -> None:
        """
        停止服务。
        """
        await self.unsubscribe(self.args, lambda message: print(message))
        await self.close()

    def _prepare_args(self) -> List[Dict]:
        """
        准备订阅参数。

        Returns:
            List[Dict]: 订阅参数列表。
        """
        args = []
        books5_sub = {
            "channel": self.channel,
            "instId": self.inst_id
        }
        args.append(books5_sub)
        return args


def _callback(message) -> None:
    """
    处理 WebSocket 消息的回调函数。

    Args:
        message (dict): WebSocket 消息。
    """
    # 统一把 str → dict
    if isinstance(message, str):
        try:
            message = json.loads(message)
        except json.JSONDecodeError:
            logger.warning("非 JSON 消息：%s", message)
            return

    arg = message.get("arg")
    # print(message)
    if not arg or not arg.get("channel"):
        return
    if message.get("event") == "subscribe":
        return
    
    # 如果频道是 books5、books、bbo-tbt、books50-l2-tbt 或 books-l2-tbt，则处理订单簿快照或更新
    if arg.get("channel") in ["books5", "books", "bbo-tbt", "books50-l2-tbt", "books-l2-tbt"]:
        on_orderbook_snapshot_or_update(message)
        # print(order_books)


def on_orderbook_snapshot_or_update(message) -> None:
    """
    处理订单簿快照或更新。

    Args:
        message (dict): WebSocket 消息。
        {
            "arg": {
                "channel": "books",
                "instId": "BTC-USDT"
            },
            "action": "snapshot",
            "data": [{
                "asks": [
                    ["8476.98", "415", "0", "13"],
                    ["8477", "7", "0", "2"],
                    ["8477.34", "85", "0", "1"],
                    ["8477.56", "1", "0", "1"],
                    ["8505.84", "8", "0", "1"],
                    ["8506.37", "85", "0", "1"],
                    ["8506.49", "2", "0", "1"],
                    ["8506.96", "100", "0", "2"]
                ],
                "bids": [
                    ["8476.97", "256", "0", "12"],
                    ["8475.55", "101", "0", "1"],
                    ["8475.54", "100", "0", "1"],
                    ["8475.3", "1", "0", "1"],
                    ["8447.32", "6", "0", "1"],
                    ["8447.02", "246", "0", "1"],
                    ["8446.83", "24", "0", "1"],
                    ["8446", "95", "0", "3"]
                ],
                "ts": "1597026383085",
                "checksum": -855196043
            }]
        }
    """
    arg = message.get("arg")
    inst_id = arg.get("instId")
    action = message.get("action")
    if inst_id not in order_books:
        order_books[inst_id] = OrderBook(inst_id=inst_id)
    data = message.get("data")[0]
    if data.get("asks"):
        if action == "snapshot" or not action:
            ask_list = [OrderBookLevel(price=float(level_info[0]),
                                       quantity=float(level_info[1]),
                                       order_count=int(level_info[3]),
                                       price_string=level_info[0],
                                       quantity_string=level_info[1],
                                       order_count_string=level_info[3],
                                       ) for level_info in data["asks"]]
            order_books[inst_id].set_asks_on_snapshot(ask_list)
        if action == "update":
            for level_info in data["asks"]:
                order_books[inst_id].set_asks_on_update(
                    OrderBookLevel(price=float(level_info[0]),
                                   quantity=float(level_info[1]),
                                   order_count=int(level_info[3]),
                                   price_string=level_info[0],
                                   quantity_string=level_info[1],
                                   order_count_string=level_info[3],
                                   )
                )
    if data.get("bids"):
        if action == "snapshot" or not action:
            bid_list = [OrderBookLevel(price=float(level_info[0]),
                                       quantity=float(level_info[1]),
                                       order_count=int(level_info[3]),
                                       price_string=level_info[0],
                                       quantity_string=level_info[1],
                                       order_count_string=level_info[3],
                                       ) for level_info in data["bids"]]
            order_books[inst_id].set_bids_on_snapshot(bid_list)
        if action == "update":
            for level_info in data["bids"]:
                order_books[inst_id].set_bids_on_update(
                    OrderBookLevel(price=float(level_info[0]),
                                   quantity=float(level_info[1]),
                                   order_count=int(level_info[3]),
                                   price_string=level_info[0],
                                   quantity_string=level_info[1],
                                   order_count_string=level_info[3],
                                   )
                )
    if data.get("ts"):
        order_books[inst_id].set_timestamp(int(data["ts"]))
    if data.get("checksum"):
        order_books[inst_id].set_exch_check_sum(data["checksum"])


class ChecksumThread(threading.Thread):
    """
    这个类用于轮询校验订单簿的校验和。
    """
    def __init__(self, wss_mds: WssMarketDataService) -> None:
        """
        初始化 ChecksumThread 类。
        Args:
            wss_mds (WssMarketDataService): WssMarketDataService 实例。
        """
        self.wss_mds = wss_mds
        super().__init__()

    async def run(self) -> None:
        """
        在后台线程中不断轮询校验所有订单簿（OrderBook）的校验和是否正确。
        """
        while 1:
            try:
                for inst_id, order_book in order_books.items():
                    order_book: OrderBook
                    if order_book.do_check_sum():
                        continue
                    # 如果某个订单簿的校验和失败，则重启 WebSocket 服务（WssMarketDataService）来重新获取数据。
                    await self.wss_mds.stop_service()
                    await asyncio.sleep(3)
                    await self.wss_mds.run_service()
                    break
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                print("Checksum task cancelled.")
                break
            except Exception as e:
                print(f"Unexpected error in checksum task: {e}")
                await asyncio.sleep(5)

async def main():
    # url = "wss://ws.okx.com:8443/ws/v5/public"
    url = "wss://ws.okx.com:8443/ws/v5/public?brokerId=9999"
    market_data_service = WssMarketDataService(url=url, inst_id="BTC-USDT-SWAP", channel="books")
    await market_data_service.start()
    await market_data_service.run_service()
    check_sum = ChecksumThread(market_data_service)
    await check_sum.start()
    await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
