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
        # Garante que planilhas antigas recebam as novas colunas
        if "ID" not in df_historico.columns:
            df_historico["ID"] = [str(uuid.uuid4()) for _ in range(len(df_historico))]
        if "Ação" not in df_historico.columns:
            df_historico["Ação"] = "Saída"
            df_historico.to_csv(ARQUIVO_HISTORICO, index=False)
    else:
        df_historico = pd.DataFrame(columns=["ID", "Data", "Ação", "Separador", "Modelo", "Quantidade"])
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

    def extrair_linha(nome):
        if " - " in nome: return nome.rsplit(" - ", 1)[0]
        return nome
        
    def extrair_cor(nome):
        if " - " in nome: return nome.rsplit(" - ", 1)[1]
        return "-"

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

# Inicializa os dados
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

# ==========================================
# CONTROLE DE ACESSO (3 NÍVEIS)
# ==========================================
st.sidebar.title("🔐 Acesso Seguro")
perfil = st.sidebar.radio("Nível de permissão:", ["👀 Visualizador (Equipe)", "⚙️ Controle (Fran)", "👑 Coordenador"])

acesso_fran = False
acesso_coord = False

if perfil == "⚙️ Controle (Fran)":
    senha = st.sidebar.text_input("Senha da Fran:", type="password")
    if senha == "fran123":
        acesso_fran = True
    elif senha != "":
        st.sidebar.error("❌ Senha incorreta!")

elif perfil == "👑 Coordenador":
    senha = st.sidebar.text_input("Senha do Coordenador:", type="password")
    if senha == "coord123":
        acesso_coord = True
    elif senha != "":
        st.sidebar.error("❌ Senha incorreta!")

# ==========================================
# TELA PRINCIPAL
# ==========================================
st.markdown("<h1 class='main-title'>📦 Torres - ESTOQUE</h1>", unsafe_allow_html=True)

if not (acesso_fran or acesso_coord):
    st.info("👋 **Bem-vindo(a) à central de estoque Torres.** Você está no modo visualização. Solicite as retiradas de material diretamente à Fran.")
    
    busca = st.text_input("🔍 Buscar modelo ou cor (Ex: TR03 Branco)...", key="busca_equipe")
    st.divider()
    exibir_estoque_premium(df_estoque, busca)

else:
    if acesso_coord:
        st.sidebar.success("👑 Acesso Liberado: Coordenador")
        abas_nomes = ["📦 Operação", "📊 Dashboard", "🕒 Histórico e Dados", "👑 Fechamento"]
    else:
        st.sidebar.success("✅ Acesso Liberado: Fran")
        abas_nomes = ["📦 Operação", "📊 Dashboard", "🕒 Histórico e Dados"]

    abas = st.tabs(abas_nomes)

    # --- ABA 1: OPERAÇÃO ---
    with abas[0]:
        st.header("📤 Registrar Saída (Uso)")
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
                        "Ação": "Saída",
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
        st.write("") 
        exibir_estoque_premium(df_estoque, busca)

        st.divider()

        st.header("📥 Receber Material (Produção)")
        with st.form("form_entrada", clear_on_submit=True):
            col1_in, col2_in, col3_in = st.columns([2, 3, 1])
            with col1_in:
                quem_fez = st.selectbox("1. Quem produziu?", [""] + separadores)
            with col2_in:
                modelo_rep = st.selectbox("2. Qual modelo?", [""] + sorted(df_estoque["Modelo"].tolist()))
            with col3_in:
                qtd_rep = st.number_input("3. Qtd", min_value=1, value=1, step=1)
            
            submit_entrada = st.form_submit_button("Lançar Entrada no Estoque")
            
            if submit_entrada:
                if not modelo_rep or not quem_fez:
                    st.error("⚠️ Preencha o modelo e quem produziu as peças.")
                else:
                    idx = df_estoque[df_estoque["Modelo"] == modelo_rep].index[0]
                    df_estoque.at[idx, "Quantidade"] += qtd_rep
                    salvar_estoque(df_estoque)
                    
                    novo_registro = pd.DataFrame([{
                        "ID": str(uuid.uuid4()),
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Ação": "Entrada",
                        "Separador": quem_fez,
                        "Modelo": modelo_rep,
                        "Quantidade": qtd_rep
                    }])
                    df_historico = pd.concat([novo_registro, df_historico], ignore_index=True).head(500)
                    salvar_historico(df_historico)
                    
                    st.success(f"✅ {qtd_rep}x {modelo_rep} (Produzido por {quem_fez}) adicionados ao estoque!")
                    time.sleep(1.5)
                    st.rerun()

        st.divider()
        st.subheader("➕ Cadastrar Novo Produto")
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

    # --- ABA 2: DASHBOARD ---
    with abas[1]:
        st.header("📊 Indicadores de Estoque")
        
        col_metric1, col_metric2 = st.columns(2)
        total_pecas = int(df_estoque["Quantidade"].sum())
        itens_em_baixa = int((df_estoque["Quantidade"] <= 5).sum())
        
        col_metric1.metric("📦 Total de Peças Físicas", total_pecas)
        col_metric2.metric("⚠️ Alertas de Falta (≤ 5 un)", itens_em_baixa)
        
        st.divider()
        
        if not df_historico.empty:
            df_saidas = df_historico[df_historico["Ação"] == "Saída"]
            df_entradas = df_historico[df_historico["Ação"] == "Entrada"]
            
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.subheader("🛠️ Quem mais Produziu?")
                if not df_entradas.empty:
                    top_produtores = df_entradas.groupby("Separador")["Quantidade"].sum().sort_values(ascending=False)
                    st.bar_chart(top_produtores, color="#16a34a")
                else:
                    st.info("Sem dados de produção ainda.")
                    
            with col_graf2:
                st.subheader("👤 Quem mais Retirou?")
                if not df_saidas.empty:
                    top_separadores = df_saidas.groupby("Separador")["Quantidade"].sum().sort_values(ascending=False)
                    st.bar_chart(top_separadores, color="#dc2626")
                else:
                    st.info("Sem dados de retirada ainda.")
            
            st.divider()
            
            st.subheader("📈 Top 5 Modelos Mais Retirados")
            if not df_saidas.empty:
                top_modelos = df_saidas.groupby("Modelo")["Quantidade"].sum().sort_values(ascending=False).head(5)
                st.bar_chart(top_modelos)
        else:
            st.info("Aguardando movimentações para gerar gráficos.")

    # --- ABA 3: HISTÓRICO ---
    with abas[2]:
        st.header("🕒 Histórico Recente")
        
        # Formata a exibição para ficar claro o que é entrada e saída
        df_exibicao = df_historico.drop(columns=["ID"], errors="ignore").copy()
        
        def colorir_acao(val):
            if val == 'Entrada': return 'color: #16a34a; font-weight: bold;'
            if val == 'Saída': return 'color: #dc2626; font-weight: bold;'
            return ''
            
        st.dataframe(df_exibicao.style.map(colorir_acao, subset=['Ação']), use_container_width=True, hide_index=True)
        
        st.divider()
        
        st.subheader("↩️ Estornar Lançamento")
        st.caption("Caso tenha havido erro, cancele aqui e o estoque será corrigido automaticamente.")
        
        ultimos_registros = df_historico.head(20)
        opcoes_desfazer = {}
        for _, row in ultimos_registros.iterrows():
            acao = row.get("Ação", "Saída")
            if acao == "Entrada":
                texto = f"{row['Data']} | 🟢 ENTRADA: {row['Separador']} produziu {row['Quantidade']}x {row['Modelo']}"
            else:
                texto = f"{row['Data']} | 🔴 SAÍDA: {row['Separador']} retirou {row['Quantidade']}x {row['Modelo']}"
            opcoes_desfazer[texto] = row["ID"]
            
        selecao_desfazer = st.selectbox("Registro para cancelar:", [""] + list(opcoes_desfazer.keys()))
        
        if st.button("❌ Estornar Movimentação"):
            if selecao_desfazer:
                id_alvo = opcoes_desfazer[selecao_desfazer]
                registro_cancelado = df_historico[df_historico["ID"] == id_alvo].iloc[0]
                
                idx = df_estoque[df_estoque["Modelo"] == registro_cancelado["Modelo"]].index[0]
                
                # Se for saída, devolve pro estoque. Se for entrada, tira do estoque.
                if registro_cancelado.get("Ação", "Saída") == "Saída":
                    df_estoque.at[idx, "Quantidade"] += registro_cancelado["Quantidade"]
                else:
                    df_estoque.at[idx, "Quantidade"] -= registro_cancelado["Quantidade"]
                    # Evita estoque negativo caso tenham gasto a peça antes de estornar
                    if df_estoque.at[idx, "Quantidade"] < 0:
                        df_estoque.at[idx, "Quantidade"] = 0
                        
                salvar_estoque(df_estoque)
                
                df_historico = df_historico[df_historico["ID"] != id_alvo]
                salvar_historico(df_historico)
                
                st.success("✅ Estorno realizado! Saldo atualizado.")
                time.sleep(1.5)
                st.rerun()

    # --- ABA 4: FECHAMENTO (SÓ COORDENADOR) ---
    if acesso_coord:
        with abas[3]:
            st.header("👑 Área do Coordenador")
            st.write("Exporte os relatórios gerenciais consolidados do sistema.")
            
            st.divider()
            
            df_saidas = df_historico[df_historico["Ação"] == "Saída"]
            df_entradas = df_historico[df_historico["Ação"] == "Entrada"]
            
            texto_relatorio = f"====================================\n"
            texto_relatorio += f"RELATORIO DE FECHAMENTO - CAIXA TOMADA\n"
            texto_relatorio += f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            texto_relatorio += f"====================================\n\n"
            
            texto_relatorio += f"1. RESUMO GERAL DO ESTOQUE:\n"
            texto_relatorio += f"Total de Peças em Estoque: {int(df_estoque['Quantidade'].sum())} unidades\n"
            texto_relatorio += f"Modelos Cadastrados: {len(df_estoque)}\n\n"
            
            texto_relatorio += f"2. RESUMO DE PRODUÇÃO (ENTRADAS):\n"
            if not df_entradas.empty:
                texto_relatorio += f"Total de Peças Produzidas: {int(df_entradas['Quantidade'].sum())} unidades\n"
                agrupado_prod = df_entradas.groupby("Separador")["Quantidade"].sum().sort_values(ascending=False)
                for sep, qtd in agrupado_prod.items():
                    texto_relatorio += f"- {sep}: produziu {qtd} peças\n"
            else:
                texto_relatorio += "Nenhuma produção registrada.\n"
                
            texto_relatorio += f"\n3. RESUMO DE USO (SAÍDAS):\n"
            if not df_saidas.empty:
                texto_relatorio += f"Total de Peças Retiradas: {int(df_saidas['Quantidade'].sum())} unidades\n\n"
                
                texto_relatorio += f"--- Retiradas por Colaborador ---\n"
                agrupado_sep = df_saidas.groupby("Separador")["Quantidade"].sum().sort_values(ascending=False)
                for sep, qtd in agrupado_sep.items():
                    texto_relatorio += f"- {sep}: {qtd} peças\n"
                
                texto_relatorio += f"\n--- Top 5 Modelos Mais Consumidos ---\n"
                agrupado_mod = df_saidas.groupby("Modelo")["Quantidade"].sum().sort_values(ascending=False).head(5)
                for mod, qtd in agrupado_mod.items():
                    texto_relatorio += f"- {mod}: {qtd} peças\n"
            else:
                texto_relatorio += "Nenhuma retirada registrada no sistema.\n"
                
            texto_relatorio += f"\n====================================\n"
            texto_relatorio += f"Fim do Relatório\n"

            st.subheader("📄 Relatório Rápido de Fechamento")
            st.text_area("Pré-visualização do Relatório:", value=texto_relatorio, height=250, disabled=True)
            
            st.download_button(
                label="📥 Baixar Relatório (Formato .txt para WhatsApp/Impressão)",
                data=texto_relatorio.encode('utf-8'),
                file_name=f"fechamento_{datetime.now().strftime('%d-%m-%Y')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.divider()
            
            st.subheader("📥 Exportação Avançada (Planilhas Excel)")
            col_down1, col_down2 = st.columns(2)
            
            with col_down1:
                csv_estoque = df_estoque.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📊 Planilha de Estoque Atual",
                    data=csv_estoque,
                    file_name=f"estoque_{datetime.now().strftime('%d-%m-%Y')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            with col_down2:
                csv_historico = df_historico.drop(columns=["ID"], errors="ignore").to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📊 Relatório Base de Movimentação",
                    data=csv_historico,
                    file_name=f"historico_{datetime.now().strftime('%d-%m-%Y')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
