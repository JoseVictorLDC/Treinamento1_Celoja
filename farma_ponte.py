from bs4 import BeautifulSoup
import requests
import json

# Pega o número de páginas da categoria.
textoHtml = requests.get(f'https://www.farmaponte.com.br/saude/').text
paginaHtml = BeautifulSoup(textoHtml, 'lxml')
numPaginas = int(paginaHtml.find_all("div", class_="text-center pt-3")[-1].text.split()[-1])

# Cria lista que será populada com os dados dos produtos.
dados = []

# Itera por todas as páginas existentes na categoria.
for pagina in range(1, numPaginas+1):
    htmlText = requests.get(f'https://www.farmaponte.com.br/saude/?p={pagina}').text
    soup = BeautifulSoup(htmlText, 'lxml')
    produtos = soup.find_all('div', class_="item-product")

    # Itera por todos os produtos contidos em uma das páginas e obtém os dados do produto.
    for produto in produtos:
        nomeProduto = produto.find('h2').text.strip()
        sku = produto.get('data-id').split("_")[-1]
        try:
            desconto = produto.find('span', class_="discount").text.split("%")[0]
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
        
# Define o caminho do arquivo no qual serão gravados os dados.
caminhoArquivo = "dadosFarmaPonte.json"

# Grava os dados em formato JSON.
with open(caminhoArquivo, 'a') as arquivo:
    json.dump(dados, arquivo, indent=4)
