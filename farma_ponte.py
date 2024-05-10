from bs4 import BeautifulSoup
import requests
import json
import os
from funcsAux import finalizaExtracao, escolheCategoria

def extracaoDeDados(categoria="saude"):
    # Pega o número de páginas da categoria.
    textoHtml = requests.get(f'https://www.farmaponte.com.br/{categoria}/').text
    paginaHtml = BeautifulSoup(textoHtml, 'lxml')
    numPaginas = int(paginaHtml.find_all("div", class_="text-center pt-3")[-1].text.split()[-1])

    # Cria lista que será populada com os dados dos produtos.
    dados = []
    
    # Itera por todas as páginas existentes na categoria.
    paginasExtraidas = 0
    for pagina in range(1, numPaginas+1):
        htmlText = requests.get(f'https://www.farmaponte.com.br/{categoria}/?p={pagina}').text
        soup = BeautifulSoup(htmlText, 'lxml')
        produtos = soup.find_all('div', class_="item-product")
        # Itera por todos os produtos contidos em uma das páginas e obtém os dados do produto.
        produtosExtraidos = 0
        for produto in produtos:
            nomeProduto = produto.find('h2').text.strip()
            sku = produto.get('data-id').split("_")[-1]
            try:
                desconto = int(produto.find('span', class_="discount").text.split("%")[0])
            except:
                desconto = 0
            try:
                precoUnitario = float(produto.find('p', class_='unit-price').text.split()[-1].replace(',','.'))
            except:
                precoUnitario = None
            try:
                precoPix = float(produto.find('p', class_='pix-price').find('strong').text.split()[-1].replace(',','.'))
            except:
                precoPix = None
            try:
                precoVenda = float(produto.find('strong', class_='description-price').text.strip().split()[-1].replace(',','.'))
            except:
                precoVenda = None

            # Pega a URL de um item específico e acessa ela para obter o EAN e a marca.
            url = f"https://www.farmaponte.com.br{produto.find('a', class_='item-image').get('href')}"
            htmlIndividual = requests.get(url).text
            individualSoup = BeautifulSoup(htmlIndividual, 'lxml')

            try:
                ean = individualSoup.find('span', class_='mr-3').find('meta', itemprop='gtin13')['content']
            except:
                ean = "Sem EAN"
            try:
                marca = individualSoup.find('meta', itemprop='brand')['content']
            except:
                marca = "Sem marca"

            # Adiciona os dicionários com os dados dos produtos à lista.
            dados.append({
                "Nome do produto": nomeProduto,
                "Desconto": desconto,
                "Preco unitario": precoUnitario,
                "SKU": sku,
                "Preco PIX": precoPix,
                "Preco Venda": precoVenda,
                "url": url,
                "ean": ean,
                "Marca": marca,
            })
            produtosExtraidos += 1
            progressoTotal = ((paginasExtraidas + (produtosExtraidos/len(produtos)))/ numPaginas) * 100
            os.system('clear')
            print("Iniciando extração dos produtos")
            print(f"url: https://www.farmaponte.com.br/{categoria}/")
            print(f"Progresso da extração: {progressoTotal:.2f}%")
        paginasExtraidas += 1


    # Define o caminho do arquivo no qual serão gravados os dados.
    caminhoArquivo = f"dadosFarmaPonte/dadosFarmaPonte{categoria.capitalize()}.json"

    # Grava os dados em formato JSON.
    with open(caminhoArquivo, 'w') as arquivo:
        json.dump(dados, arquivo, indent=4)

    finalizaExtracao(numPaginas, caminhoArquivo)

categoriaEscolhida = escolheCategoria()

extracaoDeDados(categoria=categoriaEscolhida)


