import requests
from bs4 import BeautifulSoup
import os
import time
import json
import re
import json
import pandas as pd

# Capturando todas as URLs

# Função de acessar site
all_workers = os.cpu_count()

def access_site(url, max_attempts=all_workers):
    headers = {'Accept': '*/*', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    for retry in range(max_attempts):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
        except Exception as e:
                print(f"An error occurred while accessing URL: {url}: {e}. Retrying... (Attempt {retry + 1}/{max_attempts})")
                time.sleep(1)

# Função captura de todos os nomes de marcas e criação de URLs
def getNomeMarcas():
    response = access_site("https://www.drogariasminasmais.com.br/medicamentos")
    soup = BeautifulSoup(response.text, 'html.parser')
    sessaoMarcasGrandes = soup.find('div', class_='vtex-search-result-3-x-filter__container vtex-search-result-3-x-filter__container--responsive-result-content-mz0001 bb b--muted-4 vtex-search-result-3-x-filter__container--brand')
    sessaoMarcas = sessaoMarcasGrandes.find('div', class_='vtex-search-result-3-x-filterTemplateOverflow vtex-search-result-3-x-filterTemplateOverflow--responsive-result-content-mz0001 pb5 overflow-y-auto')
    marcas = sessaoMarcas.find_all('label', class_='vtex-checkbox__label w-100 c-on-base pointer')
    return marcas

# Criando uma lista de URLs ainda não bem estruturadas
urlSuja = getNomeMarcas()
urlLimpa = []

# Limpando lista das URLs
for i in urlSuja:
    # Criando texto separado e minusculo com "-"
    texto = i.text.lower()
    textoNovo = texto.replace(" ", "-")
    textoNovissimo = textoNovo.replace("/", "-")

    # Salvando tudo em uma lista
    urlLimpa.append(textoNovissimo)

listaUrls = []

# Criando todas as URLs
for j in urlLimpa:
    URL = "https://www.drogariasminasmais.com.br/medicamentos/" + j + "?initialMap=c&initialQuery=medicamentos&map=category-1,brand&page="
    listaUrls.append(URL)

# Função para encontrar um arquivo JSON secreto dependendo da página e da marca
def getJSON(urlInicial, page_number):
    url = str(urlInicial) + str(page_number)
    while True:
        try:
            requisicao = requests.get(url)
            break
        except:
            time.sleep(1)
    soup = BeautifulSoup(requisicao.text, 'lxml')
    jsonSujo = soup.find_all('script')[-34].text
    eanRegex = r'"ean":"(?:\d{1,13})"'
    eans = re.findall(eanRegex, jsonSujo)
    if len(eans) != 0:
        print(url)
        return jsonSujo
    else:
        return
    
total_pages = 50
listaJSON = []
dados = []

# Iteração por páginas de usuários
for url in listaUrls: 
    for page_number in range(1, total_pages + 1):
        res = getJSON(url, page_number)
        if res == None:
            break
        else:
            listaJSON.append(res)

# Expreções Regex para encontrar os dados.
eanRegex = r'"ean":"(\d{1,13})"'
nomeRegex = r'"nameComplete":"([^"]+)"'
skuRegex = r'"productId":"(\d+)"'
precoSemDescontoRegex = r'"ListPrice":(\d+(?:\.\d+)?)'
precosAVistaRegex = r'"spotPrice":(\d+(?:\.\d+)?)'
marcasRegex = r'"brand":"([^"]+)"'

for i in range(len(listaJSON)):

    # Encontra os dados.
    eans = re.findall(eanRegex, listaJSON[i])
    nomes = re.findall(nomeRegex, listaJSON[i])
    skus = re.findall(skuRegex, listaJSON[i])
    precosSemDesconto = re.findall(precoSemDescontoRegex, listaJSON[i])
    precosAVista = re.findall(precosAVistaRegex, listaJSON[i])
    marcas = re.findall(marcasRegex, listaJSON[i])
    descontos = []

    # Transforma os preços para float e calcula os descontos.
    for i in range(len(precosSemDesconto)):
        precosAVista[i] = float(precosAVista[i])
        precosSemDesconto[i] = float(precosSemDesconto[i])
        desconto = (1 - (precosAVista[i]/precosSemDesconto[i]))
        descontos.append(round(desconto, 2)*100)

    for i in range(len(eans)):
        dados.append({
            "Nome do produto": nomes[i],
            "Desconto": descontos[i],
            "Preco unitario": precosSemDesconto[i],
            "SKU": skus[i],
            "Preco Venda": precosAVista[i],
            "ean": eans[i],
            "Marca": marcas[i],
        })

    caminhoArquivo = f"dadosDrogariaMinasMais/dadosJSON/dadosDrogariaMinasMais.json"

        # Grava os dados em formato JSON.
    with open(caminhoArquivo, 'w') as arquivo:
        json.dump(dados, arquivo, indent=4)

        # Grava os dados em formato XLSX.
    df = pd.DataFrame(dados)
    caminhoArquivoExcel = f"dadosDrogariaMinasMais/dadosXLSX/dadosDrogariaMinasMais.xlsx"
    df.to_excel(caminhoArquivoExcel, index=False)
