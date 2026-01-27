import MetaTrader5 as mt5
import pandas as pd
import ta
from datetime import date, datetime, timedelta

def main():
    # Garantir conexão
    if not mt5.initialize():
        raise RuntimeError("Falha ao inicializar MT5")
    
    symbol = "XAUUSD"
    timeframe = mt5.TIMEFRAME_M5

    # dia desejado
    dia = datetime(2025, 12, 9).date()

    # carregar muitos candles
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 2000)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # FILTRAR O PRIMEIRO CANDLE REAL DO DIA (A API VAI ENTREGAR O CORRETO)
    primeiro = df[df['time'].dt.date == dia].head(1)

    if primeiro.empty:
        print("Nenhum candle encontrado para esse dia.")
    else:
        idx = primeiro.index[0]
        quatro = df.loc[idx: idx+3]

        open_list = quatro['open'].tolist()
        close_list = quatro['close'].tolist()
        high_list = quatro['high'].tolist()
        low_list = quatro['low'].tolist()

        print("INFOMACOES GERAIS 4 PRIMEIRAS CANDLES: ")
        print(quatro)
        print(' ')

        print("CANAL/MARCACAO EM CORPO: ")
        body = [max(open_list+close_list), min(open_list+close_list)]
        print(body)
        print(f'TAMANHO: {(body[0]-body[1])*100} pts')
        print(' ')

        print("CANAL/MARCACAO EM PAVIO: ")
        wick = [max(high_list+low_list), min(high_list+low_list)]
        print(wick)
        print(f'TAMANHO: {(wick[0]-wick[1])*100} pts')
        print(' ')

        print("CANAL/MARCACAO PAVIO-CORPO: ")
        wick_body = [min(wick), max(body)]
        print(wick_body)
        print(f'TAMANHO: {(wick_body[1]-wick_body[0])*100} pts')
        print(' ')

        print("CANAL/MARCACAO CORPO-PAVIO: ")
        body_wick = [min(body), max(wick)]
        print(body_wick)
        print(f'TAMANHO: {(body_wick[1]-body_wick[0])*100} pts')
        print(' ')

if __name__ == "__main__":
    main()
