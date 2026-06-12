import MetaTrader5 as mt5
import pytz
import pandas as pd
import math
from typing import Any
from datetime import datetime
from abc import ABC, abstractmethod

# Abertura (1), Máximo (2), Mínimo (3), Fechamento(4)
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

class Channel(ABC):
    def __init__(self, reference: str, channel_scope: str, candles: list[Any]):
        self.reference = reference
        self.channel_scope = channel_scope
        self.candles = candles

    # Verifica, dentro de um intervalo de candles, se houve o rompimento do canal passado
    def verify_rupture(self, channel: dict[str, float], candles: list[Any]):
        for candle in candles:
            if candle[4] > channel["max_level"]:
                rupture = {
                    "candle": candle,
                    "ratio": math.trunc(((int((candle[4]-channel["max_level"])*100)/channel["channel_expansion"])*100)*100)/100,
                    "direction": "up",
                }
                break
            elif candle[4] < channel["lower_level"]:
                rupture = {
                    "candle": candle,
                    "ratio": math.trunc(((int((channel["lower_level"]-candle[4])*100)/channel["channel_expansion"])*100)*100)/100,
                    "direction": "down",
                }
                break
            else:
                pass
        return rupture

    # Com os atributos passados, cria um objeto com as propriedades de um canal
    @abstractmethod
    def set_channel(self, previous_channel=None, rupture_candle=None) -> dict[str, float]:
        pass

class GlobalChannel(Channel):
    def set_channel(self) -> dict[str, float]:
        # Monta o canal com base nos quatro primeiros candles
        if(self.reference == "openning channel"):
            channel = {
                "channel_name": self.reference,
                "channel_scope": self.channel_scope,
                "max_level" : max(candle[2] for candle in self.candles),
                "lower_level": min(candle[3] for candle in self.candles),
                "channel_expansion": (max(candle[2] for candle in self.candles) - min(candle[3] for candle in self.candles))*100
            }
        return channel

class LocalChannel(Channel):
    def set_channel(self) -> dict[str, float]:
        # Monta o canal com base nos quatro primeiros candles
        if(self.reference == "openning channel"):
            channel = {
                "channel_name": self.reference,
                "channel_scope": self.channel_scope,
                "max_level" : max(candle[2] for candle in self.candles),
                "lower_level": min(candle[3] for candle in self.candles),
                "channel_expansion": (max(candle[2] for candle in self.candles) - min(candle[3] for candle in self.candles))*100
            }
        return channel

class Entry:
    def __init__(self, symbol, volume, sl, tp, fill, description, type):
        self.symbol = symbol
        self.volume = volume
        self.sl = sl
        self.tp = tp
        self.fill = fill
        self.description = description
        self.type = type

    def set_levels(self):
        json = {
            "symbol": self.symbol,
            "volume": self.volume,
            "sl": self.sl,
            "tp": self.tp,
            "fill": self.fill,
            "description": self.description,
            "type": self.type
        }
        return json

timezone = pytz.timezone("Etc/UTC")

# Inicia o sistema MetaTrader5
meta_trader = Access()
meta_trader.open()

day_initial = datetime(2026, 6, 12, 1, 00, 00, tzinfo=timezone)
day_final = datetime(2026, 6, 12, 23, 59, 59, tzinfo=timezone)

run = Operation('XAUUSD.h', mt5.TIMEFRAME_M5)

while True:
    # Pega todas as velas dentro do intervalo passado
    candles = pd.DataFrame(run.get_candles("openning", day_initial, day_final))

    # Pega quatro velas iniciais 
    initial_candles = candles.head(4).values.tolist()

#   //////////////////////////////////     MARCA CANAL     \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    # Marca canais (Canal Local e Canal Global)
    local = LocalChannel("openning channel", "local", initial_candles)
    localchannel = local.set_channel()
    geral = GlobalChannel("openning channel", "global", initial_candles)
    globalchannel = geral.set_channel()

    print(" ")
    print("Canal de Abertura: ")
    for property in globalchannel:
        print(f'    {property}: {globalchannel[property]}')
    print(" ")

#   //////////////////////////////////     VERIFICA ROMPIMENTO     \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

    # Verifica o rompimento do canal global
    remainder = candles.iloc[4:].values.tolist()
    rupture = geral.verify_rupture(globalchannel, remainder)
    print(rupture)
    print(" ")

#   //////////////////////////////////     ENTRADA (CASO ATENDA REQUISITOS)     \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    requisitos = False
    volume, sl, tp, description, requisitos = False

    if requisitos:
        print("Abrindo operação.")
        trade = Entry("HK50.h", volume, sl, tp, "Tudo/Nada", description, type)
    
    break
        
    # points = globalchannel["channel_expansion"]+2*((15/100)*globalchannel["channel_expansion"])
    # volume = (0.1*50*1000)/(0.13*points)
    # sl = globalchannel["lower_level"]-((15/100)*(globalchannel["channel_expansion"]/100)) if rupture["direction"] == "up" else globalchannel["max_level"]+((15/100)*(globalchannel["channel_expansion"]/100))
    # tp = (globalchannel["max_level"]+(globalchannel["channel_expansion"]/100))-((15/100)*(globalchannel["channel_expansion"]/100)) if rupture["direction"] == "up" else (globalchannel["lower_level"]-(globalchannel["channel_expansion"]/100))+((15/100)*(globalchannel["channel_expansion"]/100))
    # description = "Compra" if rupture["direction"] == "up" else "Venda"
    # type = "buy" if rupture["direction"] == "up" else "sell"

    # trade = Entry("HK50.h", volume, sl, tp, "Tudo/Nada", description, type)

    # trade_object = trade.set_levels()

    # print("Propriedades da entrada:")
    # print(trade_object)
    # print(" ")

    # # verificar resultado da operação
    # trade_candles = pd.DataFrame(run.get_candles("trade", datetime.fromtimestamp((rupture["candle"][0]), tz=timezone), day_final))
    # trade_candles = trade_candles.values.tolist()
    # for candle in trade_candles:
    #     if trade_object["type"] == "buy":
    #         if candle[2] >= trade_object["tp"]:
    #             print("Resultado: Take")
    #             break
    #         elif candle[3] <= trade_object["sl"]:
    #             print("Resultado: Stop")
    #             break
    #         else:
    #             pass
    #     elif trade_object["type"] == "sell":
    #         if candle[2] >= trade_object["sl"]:
    #             print("Resultado: Stop")
    #             break
    #         elif candle[3] <= trade_object["tp"]:
    #             print("Resultado: Take")
    #             break
    #         else:
    #             pass

#   //////////////////////////////////     ANOTAÇÕES     \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

#   Quando CA
#       Canal Local: CA
#       Canal Global: CA
#   Quando C1
#       Canal Local: C1 (CA)
#       Canal Global: C1+CA
#   Quando C2
#       Canal Local: C2 (C1+CA)
#       Canal Global: C2+(C1+CA)

#   Addons (propriedades da operação)
#       Alvo
#           Take de 1 (-R:R)
#           1:1
#           Take de 2 (+R:R)
#       Otimização de R:R
#       Entrada direta ou formação de C1
#       Virada de mão caso StopLoss

#   Além de identificar se é canal global ou local, precisa de script
#   para identificar se é canal de abertura, primeiro canal, segundo canal...
#   Canal Local: canal formado no momento da execução
#   Canal Global: canal de referencia atual, que servirá para identificação de rompimento e formação de novos canais

#   Canal de Abertura: Primeiro canal a ser formado, a partir das quatro primeiras velas
#   Canal 01: Segundo canal a ser formado, mesma extensão do canal local anterior, novo canal local e canal global CA+C1
#   Canal 02: Terceiro canal a ser formado, mesma extensão do canal global (c1+ca)

#   Na criação do canal, preciso passar um identificador que mostra qual o índice dele
#   se é o canal 0 (CA), se é o canal 1 (c1), se é o canal 2 (c2) e etc 
#   isso para conseguir calcular o Canal Global