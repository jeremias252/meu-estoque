import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

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
        margin-bottom: 1rem;
        border-bottom: 2px solid #333333;
    }
    
    .alert-box {
        background-color: #3f0e0e;
        border-left: 5px solid #ef4444;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
        color: #fca5a5;
    }
    </style>
    """, unsafe_allow_html=True)

# COLOQUE AQUI O LINK DA SUA PLANILHA "Torres - Estoque" DO GOOGLE DRIVE
URL_PLANILHA = "COLE_AQUI_O_LINK_DA_SUA_PLANILHA_TORRES"

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        df_estoque = conn.read(spreadsheet=URL_PLANILHA, worksheet="Estoque")
    except:
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
        conn.update(spreadsheet=URL_PLANILHA, worksheet="Estoque", data=df_estoque)

    try:
        df_historico = conn.read(spreadsheet=URL_PLANILHA, worksheet="Historico")
    except:
        df_historico = pd.DataFrame(columns=["ID", "Data", "Ação", "Separador", "Modelo", "Quantidade"])
        conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=df_historico)

    return df_estoque, df_historico

def salvar_estoque(df):
    conn.update(spreadsheet=URL_PLANILHA, worksheet="Estoque", data=df)

def salvar_historico(df):
    conn.update(spreadsheet=URL_PLANILHA, worksheet="Historico", data=df)

# ==========================================
# EXIBIÇÃO DE ESTOQUE
# ==========================================
def exibir_estoque_premium(df_base, termo_busca=""):
    df_view = df_base.copy()
    if termo_busca:
        df_view = df_view[df_view["Modelo"].str.contains(termo_busca, case=False)]
        
    if df_view.empty:
        st.warning("Nenhum modelo encontrado com este nome ou cor.")
        return

    def extrair_linha(nome):
        if " - " in nome: return nome.rsplit(" - ", 1)[0]
        return nome
        
    def extrair_cor(nome):
        if " - " in nome: return nome.rsplit(" - ", 1)[1]
        return "Padrão"

    df_view['Linha'] = df_view['Modelo'].apply(extrair_linha)
    df_view['Cor'] = df_view['Modelo'].apply(extrair_cor)
    
    df_totais = df_view.groupby('Linha')['Quantidade'].sum().reset_index()
    df_totais = df_totais.sort_values(by='Quantidade', ascending=False)
    
    for _, row_total in df_totais.iterrows():
        linha = row_total['Linha']
        total_linha = int(row_total['Quantidade'])
        icone = "🔴" if total_linha == 0 else ("🟡" if total_linha <= 5 else "📦")
        
        with st.expander(f"{icone} {linha} — (Total: {total_linha} un.)"):
            df_linha = df_view[df_view['Linha'] == linha].sort_values(by='Cor')
            cols = st.columns(len(df_linha) if len(df_linha) > 0 else 1)
            
            for i, (_, row) in enumerate(df_linha.iterrows()):
                cor = row['Cor']
                qtd = int(row['Quantidade'])
                status = "🔴 Zerado" if qtd == 0 else ("🟡 Baixo" if qtd <= 5 else "🟢 OK")
                
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

# --- LOGO SVG ---
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

# --- CONTROLE DE ACESSO ---
st.sidebar.title("🔐 Acesso Seguro")
perfil = st.sidebar.radio("Nível de permissão:", ["👀 Visualizador (Equipe)", "⚙️ Controle (Fran)", "👑 Coordenador"])

acesso_fran = False
acesso_coord = False

if perfil == "⚙️ Controle (Fran)":
    senha = st.sidebar.text_input("Senha da Fran:", type="password")
    if senha == "fran123": acesso_fran = True
    elif senha != "": st.sidebar.error("❌ Senha incorreta!")

elif perfil == "👑 Coordenador":
    senha = st.sidebar.text_input("Senha do Coordenador:", type="password")
    if senha == "coord123": acesso_coord = True
    elif senha != "": st.sidebar.error("❌ Senha incorreta!")

# --- TELA PRINCIPAL ---
st.markdown("<h1 class='main-title'>📦 Torres - ESTOQUE</h1>", unsafe_allow_html=True)

# ALERTA DE ESTOQUE CRÍTICO
zerados = df_estoque[df_estoque["Quantidade"] == 0]["Modelo"].tolist()
if zerados:
    st.markdown(f"<div class='alert-box'>🚨 <b>ATENÇÃO CRÍTICA:</b> Há {len(zerados)} modelos com estoque ZERADO!</div>", unsafe_allow_html=True)

if not (acesso_fran or acesso_coord):
    st.info("👋 Modo Visualização. Solicite retiradas diretamente à Fran.")
    busca = st.text_input("🔍 Buscar modelo...", key="busca_equipe")
    st.divider()
    exibir_estoque_premium(df_estoque, busca)

else:
    abas_nomes = ["📦 Operação", "📊 Dashboard", "🕒 Histórico", "👑 Fechamento"] if acesso_coord else ["📦 Operação", "📊 Dashboard", "🕒 Histórico"]
    abas = st.tabs(abas_nomes)

    with abas[0]: # OPERAÇÃO
        st.header("📤 Registrar Saída")
        with st.form("form_saida", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1: sep = st.selectbox("1. Colaborador", [""] + separadores)
            with col2: modelo = st.selectbox("2. Modelo", [""] + sorted(df_estoque["Modelo"].tolist()))
            with col3: qtd = st.number_input("3. Qtd", min_value=1, value=1)
            submit_saida = st.form_submit_button("Confirmar Saída", type="primary", use_container_width=True)

        if submit_saida:
            if not sep or not modelo: st.error("⚠️ Preencha os campos.")
            else:
                idx = df_estoque[df_estoque["Modelo"] == modelo].index[0]
                estoque_atual = df_estoque.at[idx, "Quantidade"]
                if estoque_atual < qtd:
                    st.error(f"⚠️ Saldo insuficiente! Temos apenas {estoque_atual} un.")
                else:
                    df_estoque.at[idx, "Quantidade"] -= qtd
                    salvar_estoque(df_estoque)
                    novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": "Saída", "Separador": sep, "Modelo": modelo, "Quantidade": qtd}])
                    df_historico = pd.concat([novo, df_historico], ignore_index=True)
                    salvar_historico(df_historico)
                    st.success(f"✅ Registrado com sucesso!")
                    st.rerun()

        st.divider()
        st.header("📋 Estoque Atual")
        busca = st.text_input("🔍 Buscar modelo...", key="busca_admin")
        exibir_estoque_premium(df_estoque, busca)

        st.divider()
        st.header("📥 Receber Material (Produção)")
        with st.form("form_entrada", clear_on_submit=True):
            col1_in, col2_in, col3_in = st.columns([2, 3, 1])
            with col1_in: quem_fez = st.selectbox("1. Quem produziu?", [""] + separadores)
            with col2_in: modelo_rep = st.selectbox("2. Modelo", [""] + sorted(df_estoque["Modelo"].tolist()))
            with col3_in: qtd_rep = st.number_input("3. Qtd", min_value=1, value=1)
            submit_entrada = st.form_submit_button("Lançar Entrada")
            
            if submit_entrada:
                if not modelo_rep or not quem_fez: st.error("⚠️ Preencha os campos.")
                else:
                    idx = df_estoque[df_estoque["Modelo"] == modelo_rep].index[0]
                    df_estoque.at[idx, "Quantidade"] += qtd_rep
                    salvar_estoque(df_estoque)
                    novo = pd.DataFrame([{"ID": str(uuid.uuid4()), "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ação": "Entrada", "Separador": quem_fez, "Modelo": modelo_rep, "Quantidade": qtd_rep}])
                    df_historico = pd.concat([novo, df_historico], ignore_index=True)
                    salvar_historico(df_historico)
                    st.success("✅ Entrada Lançada!")
                    st.rerun()

    with abas[1]: # DASHBOARD COM FILTRO DE DATA
        st.header("📊 Indicadores de Estoque")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("📦 Total de Peças", int(df_estoque["Quantidade"].sum()))
        col_m2.metric("⚠️ Modelos Zerados/Baixos", len(zerados))
        
        st.divider()
        st.subheader("📅 Filtrar Gráficos por Período")
        col_d1, col_d2 = st.columns(2)
        d_inicio = col_d1.date_input("Data Inicial", datetime.now().replace(day=1))
        d_fim = col_d2.date_input("Data Final", datetime.now())
        
        if not df_historico.empty:
            df_hist_copy = df_historico.copy()
            df_hist_copy['Data_Filtro'] = pd.to_datetime(df_hist_copy['Data']).dt.date
            df_filtrado = df_hist_copy[(df_hist_copy['Data_Filtro'] >= d_inicio) & (df_hist_copy['Data_Filtro'] <= d_fim)]
            
            df_saidas = df_filtrado[df_filtrado["Ação"] == "Saída"]
            df_entradas = df_filtrado[df_filtrado["Ação"] == "Entrada"]
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.subheader("🛠️ Quem mais Produziu?")
                if not df_entradas.empty: st.bar_chart(df_entradas.groupby("Separador")["Quantidade"].sum(), color="#16a34a")
            with col_g2:
                st.subheader("👤 Quem mais Retirou?")
                if not df_saidas.empty: st.bar_chart(df_saidas.groupby("Separador")["Quantidade"].sum(), color="#dc2626")

    with abas[2]: # HISTÓRICO
        st.header("🕒 Histórico Recente")
        st.dataframe(df_historico.drop(columns=["ID"], errors="ignore"), use_container_width=True, hide_index=True)

    if acesso_coord:
        with abas[3]: # FECHAMENTO
            st.header("👑 Fechamento Mensal")
            st.write("Baixe a planilha atualizada direto do Google Sheets ou salve o resumo em texto.")
