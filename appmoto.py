import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import hashlib
from io import BytesIO

# Nome do arquivo JSON
arquivo_json = "dados.json"

# Função para carregar os dados do JSON
def carregar_dados():
    if os.path.exists(arquivo_json):
        with open(arquivo_json, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

# Função para salvar os dados no JSON
def salvar_dados(dados):
    with open(arquivo_json, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4, ensure_ascii=False)

# Função para adicionar um novo registro
def adicionar_registro(data, btf, frota, distancia, local_macro, motivo):
    # Carregar os dados existentes
    dados = carregar_dados()
    
    # Adicionar o novo registro
    dados.append({
        "Data": data.strftime("%d/%m/%Y"),  # Salvar no formato brasileiro
        "BTF": btf,
        "Frota": str(frota),
        "Distância": distancia,
        "Local Macro": local_macro,
        "Motivo": motivo
        
    })
    
    # Salvar os dados no JSON
    salvar_dados(dados)

# Função para converter os dados para DataFrame
def dados_para_dataframe():
    dados = carregar_dados()
    df = pd.DataFrame(dados)
    
    # Adicionar coluna "Excluir" para checkbox, se não existir
    if not "Excluir" in df.columns:
        df["Excluir"] = False
    return df

# Função para verificar senha
def verificar_senha(senha_input, senha_armazenada):
    senha_hash = hashlib.sha256(senha_input.encode()).hexdigest()
    return senha_hash == senha_armazenada

# Senha dos analistas (armazenada como hash SHA-256)
senha_armazenada = hashlib.sha256("analista123".encode()).hexdigest()  # Senha: analista123

# Página principal do Streamlit
st.title("Registro de KM Morto")

# Formulário para motoristas
with st.form("form_km_morto"):
    st.subheader("Inserir Registro de KM Morto")
    data = st.date_input("Data")  # Input de data (retorna um objeto datetime.date)
    btf = st.number_input("BTF", min_value=0, step=1)
    frota = st.number_input("Frota", min_value=0, step=1)
    distancia = st.number_input("Distância (KM)", min_value=0.0, format="%.1f", step=0.1)
    # Lista suspensa para "Local Macro"
    local_macro = st.selectbox(
        "Local Macro",
        options=[
            "Nenhum",
            "Automotiva 1",
            "Oficina Terceiro",
            "Automotiva 2",
            "Pátio",
            "OT L1",
            "OT L2",
            "Socorro(Guincho)"
        ],
        index=0  # Seleciona "Nenhum" como valor padrão
    )
    motivo = st.text_area("Motivo")

    submit = st.form_submit_button("Salvar")

    if submit:
        if motivo:
            adicionar_registro(data, btf, frota, distancia, local_macro, motivo)
            st.success(f"Registro salvo com sucesso! Data: {data.strftime('%d/%m/%Y')}")
        else:
            st.error("Por favor, preencha o motivo.")

# Área restrita para analistas
st.subheader("Área Restrita para Analistas")

# Campo de senha
senha_input = st.text_input("Digite a senha para acessar a área de analistas", type="password")

if senha_input:
    if verificar_senha(senha_input, senha_armazenada):
        st.success("Acesso autorizado!")

        # Carregar os dados para exibição
        df = dados_para_dataframe()

        if not df.empty:
            # Exibir os dados em um editor para os analistas
            st.subheader("Editar ou Excluir Registros")
            st.write("Selecione as linhas que deseja excluir marcando os checkboxes abaixo.")

            # Usar st.data_editor para permitir edição de checkbox
            df_editado = st.data_editor(
                df,
                column_config={
                    "Excluir": st.column_config.CheckboxColumn("Excluir"),  # Configuração para checkbox
                },
                use_container_width=True,
            )

            # Botão de exclusão
            if st.button("Excluir Selecionados"):
                # Filtrar os dados para manter apenas os registros não marcados para exclusão
                df_filtrado = df_editado[~df_editado["Excluir"]].drop(columns=["Excluir"])

                # Salvar os dados atualizados no JSON
                salvar_dados(df_filtrado.to_dict(orient="records"))
                st.success("Registros excluídos com sucesso!")
                df = df_filtrado  # Atualizar a tabela exibida

            # Botão para baixar os registros como Excel
            st.subheader("Baixar Dados")
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
            st.warning("Nenhum registro encontrado ainda.")
    else:
        st.error("Senha incorreta.")
