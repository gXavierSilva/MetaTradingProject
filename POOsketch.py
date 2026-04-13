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
    def __init__(self, symbol, timeframe, date, lote, take_level, stop_level):
        self.symbol = symbol
        self.timeframe = timeframe
        self.date = date
        self.lote = lote
        self.take_level = take_level
        self.stop_level = stop_level

    def properties(self):
        json = {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "date": self.date,
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
        
        date_initial = datetime(self.date.year, self.date.month, self.date.day, self.date.hour, self.date.minute, self.date.second, tzinfo=timezone)
        date_final = datetime(self.date.year, self.date.month, self.date.day, self.date.hour, 59, 59, tzinfo=timezone)

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
hour_turn = Operation('XAUUSD.h', mt5.TIMEFRAME_M1, datetime(2026, 4, 10, 2, 00, 00), 0.01, 400, 200)

# Roda script que inicia o sistema MetaTrader5
xauh1m1.open()

ht_candles = hour_turn.get_candles()
print(f'Quantidade de candles: {len(ht_candles)}')
print(" ")
print(ht_candles)

# o script da virada de hora vai ser um script que vai começar a rodar em todo inicio de hora do dia e vai findar quando tiver um retorno da operação
# o script da abertura vai ser um script que vai rodar todo inicio de abertura (configuravel, mas normalmente às 19:00 BRT) e vai findar quando tiver um retorno da operação
# ou seja, tenho dois scipts que têm a lógica semelhante, porém que rodam em momentos diferentes 
# preciso verificar se o script para backtest é o mesmo script que para rodar no dia atual. se não for, tornar o mesmo.

# A logica do script de Virada de Hora vai ser → Para toda hora exata que o dia tiver, ele vai executar o script:
#     Pegar as quatro primeiras velas a partir daquele horário; Pegar os níveis extremos (pavios); Marcar o Canal
#     de Abertura com eles; Verificar o tamanho do canal e, dependendo do tamanho, duplicar ele para a direção
#     que romper, ou fazer entrada com o lote calculado (fazer script para calcular lote) para a direção que
#     romper.
# Atenção! Para cada hora, um script novo inicia. O Passado só terminar de rodar quando a operação conclui.

# Prováveis métodos a serem criados:
#     mark_channel ou get_channel
#     check_rupture → vai ser nesse script que vou passar o dado que diz que vai duplicar ou já entrar?
#     get_lot
#     trade_entry
#     duplicate_channel (esse método, na verdade, é o mesmo do mark_channel, então a existencia dele
#         não é necessária, porém preciso pensar na lógica que faz um novo canal ser criado caso o
#         trade duplique o canal mesmo. Este novo canal será a junção do canal inicial e do
#         duplicado, e a entrada ocorrerá quando ele for rompido, formando o C2, que é a mesma
#         extensão dele.)

# horas_formatadas = [[f"{h:02d}", "00", "00"] for h in range(24)]
# print(horas_formatadas)