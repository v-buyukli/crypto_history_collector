from app.enums import ExchangeEnum
from app.exchanges.binance import BinanceClient
from app.exchanges.bybit import BybitClient


EXCHANGE_CLIENTS = {
    ExchangeEnum.BINANCE: BinanceClient,
    ExchangeEnum.BYBIT: BybitClient,
}
