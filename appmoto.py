import streamlit as st
import pandas as pd
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import hashlib
from io import BytesIO
import sendgrid
from sendgrid.helpers.mail import Mail

# Nome do arquivo JSON (salvo no mesmo diretório do projeto)
arquivo_json = os.path.join(os.path.dirname(__file__), "dados.json")

# Função para carregar os dados do JSON
def carregar_dados():
    if os.path.exists(arquivo_json):
        with open(arquivo_json, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        # Criar o arquivo JSON vazio na primeira execução
        with open(arquivo_json, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4, ensure_ascii=False)
        return []

# Função para salvar os dados no JSON
def salvar_dados(dados):
    with open(arquivo_json, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4, ensure_ascii=False)


def enviar_email(dados):
    sg = sendgrid.SendGridAPIClient(api_key="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")
    mensagem = Mail(
        from_email="scsantos492@gmail.com",  # Substitua pelo seu email
        to_emails="scsantos492@gmail.com",  # Email de destino
        subject="Novo Apontamento de KM Morto",
        plain_text_content=f"""
        Novo apontamento registrado:
        - Data: {dados['Data']}
        - Nome:{dados['Nome']}
        - BTF: {dados['BTF']}
        - Frota: {dados['Frota']}
        - Distância: {dados['Distância']} KM
        - Local Macro: {dados['Local Macro']}
        - Motivo: {dados['Motivo']} 
        """
    )
    try:
        response = sg.send(mensagem)
        st.success(f"Email enviado com sucesso! Status: {response.status_code}")
    except Exception as e:
        st.error(f"Erro ao enviar email: {e}")


# Função para adicionar um novo registro
def adicionar_registro(data, nome, btf, frota, distancia, local_macro, motivo):
    # Carregar os dados existentes
    dados = carregar_dados()
    
    # Adicionar o novo registro
    novo_registro = {
        "Data": data.strftime("%d/%m/%Y"),  # Salvar no formato brasileiro
        "Nome": nome,
        "BTF": btf,
        "Frota": str(frota),
        "Distância": distancia,
        "Motivo": motivo,
        "Local Macro": local_macro
        
    }
    dados.append(novo_registro)
    
    # Salvar os dados no JSON
    salvar_dados(dados)
    
    # Enviar email com os dados do novo registro
    enviar_email(novo_registro)

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
    nome = st.text_input("Nome")
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
            "Teste Prático",
            "Socorro(Guincho)"
        ],
        index=0  # Seleciona "Nenhum" como valor padrão
    )
    motivo = st.text_area("Motivo")

    submit = st.form_submit_button("Salvar")

    if submit:
        if motivo:
            adicionar_registro(data, nome, btf, frota, distancia, local_macro, motivo)
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
