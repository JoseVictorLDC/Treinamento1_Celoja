import streamlit as st
from ExtracaoDrogarias.funcoesAuxiliares import coletaCategorias, retornaNumeroDePaginas
from ExtracaoDrogarias.farmaPonte import extracaoDeDados

st.title("Extração")

farmacia_escolhida = st.selectbox(label="Você gostaria de extrair dados de qual farmácia?", placeholder="Escolha uma farmácia...", options=["Farma Ponte", "Drogaria Minas Mais", "Farmácias São João"], index=None)

@st.experimental_dialog("Extração")
def exibeProgresso(categoria):
    print(categoria)
    st.write(f"Iniciando extração dos produtos da categoria {categoria}")
    st.write(f"url: https://www.farmaponte.com.br/{categoria}/")
    # progresso = st.progress(0)
    extracaoDeDados(categoria)
    



if farmacia_escolhida == "Farma Ponte":
    if 'categoria' not in st.session_state:
        st.session_state['categoria'] = ''

    categorias = coletaCategorias()
    st.write("Clique em uma categoria desejada.")

    nomesDasCategorias = []

    for categoria in categorias:
        nomeCategoria = categoria[1:-1].capitalize()
        numeroDePaginas = retornaNumeroDePaginas(nomeCategoria)
        # if st.button(label=f"{nomeCategoria} - {numeroDePaginas} páginas", use_container_width=True, key=nomeCategoria):
        #     st.write(st.session_state['categoria'])
        st.button(label=f"{nomeCategoria} - {numeroDePaginas} páginas", use_container_width=True, key=nomeCategoria)
        nomesDasCategorias.append(nomeCategoria)
    
    for info in st.session_state:
        if info in nomesDasCategorias and st.session_state[f"{info}"] == True:
            exibeProgresso(info.lower())


st.write(st.session_state)