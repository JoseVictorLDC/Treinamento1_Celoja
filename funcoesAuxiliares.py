from bs4 import BeautifulSoup
import requests
import json

# caminhoArquivo = "dadosFarmaPonte/dadosFarmaPonteMamae-e-bebe.json"

# Verifica quantos produtos foram gravados.
def verificaQuantidadeItens(caminhoArquivo):
    with open(caminhoArquivo, 'r') as arquivo:
        dados = json.load(arquivo)
    return len(dados)

# if __name__ == "__main__":
#     print(verificaQuantidadeItens(caminhoArquivo))

# Coleta as categorias dos produtos.
def coletaCategorias():
    paginaInicial = requests.get("https://www.farmaponte.com.br/").text

    paginaBs = BeautifulSoup(paginaInicial, "lxml")

    categorias = []

    linkCategorias = paginaBs.find(id="menuDepartament").find_all("a", class_="root")

    for categoria in linkCategorias:
        categorias.append(categoria['href'])

    return categorias

# Imprime algumas estatísticas sobre a extração.
def finalizaExtracao(numPaginas, caminhoArquivoJSON, caminhoArquivoCSV, tempoExecucaoFormatado):
    print(f"Extração finalizada com sucesso!\n")
    print(f"Estatísticas:")
    print(f"- {numPaginas} páginas")
    print(f"- {verificaQuantidadeItens(caminhoArquivoJSON)} produtos")
    print(f"{tempoExecucaoFormatado}\n")
    print(f"Confira os dados no arquivo {caminhoArquivoJSON} ou {caminhoArquivoCSV}\n")

# Solicita ao usuário para que informe a categoria que ele deseja a extração.
def escolheCategoria():
    categorias = coletaCategorias()
    print("Escolha uma das categorias disponíveis para a extração:")
    for categoria in categorias:
        print(f'- {categoria.split("/")[1]} - {retornaNumeroDePaginas(categoria)} páginas')
    while True:
        categoriaEscolhida = input("Categoria: ")
        if f"/{categoriaEscolhida}/" not in categorias:
            print("Categoria não existe, escolha uma categoria válida.")
        else:
            break
    return categoriaEscolhida

# Pega o número de páginas da categoria.
def retornaNumeroDePaginas(categoria):
    textoHtml = requests.get(f'https://www.farmaponte.com.br/{categoria}/').text
    paginaHtml = BeautifulSoup(textoHtml, 'lxml')
    numPaginas = int(paginaHtml.find_all("div", class_="text-center pt-3")[-1].text.split()[-1])
    return numPaginas

def retornaTempoDeExecucaoFormatado(tempoExecucao):
    segundos = round(tempoExecucao)
    if segundos > 60:
        minutos = segundos // 60
        segundos = segundos % 60
        if minutos > 60:
            horas = minutos // 60
            minutos = minutos % minutos
            return f"Tempo de extração: {horas} horas, {minutos} minutos e {segundos} segundos."
        else:
            return f"Tempo de extração: {minutos} minutos e {segundos} segundos."
    else: return f"Tempo de extração: {segundos} segundos."