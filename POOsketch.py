import MetaTrader5 as mt5
import pytz
import pandas as pd
from datetime import datetime, time

class Access:
    def __init__(self):
        pass
 
    def open(self):
        if not mt5.initialize():
            print("Falha ao inicializar MT5")
            return

class Operation:
    # constructor
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe

    def get_candles(self, description, initial, final):
        print(description)
        # Garante que o símbolo está visível no MT5
        if not mt5.symbol_select(self.symbol, True):
            print(f"Falha ao selecionar {self.symbol}")
            return None

        rates = mt5.copy_rates_range(self.symbol, self.timeframe, initial, final)
        
        if rates is None:
            print(f"Erro ao capturar dados: {mt5.last_error()}")
            
        return rates    
    
    def __str__(self):
        return f"{self.symbol} {self.timeframe} {self.date}"

class Candle:
    def __init__(self, wickm, wickl, bodym, bodyl):
        self.wickm = wickm
        self.wickl = wickl
        self.bodym = bodym
        self.bodyl = bodyl
    
    def properties(self):
        json = {
            "wick_max": self.wickm,
            "wick_low": self.wickl,
            "body_max": self.bodym,
            "body_low": self.bodyl
        }
        print(json)

class Channel:
    def __init__(self, reference, channel_scope, candles):
        self.reference = reference
        self.channel_scope = channel_scope
        self.candles = candles
    
    def set_channel(self):
        if(self.reference == "openning channel"):
            channel = {
                "channel_name": self.reference,
                "channel_scope": self.channel_scope,
                "max_level" : max(candle[2] for candle in self.candles),
                "lower_level": min(candle[3] for candle in self.candles),
                "channel_expansion": (max(candle[2] for candle in self.candles) - min(candle[3] for candle in self.candles))*100
            }
        else:
            channel = "Piroquinha"
        return channel
    
    def verify_rupture(self, channel, candles):
        # Script de verificação de rompimento
        for c in candles:
            if c[4] > channel["max_level"]:
                print(datetime.fromtimestamp(c[0]))
                print("Rompimento superior")
                break
            elif c[4] < channel["lower_level"]:
                print(datetime.fromtimestamp(c[0]))
                print("Rompimento inferior")
                break
            else:
                print("Nenhum rompimento")
                pass

        # Retorno da verificação em um objeto
        objetoderompimento = {
            "candle": candles[0],
            "ratio": 40,
            "direction": "down",
        }
        # objetoderompimento = Rompimento()
        return objetoderompimento

class Entry:
    def __init__(self, symbol, volume, sl, tp, fill, description, type):
        self.symbol = symbol
        self.volume = volume
        self.sl = sl
        self.tp = tp
        self.fill = fill
        self.description = description
        self.type = type

    def properties(self):
        json = {
            "symbol": self.symbol,
            "volume": self.volume,
            "sl": self.sl,
            "tp": self.tp,
            "fill": self.fill,
            "description": self.description,
            "type": self.type
        }
        print(json)
    
    def setlevels(self):
        pass

timezone = pytz.timezone("Etc/UTC")

# Inicia o sistema MetaTrader5
meta_trader = Access()
meta_trader.open()

# --------------------------------------////////////////////---------------------------------------------------

localchannel = None
globalchannel = None

# Cria/inicia Operação 
run = Operation('XAUUSD.h', mt5.TIMEFRAME_M5)

# Pega velas iniciais 
candles = pd.DataFrame(run.get_candles("openning", datetime(2026, 5, 26, 1, 00, 00, tzinfo=timezone), datetime(2026, 5, 26, 23, 59, 59, tzinfo=timezone)))
initial_candles = candles.head(4).values.tolist()

# Marca canais (Canal Local e Canal Global)
local = Channel("openning channel", "local", initial_candles)
geral = Channel("openning channel", "global", initial_candles)
localchannel = local.set_channel()
globalchannel = geral.set_channel()
print(f'Nível Superior: {localchannel["max_level"]}')
print(f'Nível Inferior: {localchannel["lower_level"]}')

# Verifica o rompimento
# Pega resto das velas, objetivo: verificar rompimento para entrada ou duplicação de CA
remainder = candles.iloc[4:].values.tolist()
rupture = geral.verify_rupture(globalchannel, remainder)
print(" ")
print(rupture)

# # DEPENDENDO DO ROMPIMENTO:

# if(rompimento > 40):
# # Rompimento: > 40%
#     local = Channel() #atualiza
#     geral = Channel() #atualiza
#     localchannel = local.set_channel()
#     globalchannel = geral.set_channel()
#     print(localchannel, globalchannel)

# # Pega resto das velas, verificar rompimento para entrada
#     candles = pd.DataFrame(run.get_candles())
#     remainder = candles.iloc[4:].values.tolist()
# else:
# # Rompimento: < 40%
# # Realiza a entrada, caso confirmada pelo user
# # 0.01 = volume
# # 400  = channel position 01
# # 200  = channel position 02
#     trade = Entry(0.01, 400, 200)
# # Posiciona os níveis do trade (SL e TP)
#     trade.positionlevels()

# # ...
