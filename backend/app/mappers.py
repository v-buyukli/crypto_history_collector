from app.enums import ExchangeEnum
from app.exchanges.binance import BinanceClient


EXCHANGE_CLIENTS = {
    ExchangeEnum.BINANCE: BinanceClient,
}
