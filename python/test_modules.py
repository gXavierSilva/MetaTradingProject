import MetaTrader5 as mt5
print([f for f in dir(mt5) if "global" in f.lower()])

print("INFORMAÇÕES VELAS DA 5ª EM DIANTE ATÉ ÚLTIMA FECHADA:")
# print(f"Quantidade de velas: {len(velas_restantes)}")
print(velas_restantes)
print(' ')

# FILTRAR O PRIMEIRO CANDLE REAL DO DIA (A API VAI ENTREGAR O CORRETO)
# primeiro = df[df['time'].dt.date == dia].head(1)


def main():
    # Garantir conexão
    if not mt5.initialize():
        raise RuntimeError("Falha ao inicializar MT5")
    
    symbol = "XAUUSD"
    timeframe = mt5.TIMEFRAME_M5

    # Select Day
    dia = datetime(2025, 12, 11).date()

    # Obter o início do dia atual (meia-noite)
    timezone = pytz.timezone("Etc/UTC")
    hoje = datetime.now(tz=timezone).date()
    inicio_do_dia = datetime.combine(hoje, time.min).replace(tzinfo=timezone)
    fim_do_dia = datetime.combine(hoje, time.max).replace(tzinfo=timezone)

    # Converter para timestamp
    from_timestamp = int(inicio_do_dia.timestamp())
    to_timestamp = int(fim_do_dia.timestamp())

    # Obter candles apenas do dia atual
    rates = mt5.copy_rates_range(symbol, timeframe, from_timestamp, to_timestamp)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    open_channel_candles = df.head(4)

    open_list = open_channel_candles['open'].tolist()
    close_list = open_channel_candles['close'].tolist()
    high_list = open_channel_candles['high'].tolist()
    low_list = open_channel_candles['low'].tolist()

    open_channel_params = [max(high_list+low_list), min(high_list+low_list)]
    volume = (open_channel_params[0]-open_channel_params[1])
    
    print(' ')
    print(f'MARCAÇÃO CANAL DE ABERTURA: {open_channel_params}')
    print(f'VOLUME (pt): {volume*100}')
    print(' ')

    # SCRIPT PARA IDENTIFICAR ROMPIMENTO
    channel_params = []
    for i, value in df.iterrows():
        if value['close'] > open_channel_params[0]: 
            channel_params = [open_channel_params[0], open_channel_params[0]+volume]

            print(f'CANDLE DE ROMPIMENTO: ')
            print(value)
            print(' ')
            print('TIME DE INÍCIO PARA PRÓXIMA VERIFICAÇÃO DE ROMPIMENTO: ')
            print(value['time'])

            print(' ')
            print(f'MARCAÇÃO CANAL 01: {channel_params}')
            break
        elif value['close'] < open_channel_params[1]:
            channel_params = [open_channel_params[1], open_channel_params[1]-volume]

            print(f'CANDLE DE ROMPIMENTO: ')
            print(value)
            print(' ')
            print('TIME DE INÍCIO PARA PRÓXIMA VERIFICAÇÃO DE ROMPIMENTO: ')
            print(value['time'])

            print(' ')
            print(f'MARCAÇÃO CANAL 01: {channel_params}')
            break

    # if primeiro.empty:
    #     print("Nenhum candle encontrado para esse dia.")
    # else:
    #     idx = primeiro.index[0]
        
    #     # Primeiras 4 velas
    #     open_channel_candles = df.loc[idx: idx+3]

    #     high_list = open_channel_candles['high'].tolist()
    #     low_list = open_channel_candles['low'].tolist()
        
    #     open_channel_first_level = max(high_list+low_list)
    #     open_channel_second_level = min(high_list+low_list)

    #     canaldeabertura = [open_channel_first_level, open_channel_second_level]
    #     open_channel_extension = (canaldeabertura[0]-canaldeabertura[1])*100
    #     print(' ')
    #     print("CANAL DE ABERTURA (WICK): ")
    #     print(canaldeabertura)
    #     print(' ')
    #     print(f'VOLUME: {open_channel_extension} pts')
    #     print(' ')

    #     if idx + 4 < len(df) - 1:
    #         velas_restantes = df.loc[idx+4: len(df)-2]  # -2 para excluir a última aberta
    #     else:
    #         velas_restantes = pd.DataFrame()  # DataFrame vazio se não houver velas suficientes
        
    #     print('INFORMAÇÕES DE ROMPIMENTO PARA C1:')
    #     for i, value in velas_restantes.iterrows():
    #         if value['close'] > 4210.91 or value['close'] < 4205.69:
    #             print(value)
    #             print(f"CANDLE POSITION: {value['time']}, OPEN: {value['open']}, CLOSE: {value['close']}, VOLUME: {value['tick_volume']}")
    #             print(' ')
    #             if value['close'] > 4210.91:
    #                 print(f'C1 superior. Nível: {4210.91+(open_channel_extension/100)}')
    #                 print(' ')
    #             else:
    #                 print(f'C1 inferior. Nível: {4205.69-(open_channel_extension/100)}')
    #                 print(' ')
    #             break

    return

    # return open_channel_candles, velas_restantes



    print(' ')
    print(f'MARCAÇÃO CANAL DE ABERTURA: {openingChannelParams}')
    print(f'VOLUME (pt): {volume*100}')
    print(' ')

    print(f'PARÂMETROS DO ÚLTIMO CANAL: {last_channel_params}')
    print(' ')
    print('PARÂMETROS DO CANDLE DE ROMPIMENTO:')
    print(rupture_candle)
