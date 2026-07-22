import streamlit as st
import pandas as pd
import os
import time
import uuid
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Estoque", page_icon="📦", layout="centered")

ARQUIVO_ESTOQUE = "estoque_v2.csv"
ARQUIVO_HISTORICO = "historico_v2.csv"

# --- FUNÇÕES PARA CARREGAR E SALVAR DADOS ---
def carregar_dados():
    # ESTOQUE
    if os.path.exists(ARQUIVO_ESTOQUE):
        df_estoque = pd.read_csv(ARQUIVO_ESTOQUE)
    else:
        modelos_base = [
            "TR03", "TR03W", "TR03A", "TR03AW", "TR02A", "TR02AW",
            "TR03AW COM DUO", "TR03A COM DUO", "TR03A TOPO EM PEDRA 2,5 mm",
            "TR03A TOPO EM PEDRA 4 mm", "TR03A TOPO EM PEDRA 2,5 mm TOM DEDICADA",
            "TR03 2TM + 1VER", "TR03 4mm", "TR03A 2 TOM +VM", "TR02AW 1TOM + VM",
            "TR03AW 2 TOM + VM", "TR02A 4mm²", "TR02AW 4mm"
        ]
        cores = ["Branco", "Preto", "Cinza"]
        itens = [f"{modelo} - {cor}" for modelo in modelos_base for cor in cores]
        df_estoque = pd.DataFrame({"Modelo": itens, "Quantidade": 0})
        df_estoque.to_csv(ARQUIVO_ESTOQUE, index=False)

    # HISTÓRICO
    if os.path.exists(ARQUIVO_HISTORICO):
        df_historico = pd.read_csv(ARQUIVO_HISTORICO)
        # Garante que as planilhas antigas ganhem a coluna de ID para podermos "desfazer" ações
        if "ID" not in df_historico.columns:
            df_historico["ID"] = [str(uuid.uuid4()) for _ in range(len(df_historico))]
            df_historico.to_csv(ARQUIVO_HISTORICO, index=False)
    else:
        df_historico = pd.DataFrame(columns=["ID", "Data", "Separador", "Modelo", "Quantidade"])
        df_historico.to_csv(ARQUIVO_HISTORICO, index=False)

    return df_estoque, df_historico

def salvar_estoque(df):
    df.to_csv(ARQUIVO_ESTOQUE, index=False)

def salvar_historico(df):
    df.to_csv(ARQUIVO_HISTORICO, index=False)

df_estoque, df_historico = carregar_dados()
separadores = ["Fran", "Henrique", "Leonardo", "Patrick"]

st.title("📦 Meu Estoque")

# --- CRIAÇÃO DAS ABAS ---
aba_operacao, aba_dashboard, aba_historico = st.tabs(["📦 Operação", "📊 Dashboard", "🕒 Histórico & Dados"])


# ==========================================
# ABA 1: OPERAÇÃO DO DIA A DIA
# ==========================================
with aba_operacao:
    st.header("📤 Registrar Saída")
    with st.form("form_saida", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            sep = st.selectbox("1. Quem está pegando?", [""] + separadores)
        with col2:
            modelo = st.selectbox("2. Qual modelo?", [""] + df_estoque["Modelo"].tolist())
        with col3:
            qtd = st.number_input("3. Qtd", min_value=1, value=1, step=1)
            
        submit_saida = st.form_submit_button("Confirmar Retirada", type="primary", use_container_width=True)

    if submit_saida:
        if not sep or not modelo:
            st.error("⚠️ Preencha quem está pegando e o modelo.")
        else:
            idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
            estoque_atual = df_estoque.at[idx, "Quantidade"]
            
            if estoque_atual < qtd:
                st.error(f"⚠️ Estoque insuficiente! Só temos {estoque_atual} de {modelo}.")
            else:
                df_estoque.at[idx, "Quantidade"] -= qtd
                salvar_estoque(df_estoque)
                
                novo_registro = pd.DataFrame([{
                    "ID": str(uuid.uuid4()),
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Separador": sep,
                    "Modelo": modelo,
                    "Quantidade": qtd
                }])
                df_historico = pd.concat([novo_registro, df_historico], ignore_index=True).head(500)
                salvar_historico(df_historico)
                
                st.success(f"✅ SUCESSO: {qtd}x {modelo} entregues para {sep}!")
                st.toast(f"Retirada de {sep} salva!", icon="✅")

    st.divider()

    st.header("📋 Estoque Atual")
    busca = st.text_input("🔍 Pesquisar modelo ou cor...", placeholder="Ex: TR03 Preto...")

    df_view = df_estoque.copy()
    if busca:
        df_view = df_view[df_view["Modelo"].str.contains(busca, case=False)]

    def destacar_estoque_baixo(row):
        if row['Quantidade'] <= 5:
            return ['background-color: rgba(239, 68, 68, 0.3)'] * len(row)
        return [''] * len(row)

    st.dataframe(df_view.style.apply(destacar_estoque_baixo, axis=1), use_container_width=True, hide_index=True)

    st.divider()

    col_entrada, col_novo = st.columns(2)
    with col_entrada:
        st.subheader("📥 Receber Material")
        with st.form("form_entrada", clear_on_submit=True):
            modelo_rep = st.selectbox("Qual modelo chegou?", [""] + df_estoque["Modelo"].tolist())
            qtd_rep = st.number_input("Quantidade recebida", min_value=1, value=1, step=1)
            submit_entrada = st.form_submit_button("Lançar no Estoque")
            
            if submit_entrada:
                if modelo_rep:
                    idx = df_estoque[df_estoque["Modelo"] == modelo_rep].index[0]
                    df_estoque.at[idx, "Quantidade"] += qtd_rep
                    salvar_estoque(df_estoque)
                    st.success(f"✅ {qtd_rep}x {modelo_rep} adicionados!")
                    time.sleep(1)
                    st.rerun()

    with col_novo:
        st.subheader("➕ Novo Modelo")
        with st.form("form_novo", clear_on_submit=True):
            novo_nome = st.text_input("Nome do modelo (com a cor)")
            nova_qtd = st.number_input("Estoque inicial", min_value=0, value=0, step=1)
            submit_novo = st.form_submit_button("Cadastrar Modelo")
            
            if submit_novo:
                if novo_nome:
                    if novo_nome in df_estoque["Modelo"].values:
                        st.warning("Este modelo já existe!")
                    else:
                        novo_item = pd.DataFrame([{"Modelo": novo_nome, "Quantidade": nova_qtd}])
                        df_estoque = pd.concat([df_estoque, novo_item], ignore_index=True)
                        salvar_estoque(df_estoque)
                        st.success("✅ Modelo cadastrado!")
                        time.sleep(1)
                        st.rerun()


# ==========================================
# ABA 2: DASHBOARD E GRÁFICOS
# ==========================================
with aba_dashboard:
    st.header("📊 Resumo do Sistema")
    
    col_metric1, col_metric2 = st.columns(2)
    total_pecas = int(df_estoque["Quantidade"].sum())
    itens_em_baixa = int((df_estoque["Quantidade"] <= 5).sum())
    
    col_metric1.metric("📦 Total de Peças Físicas", total_pecas)
    col_metric2.metric("⚠️ Modelos no Final (5 ou menos)", itens_em_baixa)
    
    st.divider()
    
    if not df_historico.empty:
        st.subheader("📈 Top 5 Modelos Mais Retirados")
        # Soma as quantidades por modelo e pega os 5 maiores
        top_modelos = df_historico.groupby("Modelo")["Quantidade"].sum().sort_values(ascending=False).head(5)
        st.bar_chart(top_modelos)
        
        st.subheader("👤 Quem mais retirou peças?")
        # Soma as quantidades por separador
        top_separadores = df_historico.groupby("Separador")["Quantidade"].sum().sort_values(ascending=False)
        st.bar_chart(top_separadores)
    else:
        st.info("Nenhuma retirada registrada ainda para gerar gráficos.")


# ==========================================
# ABA 3: HISTÓRICO, DESFAZER E EXPORTAÇÃO
# ==========================================
with aba_historico:
    st.header("🕒 Histórico de Retiradas")
    
    # Mostra a tabela sem a coluna técnica de ID
    st.dataframe(df_historico.drop(columns=["ID"], errors="ignore"), use_container_width=True, hide_index=True)
    
    st.divider()
    
    # --- ÁREA PARA DESFAZER ERROS ---
    st.subheader("↩️ Cancelar um Lançamento Errado")
    st.caption("Se alguém lançou algo errado, selecione abaixo para desfazer. A peça voltará para o estoque automaticamente.")
    
    # Pega as últimas 20 retiradas para facilitar
    ultimos_registros = df_historico.head(20)
    opcoes_desfazer = {}
    for _, row in ultimos_registros.iterrows():
        texto = f"{row['Data']} | {row['Separador']} retirou {row['Quantidade']}x {row['Modelo']}"
        opcoes_desfazer[texto] = row["ID"]
        
    selecao_desfazer = st.selectbox("Selecione o registro para cancelar:", [""] + list(opcoes_desfazer.keys()))
    
    if st.button("❌ Desfazer e Devolver ao Estoque"):
        if selecao_desfazer:
            id_alvo = opcoes_desfazer[selecao_desfazer]
            registro_cancelado = df_historico[df_historico["ID"] == id_alvo].iloc[0]
            
            # Devolve ao estoque
            idx = df_estoque[df_estoque["Modelo"] == registro_cancelado["Modelo"]].index[0]
            df_estoque.at[idx, "Quantidade"] += registro_cancelado["Quantidade"]
            salvar_estoque(df_estoque)
            
            # Remove do histórico
            df_historico = df_historico[df_historico["ID"] != id_alvo]
            salvar_historico(df_historico)
            
            st.success("Lançamento cancelado! As peças voltaram para o estoque.")
            time.sleep(1.5)
            st.rerun()
            
    st.divider()

    # --- ÁREA DE EXPORTAÇÃO (DOWNLOAD) ---
    st.subheader("📥 Exportar Dados para Excel/CSV")
    st.caption("Baixe as planilhas para abrir no Excel.")
    
    col_down1, col_down2 = st.columns(2)
    
    with col_down1:
        # Prepara o arquivo de estoque
        csv_estoque = df_estoque.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar Planilha de Estoque Atual",
            data=csv_estoque,
            file_name=f"estoque_{datetime.now().strftime('%d-%m-%Y')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col_down2:
        # Prepara o arquivo de histórico
        csv_historico = df_historico.drop(columns=["ID"], errors="ignore").to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar Relatório de Retiradas",
            data=csv_historico,
            file_name=f"historico_{datetime.now().strftime('%d-%m-%Y')}.csv",
            mime="text/csv",
            use_container_width=True
        )
