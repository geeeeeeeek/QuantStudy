from tigeropen.common.consts import (Language,  # 语言
                                     Market,  # 市场
                                     BarPeriod,  # k线周期
                                     QuoteRight)  # 复权类型
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.trade.trade_client import TradeClient

from tigeropen.common.consts import Market, SecurityType, Currency
from tigeropen.common.util.contract_utils import stock_contract
from tigeropen.common.util.order_utils import (market_order,  # 市价单
                                               limit_order,  # 限价单
                                               stop_order,  # 止损单
                                               stop_limit_order,  # 限价止损单
                                               trail_order,  # 移动止损单
                                               order_leg)  # 附加订单


# 老虎api实现实盘交易


def get_client_config():
    """
    https://quant.itigerup.com/#developer 开发者信息获取
    """
    client_config = TigerOpenClientConfig()
    client_config.private_key = read_private_key('E:\\software\\rsa_key')
    client_config.tiger_id = '20150279'
    client_config.account = '20190425155943480'
    client_config.language = Language.zh_CN
    return client_config


client_config = get_client_config()

trade_client = TradeClient(client_config)

contract = stock_contract(symbol='GOOG', currency='USD')

# 创建订单对象
stock_order = limit_order(account=client_config.account,  # 下单账户，可以使用标准、环球、或模拟账户
                          contract=contract,  # 第1步中获取的合约对象
                          action='BUY',
                          quantity=100,
                          limit_price=207.60)

# 提交订单
trade_client.place_order(stock_order)

print(stock_order)
