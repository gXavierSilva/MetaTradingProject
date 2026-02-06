class Operation:
    # constructor
    def __init__(self, lote, take_level, stop_level):
        self.lote = lote
        self.take_level = take_level
        self.stop_level = stop_level

    def fatiar(self):
        print("fatia gostoso vai fatia")

    def get_json(self):
        json = {
            "lote": self.lote,
            "take": self.take_level,
            "stop": self.stop_level
        }
        print(json)
    
    def __str__(self):
        return f"{self.lote} {self.take_level} {self.stop_level}"

class Access:
    def __init__(self, symbol, timeframe):
        pass

abertura = Operation(0.01, 400, 200)

print(abertura)
abertura.fatiar()
abertura.get_json()