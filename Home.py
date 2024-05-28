import streamlit as st

st.set_page_config(page_title="Celoja", page_icon="imagens/Logo_Celoja.png", layout="centered", initial_sidebar_state="auto", menu_items=None)

with st.sidebar:
  st.image("imagens/Logo_Celoja.png", width=150)
st.title("Home")
st.write("Interface para extração dos produtos.")
