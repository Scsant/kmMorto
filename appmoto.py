import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import hashlib
from io import BytesIO
from openpyxl import Workbook
from github import Github
from dotenv import load_dotenv


st.markdown(
    """
    <style>
        .header-container {
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(180deg, #623B20, #2F4F4F);
        }
        .header-container img {
            max-width: 200px; /* Tamanho da imagem */
            margin-right: 10px; /* Espaçamento ao lado da imagem */
        }
        .header-container h1 {
            color: black; /* Cor do texto */
            font-size: 30px;
        }
        /* Alterar a cor de todos os rótulos */
        div[data-testid="stForm"] label,
        div[data-baseweb="block"] label {
            color: #ffffff !important; /* Cor branca para contraste */
            font-weight: bold; /* Negrito opcional */
        }

        /* Estilizar botões */
        button {
            background-color: #ffffff !important;
            color: #333333 !important;
            border: 1px solid #333333 !important;
            border-radius: 5px !important;
        }

        /* Fundo da aplicação */
        .stApp {
            background: linear-gradient(180deg, #623B20, #2F4F4F);
            color: #ffffff; /* Texto em branco para contraste */
        }
        
        /* Campos de entrada */
        input, textarea, select {
            background-color: #333333 !important;
            color: #ffffff !important;
        }
    </style>
    <div class="header-container">
        <img src="https://raw.githubusercontent.com/Scsant/vale-pedagio-app/9a8cbe3dddcdadf284f1281fd864bb84097fcb31/Bracell_logo.png" alt="Logo">
    </div>
    """,
    unsafe_allow_html=True
)

# Conteúdo da página
st.write("Logística Florestal")



# Carregar variáveis do arquivo .env
load_dotenv()

# Token do GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "Scsant/kmMorto"  # Nome do repositório

# Inicializar PyGithub
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Função para carregar os dados do GitHub
def carregar_dados():
    try:
        content = repo.get_contents("dados.json")
        return json.loads(content.decoded_content.decode("utf-8"))
    except:
        return []

# Função para salvar os dados no GitHub
def salvar_dados(dados):
    try:
        content = repo.get_contents("dados.json")
        repo.update_file(content.path, "Atualizando registros", json.dumps(dados, indent=4, ensure_ascii=False), content.sha)
    except:
        repo.create_file("dados.json", "Criando arquivo de registros", json.dumps(dados, indent=4, ensure_ascii=False))

# Função para excluir registros no GitHub
def excluir_registros():
    try:
        repo.delete_file("dados.json", "Excluindo registros", repo.get_contents("dados.json").sha)
        st.success("Todos os registros foram excluídos do GitHub!")
    except Exception as e:
        st.error(f"Erro ao excluir os registros: {e}")

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
    ["Nenhum", "Automotiva 1", "Automotiva 2", "Oficina Terceiro", "Pátio", "OT L1", "OT L2", "Teste Prático", "Socorro(Guincho)", "Desvio de Fazenda"],
    key="local_macro",
    index=["Nenhum", "Automotiva 1", "Automotiva 2", "Oficina Terceiro", "Pátio", "OT L1", "OT L2", "Teste Prático", "Socorro(Guincho)", "Desvio de Fazenda"].index(st.session_state.get("local_macro", "Nenhum"))
)
motivo = st.text_area("Motivo", key="motivo", value=st.session_state.get("motivo", ""))

# Botões
col1, col2 = st.columns(2)
salvar = col1.button("Salvar")
novo_registro = col2.button("Novo Registro")

if salvar:
    registro = {
        "Data": data.strftime("%d/%m/%Y"),
        "Data de Registro": datetime.today().strftime("%d/%m/%Y"),  # Data fixa do momento do salvamento
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
            df["Excluir"] = False

        selecionar_todos = st.checkbox("Selecionar Todos para Exclusão")
        df["Excluir"] = selecionar_todos

        # Editor de dados
        df_editado = st.data_editor(
            df,
            column_config={"Excluir": st.column_config.CheckboxColumn("Excluir")},
            use_container_width=True
        )

        # Botão para Excluir Selecionados
        if st.button("Excluir Selecionados"):
            registros_excluir = df_editado[df_editado["Excluir"]]
            if not registros_excluir.empty:
                excluir_registros()  # Limpa o arquivo no GitHub
                st.success("Todos os registros foram excluídos com sucesso no GitHub!")
                st.rerun()
            else:
                st.warning("Nenhum registro foi selecionado para exclusão.")

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
        st.warning("Nenhum registro disponível.")
