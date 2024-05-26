from bs4 import BeautifulSoup
import requests
import time
import json
import re
from math import ceil
from ExtracaoDrogarias.funcoesAuxiliares import retornaTempoDeExecucaoFormatado, limpaTela, jsonToXlsx

if __name__ != "__main__":
    from ExtracaoDrogarias.funcoesAuxiliares import retornaTempoDeExecucaoFormatado, limpaTela, verificaQuantidadeItens
    import streamlit as st

caminhoArquivoJSON = "ExtracaoDrogarias/dadosSaoJoaoFarmacia/dadosJSON/saoJoaoFarmacia.json"
caminhoArquivoXLSX = "ExtracaoDrogarias/dadosSaoJoaoFarmacia/dadosXLSX/saoJoaoFarmacia.xlsx"

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
    # Antes a categoria fitoterápicos estava dando problema por causa de erro no site, agora eles arrumaram.
    # categorias.remove('fitoterapicos')
    return categorias

# Função para acessar a categoria e coletar o número de produtos total
def coletaNumeroDeProdutos(categoria):
    url = f"https://www.saojoaofarmacias.com.br/medicamentos/{categoria}?initialMap=c&initialQuery=medicamentos&map=category-1,category-2"
    textoHTML = acessaURL(url).text
    soup = BeautifulSoup(textoHTML, 'lxml')
    numeroProdutosRegex = r'"recordsFiltered":(\d+),'
    numeroDeProdutos = int(re.findall(numeroProdutosRegex, str(soup))[0])
    return numeroDeProdutos

# Função principal de extração de dados
def extracaoDeDados():
    dadosNovos = []
    with open(caminhoArquivoJSON, 'w') as file:
        json.dump(dadosNovos, file, indent=4)
    inicio = time.time()
    categoriaExtraida = 0
    statusExtracao = st.empty()
    statusCategoriaExtraida = st.empty()
    categorias = coletaCategorias()

    for j in range(len(categorias)):
        categoriaExtraida += 1
        numeroDeProdutos = coletaNumeroDeProdutos(categorias[j])
        numeroDePaginas = ceil(numeroDeProdutos / 24)
        for pagina in range(1, numeroDePaginas+1):
            textoHtml = requests.get(f'https://www.saojoaofarmacias.com.br/medicamentos/{categorias[j]}?initialMap=c&initialQuery=medicamentos&map=category-1,category-2&page={pagina}').text
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
            print(f"Página {pagina} de {numeroDePaginas} de {categorias[j]}")
            print(f"Categoria {categoriaExtraida} de {len(categorias)}")
            if __name__ != "__main__":
                statusExtracao.write(f"Página {pagina} de {numeroDePaginas} de {categorias[j]}")
                statusCategoriaExtraida.write(f"Categoria {categoriaExtraida} de {len(categorias)}")


    jsonToXlsx(caminhoArquivoJSON, caminhoArquivoXLSX)

    fim = time.time()
    tempoExecucao = fim - inicio
    tempoExecucaoFormatado = retornaTempoDeExecucaoFormatado(tempoExecucao=tempoExecucao)
    print(tempoExecucaoFormatado)

    if __name__ != "__main__":
        st.success("Extração finalizada, os dados extraídos já estão atualizados na área de visualização!", icon="✅")
        with st.expander("Estatísticas sobre a extração"):
            st.write(f"- {verificaQuantidadeItens(caminhoArquivoJSON)} produtos")
            st.write(f"{tempoExecucaoFormatado}")


if __name__ == "__main__":
    extracaoDeDados()