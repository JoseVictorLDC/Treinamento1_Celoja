import json
caminho_arquivo = "dadosFarmaPonte.json"

# Função para verificar quantos produtos foram gravados.
def verificaQuantidadeItens():
    with open(caminho_arquivo, 'r') as arquivo:
        dados = json.load(arquivo)
    print(len(dados))

verificaQuantidadeItens()