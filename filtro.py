import re
import pandas as pd

def extrair_tipo(titulo):
    matchComprimido = re.search(r'\b(comprimidos|Comprimido|cpds|cp)\b', titulo, re.IGNORECASE)
    matchCapsula = re.search(r'\b(Capsulas|Cápsula|cap|caps)\b', titulo, re.IGNORECASE)
    matchUnidade = re.search(r'\b(Unidades|Unidade|un|und)\b', titulo, re.IGNORECASE)
    matchXarope = re.search(r'\b(Xarope|Unidade|un|und)\b', titulo, re.IGNORECASE)
    if matchComprimido:
        return str("Comprimido")
    elif matchCapsula:
        return str("Cápsula")
    elif matchUnidade:
        return str("Unidade")
    elif matchXarope:
        return str("Xarope")
    else:
        return "Outros"

def extrair_massa(titulo):
    padrao = r'(\d+[\.,]?\d*)\s*(?:Mg|mgs|mg|mG|MGS|mG)'
    match = re.search(padrao, titulo, re.IGNORECASE)
    if match:
        # Convertendo o valor capturado para float
        return float(match.group(1).replace(',', '.'))
    else:
        return 0

def extrair_volume(titulo):
    padrao = r'(\d+[\.,]?\d*)\s*(?:Ml|mls|ml|mL|MLS|mL)'
    match = re.search(padrao, titulo, re.IGNORECASE)
    if match:
        # Convertendo o valor capturado para float
        return float(match.group(1).replace(',', '.'))
    else:
        return 0

def extrair_quantidades(titulo):
    padraoComprimido = r'(\d+[\.,]?\d*)\s*(?:Comprimidos|comprimido|cpds|cp|cpr)'
    padraoCapsula = r'(\d+[\.,]?\d*)\s*(?:Cápsulas|Capsula|caps|cpr)'
    padraoUnidade = r'(\d+[\.,]?\d*)\s*(?:Unidades|unidade|un)'
    padraoFrasco = r'(\d+[\.,]?\d*)\s*(?:Frascos|Frasco)'
    matchComprimido = re.search(padraoComprimido, titulo, re.IGNORECASE)
    matchCapsula = re.search(padraoCapsula, titulo, re.IGNORECASE)
    matchUnidade = re.search(padraoUnidade, titulo, re.IGNORECASE)
    matchFrasco = re.search(padraoFrasco, titulo, re.IGNORECASE)
    if matchComprimido:
        # Convertendo o valor capturado para float
        return float(matchComprimido.group(1).replace(',','.'))
    elif matchCapsula:
        return float(matchCapsula.group(1).replace(',','.'))
    elif matchUnidade:
        return float(matchUnidade.group(1).replace(',','.'))
    elif matchFrasco:
        return float(matchFrasco.group(1).replace(',','.'))
    else:
        return 0

caminho_do_arquivo_excel = 'ExtracaoDrogarias/dadosFarmaPonte/dadosXLSX/dadosFarmaPonteSaude.xlsx'
df = pd.read_excel(caminho_do_arquivo_excel)
df['Massa do Componente Ativo (em mg)'] = df['Nome do produto'].apply(extrair_massa)
df['Volume do Componente Ativo (em ml)'] = df['Nome do produto'].apply(extrair_volume)
df['Quantidade'] = df['Nome do produto'].apply(extrair_quantidades)
df['Tipo'] = df['Nome do produto'].apply(extrair_tipo)


caminhoArquivoExcel = f"teste.xlsx"
df.to_excel(caminhoArquivoExcel, index=False)