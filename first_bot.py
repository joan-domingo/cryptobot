import websocket, json, math, config
from binance.client import Client
from binance.enums import *
from decimal import Decimal


CURRENCY = 'LUNA'
TRADE_CURRENCY = CURRENCY.lower() + 'busd'

SOCKET = "wss://stream.binance.com:9443/ws/" + TRADE_CURRENCY + "@kline_1m"

in_position_to_buy = True
last_buy_price = 0

client = Client(config.API_KEY, config.API_SECRET )

info = client.get_symbol_info(TRADE_CURRENCY)
# print(info)

# print(client.get_asset_balance(asset=CURRENCY))

floor_value = Decimal(1 / Decimal(info['filters'][2]['minQty']))

def buy(coin_price):
    global last_buy_price

    try:
        # Calculate how much $10 can buy
        coin_qty = Decimal(10) / Decimal(coin_price)
        buy_quantity = math.floor((coin_qty * floor_value)/floor_value)
        print(buy_quantity)

        print("sending buy order")
        order = client.create_order(symbol=TRADE_CURRENCY.upper(), side = SIDE_BUY, type = ORDER_TYPE_MARKET, quantity = buy_quantity)
        print(order)
        
        # Calculate $ spent
        myOrder = order['fills'][0]
        last_buy_price = float(myOrder['qty'])
    except Exception as e:
        print(e)
        return False

    return True

def sell():
    global floor_value
    global client

    try:
        sell_quantity = math.floor(Decimal(client.get_asset_balance(asset=CURRENCY)['free']) * floor_value)/floor_value
        print(sell_quantity)

        print("sending sell order")
        order = client.create_order(symbol=TRADE_CURRENCY.upper(), side = SIDE_SELL, type = ORDER_TYPE_MARKET, quantity = sell_quantity)
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

        if in_position_to_buy:
            # buy
            coin_price = float(close)
            print("buy at {}".format(coin_price))
            order_succeeded = buy(coin_price)
            if order_succeeded:
                in_position_to_buy = False
                last_buy_price = close

        else:
            print("trying to sell higher than {}".format(last_buy_price * 0.05 + last_buy_price))
            if float(close) >= last_buy_price * 0.05 + last_buy_price:
                # sell
                order_succeeded = sell()
                print("Sell !!!!")
                if order_succeeded:
                    in_position_to_buy = True



ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()