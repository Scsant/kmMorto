import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import hashlib
from io import BytesIO
from openpyxl import Workbook

# Nome do arquivo JSON
arquivo_json = os.path.join(os.path.dirname(__file__), "dados.json")

# Função para carregar os dados
def carregar_dados():
    if os.path.exists(arquivo_json):
        with open(arquivo_json, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

# Função para salvar os dados
def salvar_dados(dados):
    with open(arquivo_json, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4, ensure_ascii=False)

# Função para verificar duplicatas
def verificar_duplicata(novo_registro):
    dados = carregar_dados()
    for registro in dados:
        if registro == novo_registro:  # Comparar registros completos
            return True
    return False

# Função para verificar senha
def verificar_senha(senha_input, senha_armazenada):
    senha_hash = hashlib.sha256(senha_input.encode()).hexdigest()
    return senha_hash == senha_armazenada

# Inicialização das chaves no session_state
if "limpar_form" not in st.session_state:
    st.session_state.limpar_form = False

# Senha dos analistas
senha_armazenada = hashlib.sha256("analista123".encode()).hexdigest()  # Senha: analista123

# Formulário principal
st.subheader("Inserir Registro de KM Morto")

# Resetar os valores ao clicar em "Novo Registro"
if st.session_state.limpar_form:
    st.session_state.data = datetime.today()
    st.session_state.nome = ""
    st.session_state.btf = 0
    st.session_state.frota = 0
    st.session_state.distancia = 0.0
    st.session_state.local_macro = "Nenhum"
    st.session_state.motivo = ""
    st.session_state.limpar_form = False

# Definir valores padrão nos campos usando session_state
data = st.date_input("Data", key="data", value=st.session_state.get("data", datetime.today()))
nome = st.text_input("Nome", key="nome", value=st.session_state.get("nome", ""))
btf = st.number_input("BTF", min_value=0, step=1, key="btf", value=st.session_state.get("btf", 0))
frota = st.number_input("Frota", min_value=0, step=1, key="frota", value=st.session_state.get("frota", 0))
distancia = st.number_input("Distância (KM)", min_value=0.0, step=0.1, key="distancia", value=st.session_state.get("distancia", 0.0))
local_macro = st.selectbox(
    "Local Macro",
    ["Nenhum", "Automotiva 1", "Automotiva 2", "Oficina Terceiro", "Pátio", "OT L1", "OT L2", "Teste Prático", "Socorro(Guincho)"],
    key="local_macro",
    index=["Nenhum", "Automotiva 1", "Automotiva 2", "Oficina Terceiro", "Pátio", "OT L1", "OT L2", "Teste Prático", "Socorro(Guincho)"].index(st.session_state.get("local_macro", "Nenhum"))
)
motivo = st.text_area("Motivo", key="motivo", value=st.session_state.get("motivo", ""))

# Botões
col1, col2 = st.columns(2)
salvar = col1.button("Salvar")
novo_registro = col2.button("Novo Registro")

if salvar:
    registro = {
        "Data": data.strftime("%d/%m/%Y"),
        "Nome": nome,
        "BTF": btf,
        "Frota": frota,
        "Distância": distancia,
        "Local Macro": local_macro,
        "Motivo": motivo
    }
    if verificar_duplicata(registro):
        st.warning("Erro: Registro duplicado!")
    else:
        salvar_dados(carregar_dados() + [registro])
        st.success("Registro salvo com sucesso!")

if novo_registro:
    st.session_state.limpar_form = True
    st.rerun()


# Área Restrita dos Analistas
st.subheader("Área Restrita para Analistas")

senha_input = st.text_input("Digite a senha para acessar a área de analistas", type="password")
if st.button("Verificar Senha"):
    if verificar_senha(senha_input, senha_armazenada):
        st.session_state.senha_autorizada = True
        st.success("Acesso autorizado!")
    else:
        st.error("Senha incorreta!")

if st.session_state.get("senha_autorizada", False):
    st.subheader("Gerenciar Registros")

    # Carregar dados no DataFrame
    df = pd.DataFrame(carregar_dados())
    if not df.empty:
        if "Excluir" not in df.columns:
            df["Excluir"] = False  # Adiciona coluna Excluir se não existir

        # Checkbox "Selecionar Todos"
        selecionar_todos = st.checkbox("Selecionar Todos para Exclusão")

        # Atualizar coluna "Excluir" com base no checkbox principal
        if selecionar_todos:
            df["Excluir"] = True
        else:
            df["Excluir"] = False  # Resetar para False se desmarcado

        # Editor de dados
        df_editado = st.data_editor(
            df,
            column_config={"Excluir": st.column_config.CheckboxColumn("Excluir")},
            use_container_width=True
        )

        # Botão para Excluir Selecionados
        if st.button("Excluir Selecionados"):
            registros_excluir = df_editado[df_editado["Excluir"] == True]
            if not registros_excluir.empty:
                df_filtrado = df_editado[~df_editado["Excluir"]].drop(columns=["Excluir"])
                salvar_dados(df_filtrado.to_dict(orient="records"))
                st.success("Registros excluídos com sucesso!")
                st.rerun()
            else:
                st.warning("Nenhum registro foi selecionado para exclusão.")
    else:
        st.warning("Nenhum registro disponível.")

        
        # Botão para baixar dados
    if not df.drop(columns=["Excluir"], errors="ignore").empty:
        buffer = BytesIO()
        df.drop(columns=["Excluir"], errors="ignore").to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        st.download_button(
            label="Baixar Registros em Excel",
            data=buffer,
            file_name="registros_km_morto.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.warning("Nenhum dado disponível para download.")
