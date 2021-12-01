import websocket, json
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/bnbeur@kline_1m"
TRADE_SYMBOL= 'BNBEUR'
TRADE_QUANTITY = 1

closes = []
in_position_to_buy = True
last_buy_price = 0

client = Client("$API_KEY", "$API_SECRET")

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side = side, type = order_type, quantity = quantity)
        print(order)
    except Exception as e:
        print(e)
        return False

    return True

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes
    global in_position_to_buy
    global last_buy_price

    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']

    print("message received: {}".format(close))

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if in_position_to_buy:
            # buy
            # order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
            order_succeeded = True
            print('buy!!!!')
            if order_succeeded:
                in_position_to_buy = False
                last_buy_price = close

        else:
            if close >= last_buy_price * 0.05 + last_buy_price:
                # sell
                # order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                order_succeeded = True
                print("Sell !!!!")
                if order_succeeded:
                    in_position_to_buy = True



ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()