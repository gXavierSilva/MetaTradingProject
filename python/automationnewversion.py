import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, time
import pytz

symbol = 'XAUUSD'
timeframe = mt5.TIMEFRAME_M5

timezone = pytz.timezone("Etc/UTC")
day = datetime.now(tz=timezone).date() # hoje = datetime(2025, 12, 11).date()
date_initial = datetime.combine(day, time.min).replace(tzinfo=timezone)
date_final = datetime.combine(day, time.max).replace(tzinfo=timezone)

# DEFINE O 'open_channel_params' COM BASE NA LÓGICA DE MARCAÇÃO DO CA EM ABERTURA 
def markOpenningChannel(timestamp_from, timestamp_to, candles_quantity):
    rates = mt5.copy_rates_range(symbol, timeframe, timestamp_from, timestamp_to)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # PEGAR CANDLES INICIAIS (BASE EM CONFIGURAÇÃO)
    open_channel_candles = df.head(candles_quantity)

    # PEGAR ULTIMO TIMESTAMP DAS 4 VELAS
    ultimotimestamp = int(open_channel_candles['time'][3].timestamp())

    # PASSAR TODOS OS NÍVEIS DE CADA ASPECTO DAS CANDLES
    open_list = open_channel_candles['open'].tolist()
    close_list = open_channel_candles['close'].tolist()
    high_list = open_channel_candles['high'].tolist()
    low_list = open_channel_candles['low'].tolist()

    # UPGRADE: FAZER O open_channel_params SER SELECIONÁVEL DENTRE AS 8 COMBINAÇÕES POSSIVEIS
    open_channel_params = [max(high_list+low_list), min(high_list+low_list), ultimotimestamp, (max(high_list+low_list)-min(high_list+low_list))]
    
    # ESTA FUNÇÃO VAI RETORNAR OS PARAMS (PRIMEIRO NÍVEL +, SEGUNDO NÍVEL - E ULTIMO TIMESTAMP) E O VOLUME
    return open_channel_params

# PEGA AS INFORMAÇÕES DO CANDLE ONDE HOUVE RUPTURA E PASSA TODOS OS PARÂMETROS PARA MARCAÇÃO DO CANAL
def markChannel(rupture_candle, direction , last_channel_params):
    # identificar se é rompimento superior ou inferior
    if direction == 'Up':
        nivelalto = last_channel_params[0] + last_channel_params[3]
        nivelbaixo = last_channel_params[0]
    elif direction == 'Down':
        nivelalto = last_channel_params[1]
        nivelbaixo = last_channel_params[1] - last_channel_params[3]
    
    channel_params = [nivelalto, nivelbaixo, int(rupture_candle['time'].timestamp()), (nivelalto-nivelbaixo)]
    
    return channel_params

# VERIFICA SE, QUANDO E ONDE HOUVE RUPTURA DO CANAL, PASSANDO TODAS AS INFORMAÇÕES DO CANDLE ONDE ISSO OCORREU
def checkRupture(channel_params):
    # 'df' VAI SER TODAS AS CANDLES NO INTERVALO DA ÚLTIMA DO CA - channel_params[2] - ATÉ A MAIS ATUAL - int(fim_do_dia.timestamp()) -
    rates = mt5.copy_rates_range(symbol, timeframe, channel_params[2], int(date_final.timestamp()))
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # VERIFICAR, DENTRO DO INTERVALO DE CANDLES, ONDE HÁ UM ROMPIMENTO
    # ROMPIMENTO: SE A CANDLE TEM FECHAMENTO FORA DOS EXTREMOS DO CANAL DE ABERTURA
    for i, value in df.iterrows():
        if value['close'] > channel_params[0]:
            return value, 'Up' , channel_params
        elif value['close'] < channel_params[1]:
            return value, 'Down' , channel_params

    return None, None, None

# FUNÇÃO PRINCIPAL QUE RODA O SCRIPT
def main():
    if not mt5.initialize():
        raise RuntimeError("Falha ao inicializar MT5")

    # actual_channel_params = markOpenningChannel(int(date_initial.timestamp()), int(date_final.timestamp()), 4)

    channels = []
    channel = markOpenningChannel(int(date_initial.timestamp()), int(date_final.timestamp()), 4)
    while True:
        channels.append(channel)
        candle, direction, params = checkRupture(channel)

        if not params:
            break

        channel = markChannel(candle, direction, params)
    print(channels)

    return

if __name__ == "__main__":
    main()