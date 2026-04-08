import MetaTrader5 as mt5
import pytz
from datetime import datetime, time

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

class Operation:
    # constructor
    def __init__(self, symbol, timeframe, lote, take_level, stop_level):
        self.symbol = symbol
        self.timeframe = timeframe
        self.lote = lote
        self.take_level = take_level
        self.stop_level = stop_level

    def properties(self):
        json = {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "lote": self.lote,
            "take": self.take_level,
            "stop": self.stop_level
        }
        print(json)
 
    def get_candles(self):
        # Garante que o símbolo está visível no MT5
        if not mt5.symbol_select(self.symbol, True):
            print(f"Falha ao selecionar {self.symbol}")
            return None

        timezone = pytz.timezone("Etc/UTC")
        # Nota: Usei 2026 pois é a data que você enviou, mas verifique se há dados para esse dia.
        day = datetime(2026, 4, 8) 
        
        date_initial = datetime(day.year, day.month, day.day, tzinfo=timezone)
        date_final = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=timezone)

        # O MT5 aceita objetos datetime diretamente ou timestamps
        rates = mt5.copy_rates_range(self.symbol, self.timeframe, date_initial, date_final)
        
        if rates is None:
            print(f"Erro ao capturar dados: {mt5.last_error()}")
            
        return rates    
    
    def __str__(self):
        return f"{self.lote} {self.take_level} {self.stop_level}"

class Channel:
    def __init__(self, reference, max_level, lower_level, expansion):
        self.reference = reference
        self.max_level = max_level
        self.lower_level = lower_level
        self.expansion = expansion
    
    def properties(self):
        json = {
            "reference": self.reference,
            "max_level": self.max_level,
            "lower_level": self.lower_level,
            "expansion": self.expansion
        }
        print(json)

class Access:
    def __init__(self):
        pass
 
    def open(self):
        if not mt5.initialize():
            print("Falha ao inicializar MT5")
            return

# inicial_candle = Candle(2, 4, 5, 3)
# inicial_candle.properties()
# print(" ")

# openning_channel = Channel("Canal de Abertura", 4456, 4436,(4456-4436))
# openning_channel.properties()
# print(" ")

xauh1m1 = Access()
xauh1m1.open()

openning = Operation('XAUUSD.h', mt5.TIMEFRAME_M5, 0.01, 400, 200)
openning.properties()
candles = openning.get_candles()
print(" ")
print(candles)
