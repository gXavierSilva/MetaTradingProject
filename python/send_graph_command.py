import json
import os

MT5_CMD_FILE = os.path.expanduser(
    "C:\\Users\\Public\\cmd.txt"
)

def send_graph_command(command: dict):
    """
    Envia um comando para o EA via arquivo TXT.
    O EA deve ler esse arquivo e interpretar o comando.
    """

    # transforma o dict em texto json
    data = json.dumps(command)

    # escreve no arquivo
    with open(MT5_CMD_FILE, "w", encoding="utf-8") as f:
        f.write(data)

    print(f"[OK] Comando enviado: {data}")


def send_horizontal_line(symbol: str, price: float, name: str = "hline_python"):
    """
    Envia uma linha horizontal para ser desenhada no gráfico.
    """
    cmd = {
        "type": "HLINE",
        "symbol": symbol,
        "price": price,
        "name": name
    }

    send_graph_command(cmd)


if __name__ == "__main__":
    # exemplo de teste
    send_horizontal_line("XAUUSD", 4450.00, "linha_teste")
