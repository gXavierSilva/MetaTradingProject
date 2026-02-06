import json
import os

def salvar_json_metatrader(dados_genericos):
    # 2. Definição do caminho
    # O 'r' antes das aspas indica uma "raw string", essencial para caminhos Windows
    caminho_pasta = r'C:\Users\Kei\AppData\Roaming\MetaQuotes\Terminal\Common\Files'
    nome_arquivo = 'main.json'
    
    # Une o caminho e o nome do arquivo de forma segura para o SO
    caminho_completo = os.path.join(caminho_pasta, nome_arquivo)

    # 3. Verificação de segurança (Opcional, mas recomendado)
    # Verifica se a pasta existe. Se não, tenta criá-la.
    if not os.path.exists(caminho_pasta):
        try:
            os.makedirs(caminho_pasta)
            print(f"Aviso: A pasta não existia e foi criada em: {caminho_pasta}")
        except OSError as e:
            print(f"Erro ao acessar ou criar o diretório: {e}")
            return

    # 4. Salvar o arquivo
    try:
        with open(caminho_completo, 'w', encoding='utf-8') as arquivo:
            # indent=4 deixa o JSON visualmente organizado (pretty print)
            json.dump(dados_genericos, arquivo, indent=4)
        
        print(f"Sucesso! Arquivo salvo em: {caminho_completo}")
        
    except PermissionError:
        print("Erro: Permissão negada. Verifique se o arquivo não está aberto por outro programa.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    salvar_json_metatrader()