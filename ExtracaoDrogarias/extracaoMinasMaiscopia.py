# Import do código
import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
import pandas as pd
import math

if __name__ != "__main__":
    from ExtracaoDrogarias.funcoesAuxiliares import retornaTempoDeExecucaoFormatado
    import streamlit as st

# Capturando todas as URLs
def extracaoDeDados():
    print("Iniciando Extração Minas Mais.")
    inicio = time.time()
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

    # Achando número de produtos
    url = "https://www.drogariasminasmais.com.br/medicamentos/hypera?initialMap=c&initialQuery=medicamentos&map=category-1,brand&page=1"
    requisicao = requests.get(url)
    soup = BeautifulSoup(requisicao.text, 'html.parser')
    numeroProdutos = soup.find_all('script')[-34].text
    numeroProdutos = numeroProdutos[:-8].split("quantity")[66:]

    listaNumeroProdutos = []
    listaNumeroProdutosCorreta = []

    for i in numeroProdutos:
        listaNumeroProdutos.append(i.split(",")[0])

    for i in listaNumeroProdutos:
        aux = i.replace('"', "")
        aux = aux.replace(":", "")
        listaNumeroProdutosCorreta.append(int(aux))

    # Função getAllData
    def getAllData(): 
        def getJSON(soup):
            jsonSujo = soup.find_all('script')[-34].text
            jsonSujo = jsonSujo[:-8]
            jsonLimpo = jsonSujo.split("__STATE__ = ")[1]
            return jsonLimpo

        total_pages = []

        for i in listaNumeroProdutosCorreta:
            total_pages.append(math.ceil(i/15))

        listaJSON = []
        k = 0

        for i in listaUrls:
            for page_number in total_pages[k:]:
                for paginaAtual in range(1, page_number + 1):
                    url = str(i) + str(paginaAtual)
                    requisicao = requests.get(url)
                    soup = BeautifulSoup(requisicao.text, 'html.parser')
                    listaJSON.append(getJSON(soup))
                k = k + 1
                break
        
        return listaJSON

    # Função de execução rápida
    all_workers = os.cpu_count()

    listaJSON = []

    with ThreadPoolExecutor(max_workers=all_workers) as executor:
        # Submeter as tarefas e obter os futuros
        futures = [executor.submit(getAllData) for _ in range(1)]
        
        # Processar os resultados à medida que forem completados
        for future in as_completed(futures):
            result = future.result()  # Obter o resultado do futuro
            if isinstance(result, list):  # Garantir que o resultado seja uma lista
                listaJSON.extend(result)  # Adicionar todos os itens da lista à listaJSON
            else:
                raise ValueError("Esperado uma lista de strings, mas obteve um tipo diferente")
            
    # Criando o JSON e capturando todos os códigos de produtos
    ean = []
    precoComDesconto = []
    precoSemDesconto = []
    desconto = []
    marcas = []
    nomes = []

    for i in range(0, len(listaJSON)):
        dados = json.loads(listaJSON[i])
        listaProdutosCerta = []
        listaProdutos = []
        listaFinal = []
        j = 0 

        for i in dados.keys():
            if i.split("$ROOT_QUERY")[0] == "":
                break
            if j % 18 == 0:
                listaProdutos.append(i)
            j = j + 1

        for i in listaProdutos:
                listaProdutosCerta.append(i.split(".")[0].replace("$", ""))

        for i in listaProdutosCerta:
            if i.split("Product:")[0] == "":
                listaFinal.append(i)

        # Pegando todos os dados dos produtos
        for i in listaFinal:
            nomes.append(dados[i]["productName"])
            marcas.append(dados[i]["brand"])

        for i in listaFinal:
            # Parte do JSON que tem o EAN e precos
            localJson1 = str(i) + '.items({"filter":"ALL"}).0'
            dadosDesejados1 = dados.get(localJson1)

            ean.append(dadosDesejados1["ean"])

        for i in listaFinal:
            # Parte do JSON que tem o EAN e precos
            localJson2 = "$" + str(i) + '.items({"filter":"ALL"}).0.sellers.0.commertialOffer'
            dadosDesejados2 = dados.get(localJson2)

            precoComDesconto.append(dadosDesejados2["Price"])
            precoSemDesconto.append(dadosDesejados2["ListPrice"])
            desconto.append((1 - (dadosDesejados2["Price"]/dadosDesejados2["ListPrice"])))

    fim = time.time()
    tempoExecucao = fim - inicio
    tempoExecucaoFormatado = retornaTempoDeExecucaoFormatado(tempoExecucao=tempoExecucao)
    print(tempoExecucaoFormatado)

    if __name__ != "__main__":
        st.success("Extração finalizada, os dados extraídos já estão atualizados na área de visualização!", icon="✅")
        with st.expander("Estatísticas sobre a extração"):
            st.write(f"{tempoExecucaoFormatado}")

    # Criando dataFrame
    data = {"nome": nomes, "marcas": marcas, "EAN": ean, "Preço com desconto": precoComDesconto, "Preço sem desconto": precoSemDesconto, "Desconto": desconto}
    df = pd.DataFrame(data)

    # Exportando tudo para um excel
    df.to_excel('ExtracaoDrogarias/dadosDrogariaMinasMais/dadosXLSX/DadosMinasMaisTODOS.xlsx',sheet_name='Sheet1')
