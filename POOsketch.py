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
        date_final = datetime(self.date.year, self.date.month, self.date.day, 23, 59, 59, tzinfo=timezone)

        rates = mt5.copy_rates_range(self.symbol, self.timeframe, date_initial, date_final)
        
        if rates is None:
            print(f"Erro ao capturar dados: {mt5.last_error()}")
            
        return rates    
    
    def __str__(self):
        return f"{self.lote} {self.take_level} {self.stop_level}"

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

# Inicia o sistema MetaTrader5
meta_trader = Access()
meta_trader.open()

# Objeto principal
hk50 = Operation('HK50.h', mt5.TIMEFRAME_M1, datetime(2026, 5, 7, 1, 00, 00), 0.01, 400, 200)

candles = pd.DataFrame(hk50.get_candles())

lista_4_primeiras = candles.head(4).values.tolist()

maior_high = max(candle[2] for candle in lista_4_primeiras)
menor_low = min(candle[3] for candle in lista_4_primeiras)

print(' ')
print(f'Canal de Abertura: {maior_high}, {menor_low}')

formatada = datetime.fromtimestamp(lista_4_primeiras[3][0])

rupture_check = Operation('HK50.h', mt5.TIMEFRAME_M1, datetime(2026, 5, 7, formatada.hour, formatada.minute, 00), 0.01, 400, 200)
candles_for_rupture_check = rupture_check.get_candles()
freme = pd.DataFrame(candles_for_rupture_check)
candles_para_verificacao = freme.values.tolist()

res, motivo = next(((c, "Higher Level") if c[4] > maior_high else (c, "Lower Level") for c in candles_para_verificacao if c[4] > maior_high or c[4] < menor_low), (None, "Nenhum"))

print(' ')
print(f"Rompeu: {motivo}; Candle: ({res})")

direction = "Up" if motivo == "Higher Level" else "Down"
channel_volume = (maior_high-menor_low)*100
rupture_volume = (res[4] - (maior_high if direction == "Up" else menor_low))*100
rupture_rate = abs(int((100*rupture_volume)/channel_volume))

print(' ')
print('---- ROMPIMENTO ----')
print(f'Time: {datetime.fromtimestamp(res[0])}')
print(f'Close: {res[4]}')
print(f'Rupture Level: {motivo}')
print(f'Direction: {direction}')
print(f'Rupture Rate: {rupture_rate}%')
print(f'Entry? {"Yes" if rupture_rate < 40 else "No"}')

                    # Cria operação 
                    #     operacao = Operation()

                    # Pega todas as velas 
                    # objetivo: pegar quatro primeiras velas
                    #     operacao.conseguirvelas

                    # Marcar Canal de Abertura
                    #     localchanel = Channel()
                    #     globalchanel = Channel()

                    # Pegar todas as velas
                    # objetivo: verificar rompimento do canal global
                    #     operacao.conseguirvelas

                    # Dependendo do rompimento:

                    # Marcar Canal Um (se necessário)
                    #     localchanel = Channel() #atualizar
                    #     globalchanel = Channel() #atualizar

                    # Pegar todas as velas
                    # objetivo: verificar rompimento do canal global
                    #     operacao.conseguirvelas

                    # Abrir entrada no rompimento
                    #     entrada = Entry()

                    # Posicionar níveis de StopLoss e TakeProfit
                    #     entrada.posicionartakestop
                    
                    # OU

                    # Abrir entrada
                    #     entrada = Entry()

                    # Posicionar níveis de StopLoss e TakeProfit
                    #     entrada.posicionartakestop










# Agora eu preciso verificar todos os candles após o 4 candle para ver qual FECHA ultrapassando as linhas do canal

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