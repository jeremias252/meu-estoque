import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Estoque", page_icon="📦", layout="centered")

# Mudei os nomes dos arquivos para v2, assim ele cria uma lista nova do zero 
# com as cores e não dá erro misturando com os testes antigos.
ARQUIVO_ESTOQUE = "estoque_v2.csv"
ARQUIVO_HISTORICO = "historico_v2.csv"

# --- FUNÇÕES PARA CARREGAR E SALVAR DADOS ---
def carregar_dados():
    # Carrega ou cria o estoque
    if os.path.exists(ARQUIVO_ESTOQUE):
        df_estoque = pd.read_csv(ARQUIVO_ESTOQUE)
    else:
        # Sua lista base de modelos
        modelos_base = [
            "TR03", "TR03W", "TR03A", "TR03AW", "TR02A", "TR02AW",
            "TR03AW COM DUO", "TR03A COM DUO", "TR03A TOPO EM PEDRA 2,5 mm",
            "TR03A TOPO EM PEDRA 4 mm", "TR03A TOPO EM PEDRA 2,5 mm TOM DEDICADA",
            "TR03 2TM + 1VER", "TR03 4mm", "TR03A 2 TOM +VM", "TR02AW 1TOM + VM",
            "TR03AW 2 TOM + VM", "TR02A 4mm²", "TR02AW 4mm"
        ]
        cores = ["Branco", "Preto", "Cinza"]
        
        # O Python cruza automaticamente cada modelo com as 3 cores
        itens = [f"{modelo} - {cor}" for modelo in modelos_base for cor in cores]
        
        df_estoque = pd.DataFrame({"Modelo": itens, "Quantidade": 0})
        df_estoque.to_csv(ARQUIVO_ESTOQUE, index=False)

    # Carrega ou cria o histórico
    if os.path.exists(ARQUIVO_HISTORICO):
        df_historico = pd.read_csv(ARQUIVO_HISTORICO)
    else:
        df_historico = pd.DataFrame(columns=["Data", "Separador", "Modelo", "Quantidade"])
        df_historico.to_csv(ARQUIVO_HISTORICO, index=False)

    return df_estoque, df_historico

def salvar_estoque(df):
    df.to_csv(ARQUIVO_ESTOQUE, index=False)

def salvar_historico(df):
    df.to_csv(ARQUIVO_HISTORICO, index=False)

# Inicializa os dados
df_estoque, df_historico = carregar_dados()
separadores = ["Fran", "Henrique", "Leonardo", "Patrick"]

# --- CABEÇALHO ---
st.title("📦 Meu Estoque")

# --- 1. REGISTRAR SAÍDA ---
st.header("📤 Registrar Saída")
with st.container(border=True):
    col1, col2, col3 = st.columns([2, 3, 1])
    
    with col1:
        sep = st.selectbox("1. Quem está pegando?", [""] + separadores)
    with col2:
        # A lista aqui agora tem 54 opções (Modelo + Cor)
        modelo = st.selectbox("2. Qual modelo?", [""] + df_estoque["Modelo"].tolist())
    with col3:
        qtd = st.number_input("3. Qtd", min_value=1, value=1, step=1)
        
    if st.button("Confirmar Retirada", type="primary", use_container_width=True):
        if not sep or not modelo:
            st.error("⚠️ Preencha quem está pegando e o modelo.")
        else:
            idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
            estoque_atual = df_estoque.at[idx, "Quantidade"]
            
            if estoque_atual < qtd:
                st.error(f"⚠️ Estoque insuficiente! Você tentou tirar {qtd}, mas só temos {estoque_atual} de {modelo}.")
            else:
                # Atualiza estoque
                df_estoque.at[idx, "Quantidade"] -= qtd
                salvar_estoque(df_estoque)
                
                # Registra histórico
                novo_registro = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Separador": sep,
                    "Modelo": modelo,
                    "Quantidade": qtd
                }])
                df_historico = pd.concat([novo_registro, df_historico], ignore_index=True)
                df_historico = df_historico.head(100) 
                salvar_historico(df_historico)
                
                st.success(f"✅ Retirada registrada: {sep} pegou {qtd}x {modelo}.")
                st.rerun()

# --- 2. ESTOQUE ATUAL E BUSCA ---
st.header("📋 Estoque Atual")
busca = st.text_input("🔍 Pesquisar modelo ou cor...", placeholder="Ex: TR03 Preto...")

df_view = df_estoque.copy()
if busca:
    df_view = df_view[df_view["Modelo"].str.contains(busca, case=False)]

# Função para pintar a linha de vermelho se tiver 5 ou menos
def destacar_estoque_baixo(row):
    if row['Quantidade'] <= 5:
        return ['background-color: rgba(239, 68, 68, 0.3)'] * len(row)
    return [''] * len(row)

st.dataframe(
    df_view.style.apply(destacar_estoque_baixo, axis=1), 
    use_container_width=True, 
    hide_index=True
)

# --- 3. ENTRADA DE MATERIAL E NOVOS MODELOS ---
col_entrada, col_novo = st.columns(2)

with col_entrada:
    st.subheader("📥 Repor Estoque")
    with st.container(border=True):
        modelo_rep = st.selectbox("Modelo para repor", [""] + df_estoque["Modelo"].tolist())
        qtd_rep = st.number_input("Quantidade recebida", min_value=1, value=1, step=1)
        if st.button("Adicionar ao Estoque"):
            if modelo_rep:
                idx = df_estoque[df_estoque["Modelo"] == modelo_rep].index[0]
                df_estoque.at[idx, "Quantidade"] += qtd_rep
                salvar_estoque(df_estoque)
                st.success("Estoque atualizado!")
                st.rerun()

with col_novo:
    st.subheader("➕ Cadastrar Novo")
    with st.container(border=True):
        novo_nome = st.text_input("Nome do novo modelo (com a cor)")
        nova_qtd = st.number_input("Estoque inicial", min_value=0, value=0, step=1)
        if st.button("Cadastrar Modelo"):
            if novo_nome:
                if novo_nome in df_estoque["Modelo"].values:
                    st.warning("Este modelo já existe!")
                else:
                    novo_item = pd.DataFrame([{"Modelo": novo_nome, "Quantidade": nova_qtd}])
                    df_estoque = pd.concat([df_estoque, novo_item], ignore_index=True)
                    salvar_estoque(df_estoque)
                    st.success("Modelo cadastrado!")
                    st.rerun()

# --- 4. HISTÓRICO ---
st.header("🕒 Histórico de Retiradas")
st.dataframe(df_historico, use_container_width=True, hide_index=True)
