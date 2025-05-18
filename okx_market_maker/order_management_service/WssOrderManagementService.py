import json
import time
from typing import List, Dict
import asyncio
import logging

from okx_market_maker.order_management_service.model.Order import Order, Orders
from okx.websocket.WsPrivateAsync import WsPrivateAsync
from okx_market_maker import orders_container
from okx_market_maker.config.settings import API_KEY, API_KEY_SECRET, API_PASSPHRASE

logger = logging.getLogger(__name__)

class WssOrderManagementService(WsPrivateAsync):
    def __init__(self, url: str, api_key: str = API_KEY, passphrase: str = API_PASSPHRASE,
                 secret_key: str = API_KEY_SECRET, useServerTime: bool = False):
        super().__init__(api_key, passphrase, secret_key, url, useServerTime)
        self.args = []
        self.data_ready_event = asyncio.Event()

    async def run_service(self):
        args = self._prepare_args()
        print(args)
        print("subscribing")
        orders_container.append(Orders())
        await self.subscribe(args, _callback)
        self.args += args

    async def stop_service(self):
        await self.unsubscribe(self.args, lambda message: print(message))
        await self.close()

    @staticmethod
    def _prepare_args() -> List[Dict]:
        args = []
        orders_sub = {
            "channel": "orders",
            "instType": "ANY",
        }
        args.append(orders_sub)
        return args


def _callback(message) -> None:
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
    if arg.get("channel") == "orders":
        on_orders_update(message)
        # print(orders_container)


def on_orders_update(message):
    if not orders_container:
        orders_container.append(Orders.init_from_json(message))
    else:
        orders_container[0].update_from_json(message)

async def main():
    # url = "wss://ws.okx.com:8443/ws/v5/private"
    url = "wss://ws.okx.com:8443/ws/v5/private?brokerId=9999"
    order_management_service = WssOrderManagementService(url=url)
    await order_management_service.start()
    await order_management_service.run_service()
    await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main()) 
