from bs4 import BeautifulSoup
import requests
import time
import json
import re
from math import ceil

inicio = time.time()
from funcoesAuxiliares import retornaTempoDeExecucaoFormatado, limpaTela, jsonToXlsx

# Função para acessar url mesmo em caso de demora de resposta.
def acessaURL(url):
    cont = 0
    while True:
        try:
            response = requests.get(url)
            if response.text == "":
                cont+=1
                pass
            else:
                return response
        except:
            if cont % 5 == 0:
                time.sleep(2)
            else:
                time.sleep(1)

# Função para coletar as categorias
def coletaCategorias():
    url = f'https://www.saojoaofarmacias.com.br/medicamentos'
    textoHtml = acessaURL(url).text
    soup = BeautifulSoup(textoHtml, 'lxml')
    categoriasRegex = r'"category-2","selected":false,"value":"([^"]+)","link"'
    categorias = re.findall(categoriasRegex, str(soup))
    categorias.remove('fitoterapicos')
    return categorias

categorias = coletaCategorias()

# Função para acessar a categoria e coletar o número de produtos total
def coletaNumeroDeProdutos(categoria):
    url = f"https://www.saojoaofarmacias.com.br/medicamentos/{categoria}?initialMap=c&initialQuery=medicamentos&map=category-1,category-2"
    textoHTML = acessaURL(url).text
    soup = BeautifulSoup(textoHTML, 'lxml')
    numeroProdutosRegex = r'"recordsFiltered":(\d+),'
    numeroDeProdutos = int(re.findall(numeroProdutosRegex, str(soup))[0])
    return numeroDeProdutos

dados = []
caminhoArquivoJSON = "dadosSaoJoaoFarmacia/dadosJSON/saoJoaoFarmacia.json"
caminhoArquivoXLSX = "dadosSaoJoaoFarmacia/dadosXLSX/saoJoaoFarmacia.xlsx"
categoriaExtraida = 0

with open(caminhoArquivoJSON, 'w') as file:
            json.dump(dados, file, indent=4)

def extracaoDeDados(categoria):
    numeroDeProdutos = coletaNumeroDeProdutos(categoria)
    numeroDePaginas = ceil(numeroDeProdutos / 24)
    for pagina in range(1, numeroDePaginas+1):
        textoHtml = requests.get(f'https://www.saojoaofarmacias.com.br/medicamentos/{categoria}?initialMap=c&initialQuery=medicamentos&map=category-1,category-2&page={pagina}').text
        nomeRegex = r'"productName":"([^"]+)"'
        eanRegex = r'"ean":"(\d{0,14})"'
        marcaRegex = r'"brand":"([^"]+)"'
        precoRegex = r'"Price":\s*(\d+\.\d+|\d+)'
        precoSemDescontoRegex = r'"ListPrice":\s*(\d+\.\d+|\d+)'
        nomes = re.findall(nomeRegex, textoHtml)
        eans = re.findall(eanRegex, textoHtml)
        marcas = re.findall(marcaRegex, textoHtml)
        precos = re.findall(precoRegex, textoHtml)
        precosSemDesconto = re.findall(precoSemDescontoRegex, textoHtml)
        descontos = []
        dados = []
        for i in range(len(precosSemDesconto)):
            precos[i] = float(precos[i])
            precosSemDesconto[i] = float(precosSemDesconto[i])
            desconto = (1 - (precos[i]/precosSemDesconto[i]))
            descontos.append(round(round(desconto, 2)*100))
        for i in range(len(nomes)):
            dados.append({
                "Nome do produto": nomes[i],
                "Preco unitario": precosSemDesconto[i],
                "Preco venda": precos[i],
                "Desconto": descontos[i],
                "EAN": eans[i],
                "Marca": marcas[i],})
        try:
            with open(caminhoArquivoJSON, 'r') as file:
                dadosGravados = json.load(file)
            dadosGravados.extend(dados)
            with open(caminhoArquivoJSON, 'w') as file:
                json.dump(dadosGravados, file, indent=4)
        except:
            with open(caminhoArquivoJSON, 'w') as file:
                json.dump(dados, file, indent=4)
        limpaTela()
        print(f"Página {pagina} de {numeroDePaginas} de {categoria}")
        print(f"Categoria {categoriaExtraida} de {len(categorias)}")

for i in range(len(categorias)):
    categoriaExtraida += 1
    extracaoDeDados(categorias[i])

jsonToXlsx(caminhoArquivoJSON, caminhoArquivoXLSX)


fim = time.time()
tempoExecucao = fim - inicio
tempoExecucaoFormatado = retornaTempoDeExecucaoFormatado(tempoExecucao=tempoExecucao)
print(tempoExecucaoFormatado)