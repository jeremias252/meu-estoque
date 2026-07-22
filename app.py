import streamlit as st
import pandas as pd
import os
import time
import uuid
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Torres - ESTOQUE", page_icon="📦", layout="centered")

# --- DESIGN PREMIUM E MODO ESCURO ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(243, 128, 32, 0.3);
    }
    
    .main-title {
        text-align: center;
        font-weight: 800;
        padding-bottom: 1rem;
        margin-bottom: 2rem;
        border-bottom: 2px solid #333333;
    }
    
    /* Remove a borda padrão do expander para ficar mais "limpo" */
    .streamlit-expanderHeader {
        font-weight: bold !important;
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

ARQUIVO_ESTOQUE = "estoque_v2.csv"
ARQUIVO_HISTORICO = "historico_v2.csv"

# --- FUNÇÕES PARA CARREGAR E SALVAR DADOS ---
def carregar_dados():
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

    if os.path.exists(ARQUIVO_HISTORICO):
        df_historico = pd.read_csv(ARQUIVO_HISTORICO)
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

# ==========================================
# NOVA FUNÇÃO DE ESTOQUE (SANFONAS E CARDS)
# ==========================================
def exibir_estoque_premium(df_base, termo_busca=""):
    df_view = df_base.copy()
    
    if termo_busca:
        df_view = df_view[df_view["Modelo"].str.contains(termo_busca, case=False)]
        
    if df_view.empty:
        st.warning("Nenhum modelo encontrado com este nome ou cor.")
        return

    # Separa Nome da Cor
    def extrair_linha(nome):
        if " - " in nome: return nome.rsplit(" - ", 1)[0]
        return nome
        
    def extrair_cor(nome):
        if " - " in nome: return nome.rsplit(" - ", 1)[1]
        return "-"

    df_view['Linha'] = df_view['Modelo'].apply(extrair_linha)
    df_view['Cor'] = df_view['Modelo'].apply(extrair_cor)
    
    # Agrupa pelas famílias de modelos para ver quem tem mais quantidade
    df_totais = df_view.groupby('Linha')['Quantidade'].sum().reset_index()
    df_totais = df_totais.sort_values(by='Quantidade', ascending=False)
    
    # Renderiza cada família como uma Sanfona (Expander)
    for _, row_total in df_totais.iterrows():
        linha = row_total['Linha']
        total_linha = int(row_total['Quantidade'])
        
        # Ícone de status da família geral
        icone = "🔴" if total_linha == 0 else ("🟡" if total_linha <= 5 else "📦")
        
        with st.expander(f"{icone} {linha} — (Total: {total_linha} un.)"):
            # Filtra apenas os itens desta família
            df_linha = df_view[df_view['Linha'] == linha].sort_values(by='Cor')
            
            # Cria colunas lado a lado baseadas na quantidade de cores encontradas
            cols = st.columns(len(df_linha) if len(df_linha) > 0 else 1)
            
            for i, (_, row) in enumerate(df_linha.iterrows()):
                cor = row['Cor']
                qtd = int(row['Quantidade'])
                status = "🔴 Zerado" if qtd == 0 else ("🟡 Baixo" if qtd <= 5 else "🟢 OK")
                
                # HTML do Card (Design escuro Premium)
                card_html = f"""
                <div style="background-color: #1A1A1A; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333333; margin-bottom: 5px;">
                    <div style="color: #888888; font-size: 14px; font-weight: bold; text-transform: uppercase;">{cor}</div>
                    <div style="color: #F38020; font-size: 26px; font-weight: 900; margin: 8px 0;">{qtd}</div>
                    <div style="font-size: 12px; color: #AAAAAA;">{status}</div>
                </div>
                """
                cols[i].markdown(card_html, unsafe_allow_html=True)

df_estoque, df_historico = carregar_dados()
separadores = ["Fran", "Henrique", "Leonardo", "Patrick"]

# ==========================================
# LOGO VETORIZADA DIRETO NO CÓDIGO
# ==========================================
logo_svg = """
<div style="display: flex; justify-content: center; margin-bottom: 30px;">
    <svg width="100%" viewBox="0 0 400 350" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="350" fill="transparent" rx="12"/>
        <path d="M 320 180 L 320 50 L 50 50 L 50 300 L 320 300 L 320 250" fill="none" stroke="#ffffff" stroke-width="12" />
        <text x="75" y="150" fill="#ffffff" font-family="Arial, sans-serif" font-weight="900" font-size="70" letter-spacing="2">CAIXA</text>
        <text x="75" y="235" fill="#ffffff" font-family="Arial, sans-serif" font-weight="900" font-size="60" letter-spacing="1">TOMADA</text>
        <text x="325" y="225" fill="#ffffff" font-family="Arial, sans-serif" font-weight="bold" font-size="28">.COM</text>
        <text x="385" y="200" fill="#ffffff" font-family="Arial, sans-serif" font-size="14">®</text>
        <line x1="290" y1="260" x2="380" y2="260" stroke="#F38020" stroke-width="12" />
    </svg>
</div>
"""
st.sidebar.markdown(logo_svg, unsafe_allow_html=True)

st.sidebar.title("🔐 Acesso Seguro")
perfil = st.sidebar.radio("Nível de permissão:", ["👀 Visualizador (Equipe)", "⚙️ Controle (Apenas Fran)"])

mostrar_admin = False

if perfil == "⚙️ Controle (Apenas Fran)":
    senha = st.sidebar.text_input("Senha de acesso:", type="password")
    if senha == "fran123":
        mostrar_admin = True
    elif senha != "":
        st.sidebar.error("❌ Senha incorreta!")

# ==========================================
# TELA PRINCIPAL
# ==========================================
st.markdown("<h1 class='main-title'>📦 Torres - ESTOQUE</h1>", unsafe_allow_html=True)

if not mostrar_admin:
    st.info("👋 **Bem-vindo(a) à central de estoque Torres.** Você está no modo visualização. Solicite as retiradas de material diretamente à Fran.")
    
    busca = st.text_input("🔍 Buscar modelo ou cor (Ex: TR03 Branco)...", key="busca_equipe")
    st.divider()
    exibir_estoque_premium(df_estoque, busca)

else:
    st.sidebar.success("✅ Acesso Liberado: Fran")
    
    aba_operacao, aba_painel, aba_historico = st.tabs(["📦 Operação", "📊 Dashboard", "🕒 Histórico e Dados"])

    with aba_operacao:
        st.header("📤 Registrar Saída")
        with st.form("form_saida", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                sep = st.selectbox("1. Para quem é a peça?", [""] + separadores)
            with col2:
                lista_modelos = sorted(df_estoque["Modelo"].tolist())
                modelo = st.selectbox("2. Qual modelo?", [""] + lista_modelos)
            with col3:
                qtd = st.number_input("3. Qtd", min_value=1, value=1, step=1)
                
            submit_saida = st.form_submit_button("Confirmar Saída", type="primary", use_container_width=True)

        if submit_saida:
            if not sep or not modelo:
                st.error("⚠️ Selecione o colaborador e o modelo.")
            else:
                idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
                estoque_atual = df_estoque.at[idx, "Quantidade"]
                
                if estoque_atual < qtd:
                    st.error(f"⚠️ Saldo insuficiente! Temos apenas {estoque_atual} un. de {modelo}.")
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
                    st.toast("Saída registrada!", icon="✅")

        st.divider()

        st.header("📋 Estoque Atual")
        busca = st.text_input("🔍 Buscar modelo ou cor...", key="busca_admin")
        st.write("") # Espaçamento
        exibir_estoque_premium(df_estoque, busca)

        st.divider()

        col_entrada, col_novo = st.columns(2)
        with col_entrada:
            st.subheader("📥 Receber Material")
            with st.form("form_entrada", clear_on_submit=True):
                modelo_rep = st.selectbox("Qual modelo chegou?", [""] + sorted(df_estoque["Modelo"].tolist()))
                qtd_rep = st.number_input("Quantidade recebida", min_value=1, value=1, step=1)
                submit_entrada = st.form_submit_button("Lançar Entrada")
                
                if submit_entrada:
                    if modelo_rep:
                        idx = df_estoque[df_estoque["Modelo"] == modelo_rep].index[0]
                        df_estoque.at[idx, "Quantidade"] += qtd_rep
                        salvar_estoque(df_estoque)
                        st.success(f"✅ {qtd_rep}x {modelo_rep} em estoque!")
                        time.sleep(1)
                        st.rerun()

        with col_novo:
            st.subheader("➕ Cadastrar Produto")
            with st.form("form_novo", clear_on_submit=True):
                novo_nome = st.text_input("Nome do produto (com cor)")
                nova_qtd = st.number_input("Estoque inicial", min_value=0, value=0, step=1)
                submit_novo = st.form_submit_button("Salvar Cadastro")
                
                if submit_novo:
                    if novo_nome:
                        if novo_nome in df_estoque["Modelo"].values:
                            st.warning("Produto já cadastrado!")
                        else:
                            novo_item = pd.DataFrame([{"Modelo": novo_nome, "Quantidade": nova_qtd}])
                            df_estoque = pd.concat([df_estoque, novo_item], ignore_index=True)
                            salvar_estoque(df_estoque)
                            st.success("✅ Produto adicionado!")
                            time.sleep(1)
                            st.rerun()

    with aba_painel:
        st.header("📊 Indicadores de Estoque")
        
        col_metric1, col_metric2 = st.columns(2)
        total_pecas = int(df_estoque["Quantidade"].sum())
        itens_em_baixa = int((df_estoque["Quantidade"] <= 5).sum())
        
        col_metric1.metric("📦 Total de Peças", total_pecas)
        col_metric2.metric("⚠️ Alertas de Falta (≤ 5 un)", itens_em_baixa)
        
        st.divider()
        
        if not df_historico.empty:
            st.subheader("📈 Top 5 Mais Retirados")
            top_modelos = df_historico.groupby("Modelo")["Quantidade"].sum().sort_values(ascending=False).head(5)
            st.bar_chart(top_modelos)
            
            st.subheader("👤 Retiradas por Colaborador")
            top_separadores = df_historico.groupby("Separador")["Quantidade"].sum().sort_values(ascending=False)
            st.bar_chart(top_separadores)
        else:
            st.info("Aguardando movimentações para gerar gráficos.")

    with aba_historico:
        st.header("🕒 Histórico Recente")
        st.dataframe(df_historico.drop(columns=["ID"], errors="ignore"), use_container_width=True, hide_index=True)
        
        st.divider()
        
        st.subheader("↩️ Estornar Lançamento")
        st.caption("Caso tenha havido erro de digitação, cancele aqui e a peça voltará ao saldo.")
        
        ultimos_registros = df_historico.head(20)
        opcoes_desfazer = {}
        for _, row in ultimos_registros.iterrows():
            texto = f"{row['Data']} | {row['Separador']} | {row['Quantidade']}x {row['Modelo']}"
            opcoes_desfazer[texto] = row["ID"]
            
        selecao_desfazer = st.selectbox("Registro para cancelar:", [""] + list(opcoes_desfazer.keys()))
        
        if st.button("❌ Estornar Movimentação"):
            if selecao_desfazer:
                id_alvo = opcoes_desfazer[selecao_desfazer]
                registro_cancelado = df_historico[df_historico["ID"] == id_alvo].iloc[0]
                
                idx = df_estoque[df_estoque["Modelo"] == registro_cancelado["Modelo"]].index[0]
                df_estoque.at[idx, "Quantidade"] += registro_cancelado["Quantidade"]
                salvar_estoque(df_estoque)
                
                df_historico = df_historico[df_historico["ID"] != id_alvo]
                salvar_historico(df_historico)
                
                st.success("✅ Estorno realizado! Saldo atualizado.")
                time.sleep(1.5)
                st.rerun()
                
        st.divider()

        st.subheader("📥 Exportação de Dados")
        col_down1, col_down2 = st.columns(2)
        
        with col_down1:
            csv_estoque = df_estoque.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Planilha de Estoque",
                data=csv_estoque,
                file_name=f"estoque_{datetime.now().strftime('%d-%m-%Y')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with col_down2:
            csv_historico = df_historico.drop(columns=["ID"], errors="ignore").to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Relatório de Movimentação",
                data=csv_historico,
                file_name=f"historico_{datetime.now().strftime('%d-%m-%Y')}.csv",
                mime="text/csv",
                use_container_width=True
            )
