import streamlit as st
from ExtracaoDrogarias.funcoesAuxiliares import coletaCategorias, retornaNumeroDePaginas
from ExtracaoDrogarias.farmaPonte import extracaoDeDados
from ExtracaoDrogarias import drogariaSaoJoao as sj

st.title("Extração")

farmacia_escolhida = st.selectbox(label="Você gostaria de extrair dados de qual farmácia?", placeholder="Escolha uma farmácia...", options=["Farma Ponte", "Drogaria Minas Mais", "Farmácias São João"], index=None)

# Dialog que abre quando o usuário escolhe a categoria para extração.
@st.experimental_dialog("Extração")
def exibeProgressoFP(categoria):
    print(categoria)
    st.write(f"Iniciando extração dos produtos da categoria {categoria}")
    st.write(f"url: https://www.farmaponte.com.br/{categoria}/")
    extracaoDeDados(categoria)

@st.experimental_dialog("Extração")
def exibeProgressoSJ():
    st.write(f"Iniciando extração dos produtos da Farmácias São João")
    st.write(f"url: https://www.saojoaofarmacias.com.br/medicamentos/")
    sj.extracaoDeDados()


# Interface para a Farma Ponte
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
            exibeProgressoFP(info.lower())


# Interface para Farmácias São João.
if farmacia_escolhida == "Farmácias São João":
    st.write(farmacia_escolhida)
    st.button(label=f"Iniciar extração", use_container_width=True, key="iniciar")
    if st.session_state["iniciar"] == True:
        exibeProgressoSJ()

# st.write(st.session_state)