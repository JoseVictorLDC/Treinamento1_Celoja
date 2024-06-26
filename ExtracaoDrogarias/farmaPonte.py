from bs4 import BeautifulSoup
import requests
import json
import os
import time
import pandas as pd
if __name__ != "__main__":
    from ExtracaoDrogarias.funcoesAuxiliares import finalizaExtracao, escolheCategoria, retornaTempoDeExecucaoFormatado, limpaTela, finalizaExtracaoStreamlit
    import streamlit as st

def extracaoDeDados(categoria="saude"):
    inicio = time.time()
    # Pega o número de páginas da categoria.
    textoHtml = requests.get(f'https://www.farmaponte.com.br/{categoria}/').text
    paginaHtml = BeautifulSoup(textoHtml, 'lxml')
    numPaginas = int(paginaHtml.find_all("div", class_="text-center pt-3")[-1].text.split()[-1])

    # Cria lista que será populada com os dados dos produtos.
    dados = []
    
    # Itera por todas as páginas existentes na categoria.
    paginasExtraidas = 0
    if __name__ != "__main__":
        barraDeProgresso = st.progress(0)
        statusDoProgresso = st.empty()
    for pagina in range(1, numPaginas+1):
        while True:
            try:
                htmlText = requests.get(f'https://www.farmaponte.com.br/{categoria}/?p={pagina}').text
                break
            except:
                time.sleep(1)
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
            while True:
                try:
                    htmlIndividual = requests.get(url).text
                    break
                except:
                    time.sleep(1)
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
                "Preco pix": precoPix,
                "Preco venda": precoVenda,
                "URL": url,
                "EAN": ean,
                "Marca": marca,
            })
            produtosExtraidos += 1
            progressoTotal = ((paginasExtraidas + (produtosExtraidos/len(produtos)))/ numPaginas) * 100
            limpaTela()
            print("Iniciando extração dos produtos")
            print(f"url: https://www.farmaponte.com.br/{categoria}/")
            print(f"Progresso da extração: {progressoTotal:.2f}%\n")
            if __name__ != "__main__":
                barraDeProgresso.progress(progressoTotal/100)
                statusDoProgresso.write(f"Progresso da extração: {progressoTotal:.2f}%\n")
        paginasExtraidas += 1

    # Define o caminho do arquivo no qual serão gravados os dados json.
    caminhoArquivoJSON = f"ExtracaoDrogarias/dadosFarmaPonte/dadosJSON/dadosFarmaPonte{categoria.capitalize()}.json"

    # Grava os dados em formato JSON.
    with open(caminhoArquivoJSON, 'w') as arquivo:
        json.dump(dados, arquivo, indent=4)


    # Grava os dados em formato XLSX.
    df = pd.DataFrame(dados)
    caminhoArquivoExcel = f"ExtracaoDrogarias/dadosFarmaPonte/dadosXLSX/dadosFarmaPonte{categoria.capitalize()}.xlsx"
    df.to_excel(caminhoArquivoExcel, index=False)

    # Calcula tempo e prepara para uma melhor exibição.
    fim = time.time()
    tempoExecucao = fim - inicio
    tempoExecucaoFormatado = retornaTempoDeExecucaoFormatado(tempoExecucao=tempoExecucao)

    # Exibe dados finais sobre a extração.
    if __name__ != "__main__":
        st.success("Extração finalizada, os dados extraídos já estão atualizados na área de visualização!", icon="✅")
        with st.expander("Estatísticas sobre a extração"):
            finalizaExtracaoStreamlit(numPaginas, caminhoArquivoJSON, tempoExecucaoFormatado)
    finalizaExtracao(numPaginas, caminhoArquivoJSON, caminhoArquivoExcel, tempoExecucaoFormatado)


if __name__ == "__main__":
    from funcoesAuxiliares import finalizaExtracao, escolheCategoria, retornaTempoDeExecucaoFormatado, limpaTela
    categoriaEscolhida = escolheCategoria()
    extracaoDeDados(categoria=categoriaEscolhida)
