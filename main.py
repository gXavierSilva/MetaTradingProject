import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, time, timedelta
import pytz
from JSONModule import salvar_json_metatrader
symbol = 'XAUUSD'
timeframe = mt5.TIMEFRAME_M5

timezone = pytz.timezone("Etc/UTC")
# day = datetime.now(tz=timezone).date() 
day = datetime(2026, 2, 6).date()
date_initial = datetime.combine(day, time.min).replace(tzinfo=timezone)
date_final = datetime.combine(day, time.max).replace(tzinfo=timezone)

# ----------------------------------------------------------------------------------
# 1. MARCA O CANAL DE ABERTURA (CA)
# ----------------------------------------------------------------------------------
def markOpenningChannel(timestamp_from, timestamp_to, candles_quantity):
    rates = mt5.copy_rates_range(symbol, timeframe, timestamp_from, timestamp_to)
    if rates is None or len(rates) == 0:
        return None
        
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # Pegar as primeiras 'candles_quantity' velas
    open_channel_candles = df.head(candles_quantity)

    # Último timestamp para saber onde começar a checar rompimentos
    ultimotimestamp = int(open_channel_candles['time'].iloc[-1].timestamp())

    high_list = open_channel_candles['high'].tolist()
    low_list = open_channel_candles['low'].tolist()

    max_high = max(high_list)
    min_low = min(low_list)
    volume = max_high - min_low
    
    # Estrutura do Canal: [0]High, [1]Low, [2]Timestamp, [3]Volume, [4]Nível (0 = CA)
    open_channel_params = [max_high, min_low, ultimotimestamp, volume, 0]
    
    return open_channel_params

# ----------------------------------------------------------------------------------
# 2. CALCULA E MARCA O NOVO CANAL APÓS ROMPIMENTO
# ----------------------------------------------------------------------------------
def markChannel(rupture_value, direction, candle_ruptura, last_channel_data):
    """
    rupture_value: O valor do preço que foi rompido (pode ser o extremo global alto ou baixo)
    last_channel_data: Dados do último canal criado (para calcular volume e nível)
    """
    last_volume = last_channel_data[3]
    last_level = last_channel_data[4] # 0=CA, 1=C1, etc.
    
    # LÓGICA DE VOLUME:
    # Do CA(0) para C1(1) -> Volume igual (1x)
    # Do C1(1) para C2(2) em diante -> Volume dobra (2x)
    if last_level == 0:
        new_volume = last_volume
    else:
        new_volume = last_volume * 2
        
    # DEFINIR LIMITES DO NOVO CANAL
    # O novo canal é sempre "anexado" ao nível rompido
    if direction == 'Up':
        nivelbaixo = rupture_value
        nivelalto = rupture_value + new_volume
    elif direction == 'Down':
        nivelalto = rupture_value
        nivelbaixo = rupture_value - new_volume
    
    timestamp_ruptura = int(candle_ruptura['time'].timestamp())
    next_level = last_level + 1
    
    new_channel = [nivelalto, nivelbaixo, timestamp_ruptura, new_volume, next_level]
    return new_channel

# ----------------------------------------------------------------------------------
# 3. VERIFICA ROMPIMENTO NOS EXTREMOS GLOBAIS
# ----------------------------------------------------------------------------------
def checkGlobalRupture(global_high, global_low, start_timestamp):
    # Pega dados a partir do último rompimento até o fim do dia
    rates = mt5.copy_rates_range(symbol, timeframe, start_timestamp, int(date_final.timestamp()))
    
    if rates is None or len(rates) < 2:
        return None, None, None

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # Pula a primeira vela (que é a vela onde o canal anterior foi definido)
    df_check = df.iloc[1:]

    for i, value in df_check.iterrows():
        # Verifica se rompeu o TOPO SUPREMO ou o FUNDO SUPREMO da estrutura
        if value['close'] > global_high:
            return value, 'Up', global_high # Retorna a vela, direção e qual valor foi rompido
        elif value['close'] < global_low:
            return value, 'Down', global_low # Retorna a vela, direção e qual valor foi rompido

    return None, None, None

# ----------------------------------------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------------------------------------
def main():
    if not mt5.initialize():
        print("Falha ao inicializar MT5")
        return

    channels = []
    
    # 1. Cria CA
    ca_channel = markOpenningChannel(int(date_initial.timestamp()), int(date_final.timestamp()), 4)
    
    if ca_channel is None:
        print("Dados insuficientes para CA.")
        return

    channels.append(ca_channel)
    print(f"CA Marcado: Topo={ca_channel[0]:.2f}, Fundo={ca_channel[1]:.2f}, Vol={ca_channel[3]:.2f}")

    # 2. Define os limites globais iniciais (Extremos do CA)
    current_global_high = ca_channel[0]
    current_global_low = ca_channel[1]
    last_timestamp_check = ca_channel[2]

    # Loop de execução
    while True:
        # Verifica rompimento considerando APENAS os extremos globais
        candle, direction, limit_broken = checkGlobalRupture(current_global_high, current_global_low, last_timestamp_check)

        if candle is None:
            break # Fim do dia ou sem novos rompimentos

        # Pega o último canal adicionado para calcular o próximo volume
        last_channel = channels[-1]
        
        print(f"Rompimento {direction} no nível {last_channel[4]} (Preço rompeu {limit_broken:.2f})")

        # Cria o novo canal
        new_channel = markChannel(limit_broken, direction, candle, last_channel)
        channels.append(new_channel)

        # ATUALIZA OS LIMITES GLOBAIS
        # Se rompeu pra cima, o teto sobe. O chão se mantém.
        # Se rompeu pra baixo, o chão desce. O teto se mantém.
        if direction == 'Up':
            current_global_high = new_channel[0] # Novo topo global é o topo do novo canal
            # current_global_low mantém o mesmo
        elif direction == 'Down':
            current_global_low = new_channel[1] # Novo fundo global é o fundo do novo canal
            # current_global_high mantém o mesmo
            
        # Atualiza o timestamp para a próxima verificação não olhar para trás
        last_timestamp_check = new_channel[2]

    # print("\n--- Relatório Final ---")
    # print(f"Total de canais: {len(channels)}")
    canaizinhos = []
    for c in channels:
        tipo = "CA" if c[4] == 0 else f"C{c[4]}"
        # print(f"{tipo}: High = {c[0]:.2f}, Low = {c[1]:.2f}, Vol = {c[3]:.2f}")
        alto = c[0]
        baixo = c[1]
        volumi = c[3]
        canaizinhos.append({
            "channel_name": f'{tipo} {day}',
            "high": alto,
            "low": baixo,
            "vol": volumi,
            "initial": f'{day} 01:00:00',
            "final": f'{day} 23:55:00'
            # "final": f'{day + timedelta(days=1)} 01:00:00'
        })
        canais = {
            "channel": canaizinhos
        }
    # print(canais)
    salvar_json_metatrader(canais)

    mt5.shutdown()

# ----------------------------------------------------------------------------------
# FUNÇÃO PARA EMITIR JSON COM INFORMAÇÕES DE OPERAÇÃO
# ----------------------------------------------------------------------------------
def gerarjsoncominformacoesdeentrada():
    print("damn")

if __name__ == "__main__":
    main()