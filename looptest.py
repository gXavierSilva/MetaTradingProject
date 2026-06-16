from typing import Any
from abc import ABC, abstractmethod

# →↑↓✖✓
class Channel(ABC):
    def __init__(self, index:int):
        self.index = index

    def verify_rupture(self, channel:dict[str, float]):
        print("Verificando rompimento...")
        if channel["name"] == "c3":
            print("↓ | Rompimento NÃO identificado")
            print(" ")
            return False
        else:
            print("↑ | Rompimento identificado")
            print(" ")
            return True

    @abstractmethod
    def set(self) -> dict[str, float]:
        pass

class LocalChannel(Channel):
    def set(self, candles:list[Any], prev:dict[str, float]) -> dict[str, float]:
        if self.index == 0:
            # Se for Canal de Abertura
            json = {
                "scope": "local",
                "name": "ca",
                "max": max(candles),
                "low": min(candles),
                "extension": max(candles) - min(candles)
            }
        else:
            # Se NÃO for Canal de Abertura (c1, c2, c3...)
                # Direção do rompimento
                # Extensão do Canal Global anterior
            if rupture["direction"] == "up":
                json = {
                    "scope": "local",
                    "name": f'c{self.index}',
                    "max": prev,
                    "low": prev,
                    "extension": prev
                }
            else:
                json = {
                    "scope": "local",
                    "name": f'c{self.index}',
                    "max": prev,
                    "low": prev,
                    "extension": prev
                }

        return json

class GlobalChannel(Channel):
    def set(self, local:dict[str, float], prev:dict[str, float]) -> dict[str, float]:
        json = {
            "scope": "global",
            "name": "ca" if self.index == 0 else f'c{self.index}',
            "max": local + prev,
            "low": local + prev,
            "extension": local + prev
        }
        return json

a = 0
rupture = None
previous_reference = None
candles = None
while True:
    if rupture or a == 0:
        local = LocalChannel(a)
        reference = GlobalChannel(a)

        # Cria um JSON com as informações do canal →
        local_channel = local.set(candles, previous_reference) # Retorna um JSON com as propriedades do Canal Local
        global_channel = reference.set(local_channel, previous_reference) # Retorna um JSON com a propriedades do Canal Global atual

        # Verifica rompimento do Canal de Referência
        rupture = reference.verify_rupture(global_channel)

        # ↓ ITERAÇÃO ↓
        previous_reference = global_channel
        a += 1
    else:
        print("Rompimento não identificado ou não existente.")
        print(" ")
        break

# print(f'Índice passado para o canal: {reference.index}')
# for property in global_channel:
#     print(f'    {property}: {global_channel[property]}')
# print(" ")

# FAZER ELE CRIAR OS CANAIS COM BASE NO INDICE E NO ROMPIMENTO
# ATUALIZAR VARIAVEIS DE CANAIS E ROMPIMENTO
# LÓGICA DE ABERTURA DE OPERAÇÃO

# 1° EXECUÇÃO:
#     CANAL LOCAL: CA
#     CANAL GLOBAL (REFERENCIA): CA + 0  (LOCAL ATUAL + GLOBAL ANTERIOR)
# 2° EXECUÇÃO:
#     CANAL LOCAL: C1
#     CANAL GLOBAL (REFERENCIA): C1 + CA (LOCAL ATUAL + GLOBAL ANTERIOR)
# 3° EXECUÇÃO:
#     CANAL LOCAL: C2
#     CANAL GLOBAL (REFERENCIA): C2 + (C1 + CA) (LOCAL ATUAL + GLOBAL ANTERIOR)