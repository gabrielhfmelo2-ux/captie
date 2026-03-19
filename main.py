import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import os

# ==========================================
# 1. CONFIGURAÇÃO E TEMA MINIMALISTA (CSS)
# ==========================================
st.set_page_config(page_title="Captie", page_icon="image/logo.png", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700;800&family=Inter:wght@400;600;700&display=swap');
    
    .stApp { background-color: #05060A; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #080A10; border-right: 1px solid rgba(56, 189, 248, 0.1); }
    
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { background: transparent !important; }

    /* Estilo das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 40px; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .stTabs [data-baseweb="tab"] { background: transparent; border: none; color: #475569; font-family: 'Rajdhani'; font-size: 16px; font-weight: 700; letter-spacing: 1px; padding: 10px 0; }
    .stTabs [aria-selected="true"] { color: #38BDF8 !important; border-bottom: none !important; text-shadow: 0 0 15px rgba(56,189,248,0.4); background: transparent !important;}

    /* Glassmorphism Cards */
    .card { background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(56, 189, 248, 0.05); border-radius: 12px; padding: 24px; transition: 0.3s; height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .card:hover { border-color: rgba(56, 189, 248, 0.3); transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 0 20px rgba(56,189,248,0.05); }
    .card-title { font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; margin-bottom: 5px; }
    .card-value { font-size: 38px; font-weight: 800; color: #F8FAFC; font-family: 'Rajdhani'; line-height: 1.1; letter-spacing: -1px; }
    .card-sub { font-size: 12px; color: #475569; margin-top: 8px; font-weight: 500;}
    
    /* Cores Neons e Brilhos */
    .text-cyan { color: #38BDF8; text-shadow: 0 0 15px rgba(56,189,248,0.4); }
    .text-green { color: #10B981; text-shadow: 0 0 15px rgba(16,185,129,0.4); }
    .text-red { color: #EF4444; text-shadow: 0 0 15px rgba(239,68,68,0.4); }
    .text-orange { color: #F59E0B; text-shadow: 0 0 15px rgba(245,158,11,0.4); }
    
    /* UI Adicionais (Milestones e Barras) */
    .milestone-box { background: rgba(15,23,42,0.4); border: 1px solid rgba(56, 189, 248, 0.1); padding: 15px; border-radius: 12px; text-align: center; flex: 1; transition: 0.3s; }
    .milestone-box:hover { border-color: #38BDF8; background: rgba(56,189,248,0.05); }
    .milestone-year { font-family: 'Rajdhani'; font-size: 28px; font-weight: 800; color: #F8FAFC; }
    
    button[kind="primary"] { background: linear-gradient(90deg, #0ea5e9, #38BDF8) !important; color: #05060A !important; font-weight: 800 !important; border-radius: 6px; border: none !important; transition: 0.3s; box-shadow: 0 4px 15px rgba(56,189,248,0.2); letter-spacing: 1px; }
    button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(56,189,248,0.4); }
    hr { border-color: rgba(255,255,255,0.05); margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# INICIALIZAÇÃO DE VARIÁVEL DE ESTADO PARA OS BOTÕES
if "ano_alvo" not in st.session_state:
    st.session_state.ano_alvo = 2010

# ==========================================
# 2. FUNÇÕES ÚTEIS
# ==========================================
def formata_br(v): 
    if pd.isna(v): return "R$ 0,00"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def carregar_imagem_local(caminho, fallback="LOGO", h="80"):
    if os.path.exists(caminho):
        with open(caminho, "rb") as f: return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return f"https://via.placeholder.com/{h}/0F172A/38BDF8?text={fallback}"

def progress_bar(label, percent, color):
    p = min(100, max(0, percent))
    return f"<div style='margin-top:20px;'><div style='display:flex; justify-content:space-between; margin-bottom:6px;'><span style='color:#94A3B8; font-size:11px; font-weight:700; letter-spacing:1px;'>{label}</span> <b style='color:{color}; font-family:Rajdhani; font-size:16px;'>{percent:.1f}%</b></div><div style='width:100%; background:rgba(255,255,255,0.05); height:6px; border-radius:3px; overflow:hidden;'><div style='width:{p}%; background:{color}; height:100%; border-radius:3px; box-shadow:0 0 10px {color};'></div></div></div>"

ipca_hist = { 1995:22.41, 2000:5.97, 2005:5.69, 2010:5.91, 2015:10.67, 2020:4.52, 2025:4.00, 2026:4.00 }
ANO_ATUAL = 2026

# ==========================================
# 3. BARRA LATERAL (INPUTS)
# ==========================================
with st.sidebar:
    st.markdown(f"""
        <div style="text-align:center; margin-bottom:15px; margin-top:10px;">
            <img src="{carregar_imagem_local('image/logo.png')}" style="max-width:60%; max-height:110px;">
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='card-title' style='margin-bottom:15px;'>COMO VOCÊ VAI COMEÇAR?</div>", unsafe_allow_html=True)
    capital = st.number_input("Dinheiro Inicial (R$)", min_value=0.0, max_value=1000000.0, value=10000.0, step=1000.0)
    aporte = st.number_input("Quanto vai guardar por mês? (R$)", min_value=0.0, max_value=100000.0, value=1000.0, step=100.0)
    anos = st.slider("Por quantos anos?", 1, 40, 20)
    
    st.markdown("<div class='card-title' style='margin-top:20px; margin-bottom:5px;'>ONDE VAI INVESTIR?</div>", unsafe_allow_html=True)
    
    ativos_db = {
        "Tesouro Direto (Governo)": {"tx": 11.0, "isento": False},
        "CDB (Bancos)": {"tx": 11.5, "isento": False},
        "LCI / LCA (Bancos)": {"tx": 9.5, "isento": True},
        "Ações (Empresas)": {"tx": 12.0, "isento": False}
    }
    ativo_escolhido = st.selectbox("", list(ativos_db.keys()), label_visibility="collapsed")
    taxa_aa = ativos_db[ativo_escolhido]["tx"]
    isento = ativos_db[ativo_escolhido]["isento"]

    desc_ativos = {
        "Tesouro Direto (Governo)": "🏛️ Como funciona: Você empresta dinheiro para o Governo. É o investimento mais seguro do país e protege seu poder de compra da inflação.",
        "CDB (Bancos)": "🏦 Como funciona: Você empresta para bancos. Rende mais que a poupança e tem a garantia do FGC (seguro anti-quebra).",
        "LCI / LCA (Bancos)": "🌾 Como funciona: Você financia imóveis ou o agronegócio. A grande vantagem é que todo o lucro vai limpo para o seu bolso, sem imposto.",
        "Ações (Empresas)": "🏢 Como funciona: Você vira sócio de grandes empresas (ex: Itaú, Petrobras). Oscila mais, mas historicamente é o que mais enriquece no longo prazo."
    }
    st.markdown(f"<div style='background:rgba(255,255,255,0.02); padding:12px; border-radius:6px; font-size:12px; color:#94A3B8; margin-top:5px; border: 1px solid rgba(255,255,255,0.05); line-height: 1.4;'>{desc_ativos[ativo_escolhido]}</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: rgba(56,189,248,0.05); border: 1px solid rgba(56,189,248,0.15); padding: 15px; border-radius: 8px; margin-top: 20px;'>
            <div style='color: #38BDF8; font-size: 11px; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px;'>ℹ️ BASE DE CÁLCULO:</div>
            <div style='color: #94A3B8; font-size: 12px; line-height: 1.4;'>
                Para você ter o valor exato, nosso sistema já desconta o <b>Imposto de Renda (15%)</b> automático e tira a <b>inflação (projetada em 4,5% a.a.)</b> para você saber seu poder de compra real.
            </div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. CORE MATEMÁTICO
# ==========================================
st.write("") 

meses = anos * 12
taxa_am = (1 + taxa_aa/100)**(1/12) - 1
taxa_poupanca_am = (1 + 6.17/100)**(1/12) - 1

s_gaveta, s_invest, s_poup = capital, capital, capital
dados = []
h_100k, h_500k, h_1m = None, None, None

for i in range(meses + 1):
    lucro_b = s_invest - s_gaveta
    imposto = 0 if isento else lucro_b * 0.15
    s_liq = s_invest - imposto
    
    if not h_100k and s_liq >= 100000: h_100k = i / 12
    if not h_500k and s_liq >= 500000: h_500k = i / 12
    if not h_1m and s_liq >= 1000000: h_1m = i / 12

    if i % 12 == 0: dados.append([i//12, s_gaveta, s_poup, s_invest, s_liq])
    if i < meses:
        s_gaveta += aporte
        s_poup = s_poup * (1 + taxa_poupanca_am) + aporte
        s_invest = s_invest * (1 + taxa_am) + aporte

df = pd.DataFrame(dados, columns=["Ano", "Gaveta", "Poupanca", "Bruto", "Liquido"])
patrimonio_final = s_liq
juros_liquidos = patrimonio_final - s_gaveta

# ==========================================
# 5. DASHBOARD PRINCIPAL (HERO)
# ==========================================
c1, c2, c3 = st.columns(3)
c1.markdown(f"<div class='card'><div class='card-title'>Dinheiro do seu Bolso</div><div class='card-value'>{formata_br(s_gaveta)}</div><div class='card-sub'>A soma de todos os seus depósitos</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='card-title'>Dinheiro Trabalhando Pra Você</div><div class='card-value text-green' style='font-size: 32px; margin-bottom: 6px;'>+ {formata_br(juros_liquidos)}</div><div class='card-sub'>Seu lucro só por ter deixado o tempo passar</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card' style='border-color: rgba(56,189,248,0.3);'><div class='card-title text-cyan'>Valor Total Acumulado</div><div class='card-value text-cyan'>{formata_br(patrimonio_final)}</div><div class='card-sub'>Montante final limpo e pronto para você usar</div></div>", unsafe_allow_html=True)

st.write("")
t1, t2, t3 = st.tabs(["📊 A JORNADA", "🏖️ VIVER DE RENDA", "🛒 PODER DE COMPRA REAL"])

# --- ABA 1: GRÁFICO E A COMPARAÇÃO COM A POUPANÇA ---
with t1:
    col_g1, col_g2 = st.columns([2.5, 1])
    with col_g1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Ano"], y=df["Gaveta"], name="Debaixo do Colchão", line=dict(color='rgba(255,255,255,0.2)', width=2)))
        fig.add_trace(go.Scatter(x=df["Ano"], y=df["Poupanca"], name="Poupança", line=dict(color='#F59E0B', width=2, dash='dot')))
        fig.add_trace(go.Scatter(x=df["Ano"], y=df["Liquido"], name="Investido Corretamente", line=dict(color='#38BDF8', width=3), fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.1)'))
        fig.update_layout(hovermode="x unified", margin=dict(l=0,r=0,t=20,b=0), height=320, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#94A3B8")), xaxis=dict(showgrid=False, color="#64748B"), yaxis=dict(gridcolor='rgba(255,255,255,0.02)', color="#64748B", tickprefix="R$ "))
        st.plotly_chart(fig, use_container_width=True)
        
    with col_g2:
        st.markdown("<div class='card-title' style='text-align:center; margin-bottom:10px;'>QUANDO VOCÊ CHEGA LÁ?</div>", unsafe_allow_html=True)
        m1 = f"{int(h_100k)} ANOS" if h_100k else "N/A"
        m2 = f"{int(h_500k)} ANOS" if h_500k else "N/A"
        m3 = f"{int(h_1m)} ANOS" if h_1m else "N/A"
        
        st.markdown(f"""
        <div style="display:flex; flex-direction:column; gap:10px; height: 100%;">
            <div class="milestone-box"><div class="card-title">R$ 100 MIL</div><div class="milestone-year">{m1}</div></div>
            <div class="milestone-box"><div class="card-title">R$ 500 MIL</div><div class="milestone-year">{m2}</div></div>
            <div class="milestone-box" style="border-color:#10B981; background:rgba(16,185,129,0.05);"><div class="card-title text-green">R$ 1 MILHÃO</div><div class="milestone-year text-green">{m3}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.2); padding: 15px; border-radius: 8px; margin-top: 10px;">
            <b class='text-orange'>⚠️ O Custo da Ignorância:</b> Se você tivesse deixado esse mesmo dinheiro na Poupança, você teria apenas <b>{formata_br(s_poup)}</b>. Ao investir da forma correta, você ganha <b>{formata_br(patrimonio_final - s_poup)} a mais</b> sem fazer nenhum esforço extra!
        </div>
    """, unsafe_allow_html=True)

# --- ABA 2: VIVER DE RENDA ---
with t2:
    st.write("")
    c_r1, c_r2 = st.columns([1, 1.5])
    with c_r1:
        st.markdown("<div class='card-title' style='margin-bottom:10px;'>SUA META PARA PARAR DE TRABALHAR</div>", unsafe_allow_html=True)
        renda_alvo = st.number_input("Qual seria sua renda mensal dos sonhos? (R$)", min_value=0.0, max_value=200000.0, value=10000.0, step=1000.0)
        
        st.markdown("<br><div class='card-title' style='margin-bottom:10px;'>COMO VOCÊ VAI RECEBER ESSA RENDA?</div>", unsafe_allow_html=True)
        estrategias = {
            "FIIs (Aluguéis)": 0.8,
            "Renda Fixa (Juros)": 0.7,
            "Dividendos (Lucros)": 0.6
        }
        tipo_r = st.selectbox("", list(estrategias.keys()), label_visibility="collapsed")
        yield_escolhido = estrategias[tipo_r] / 100

        desc_renda = {
            "FIIs (Aluguéis)": "🏢 Como funciona: Você compra 'pedacinhos' de shoppings e galpões e recebe os aluguéis todo mês, totalmente isentos de imposto, pingando direto na conta.",
            "Renda Fixa (Juros)": "🛡️ Como funciona: Seu dinheiro fica protegido em investimentos super seguros rendendo juros diários. Você saca apenas o lucro gerado no mês, mantendo o montante principal intacto.",
            "Dividendos (Lucros)": "📈 Como funciona: Você vive da distribuição de lucros (dividendos) que as empresas mais sólidas e lucrativas do país pagam aos seus acionistas."
        }
        st.markdown(f"<div style='background:rgba(255,255,255,0.02); padding:12px; border-radius:6px; font-size:12px; color:#94A3B8; margin-top:5px; border: 1px solid rgba(255,255,255,0.05); line-height: 1.4;'>{desc_renda[tipo_r]}</div>", unsafe_allow_html=True)
        
    with c_r2:
        renda_gerada = patrimonio_final * yield_escolhido
        cobertura = (renda_gerada / renda_alvo) * 100 if renda_alvo > 0 else 0
        cor_bar = "#10B981" if cobertura >= 100 else "#38BDF8"
        t_color = "text-green" if cobertura >= 100 else "text-cyan"
        
        st.markdown(f"<div class='card'><div class='card-title'>SALÁRIO MENSAL GERADO AUTOMATICAMENTE</div><div class='card-value {t_color}' style='font-size: 56px;'>{formata_br(renda_gerada)}</div><div class='card-sub'>Esse é o valor limpo que vai cair na sua conta todos os meses sem você precisar trabalhar.</div>{progress_bar('O quanto o plano cobre da sua Renda dos Sonhos', cobertura, cor_bar)}</div>", unsafe_allow_html=True)

# --- ABA 3: CHOQUE DE INFLAÇÃO ---
with t3:
    st.write("")
    
    dados_precos = {
        "🍔 Lanche popular fast food": { 1995: 1.60, 2000: 2.90, 2005: 5.40, 2010: 8.75, 2015: 13.50, 2020: 19.90, 2025: 25.90, 2026: 26.50 },
        "🛒 Cesta básica": { 1995: 64.0, 2000: 115.0, 2005: 185.0, 2010: 250.0, 2015: 390.0, 2020: 550.0, 2025: 780.0, 2026: 820.0 },
        "💵 Quantidade de salários mínimos": { 1995: 100.0, 2000: 151.0, 2005: 300.0, 2010: 510.0, 2015: 788.0, 2020: 1045.0, 2025: 1412.0, 2026: 1502.0 },
        "📱 Celular top de linha": { 1995: 1500.0, 2000: 2000.0, 2005: 2500.0, 2010: 3000.0, 2015: 4000.0, 2020: 7000.0, 2025: 9000.0, 2026: 9500.0 },
        "✈️ Viagem internacional": { 1995: 2000.0, 2000: 3000.0, 2005: 5000.0, 2010: 6000.0, 2015: 10000.0, 2020: 15000.0, 2025: 20000.0, 2026: 21000.0 },
        "🚗 Carro popular 0km": { 1995: 7500.0, 2000: 14000.0, 2005: 22000.0, 2010: 26000.0, 2015: 38000.0, 2020: 52000.0, 2025: 72000.0, 2026: 78000.0 },
        "🏠 Imóvel apartamento padrão": { 1995: 40000.0, 2000: 60000.0, 2005: 90000.0, 2010: 150000.0, 2015: 250000.0, 2020: 350000.0, 2025: 500000.0, 2026: 550000.0 }
    }

    c_i1, c_i2 = st.columns([1, 1.5])
    with c_i1:
        st.markdown("<div class='card-title' style='margin-bottom:10px;'>MÁQUINA DO TEMPO (ESCOLHA O ANO)</div>", unsafe_allow_html=True)
        
        anos_grid = [1995, 2000, 2005, 2010, 2015, 2020]
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        col_btn4, col_btn5, col_btn6 = st.columns(3)
        b_cols = [col_btn1, col_btn2, col_btn3, col_btn4, col_btn5, col_btn6]
        
        for i, ano in enumerate(anos_grid):
            btn_type = "primary" if st.session_state.ano_alvo == ano else "secondary"
            if b_cols[i].button(str(ano), use_container_width=True, type=btn_type, key=f"btn_{ano}"):
                st.session_state.ano_alvo = ano
                st.rerun()

        ano_alvo = st.session_state.ano_alvo
        
        fator = 1.0
        for a in range(ano_alvo, ANO_ATUAL): fator *= (1 + ipca_hist.get(a, 6.0) / 100)
        v_antigo = patrimonio_final / fator
        
        st.write("")
        st.markdown(f"""
        <div class='card' style='padding:30px;'>
            <div class='card-title'>PODER DE COMPRA EQUIVALENTE</div>
            <div class='card-value text-cyan' style='font-size:42px;'>{formata_br(v_antigo)}</div>
            <div class='card-sub'>Para você comprar hoje o exato padrão de vida que se comprava com <b>{formata_br(v_antigo)}</b> em {ano_alvo}, você precisa gastar todos os seus atuais <b>{formata_br(patrimonio_final)}</b>. A inflação corroeu a diferença invisivelmente.</div>
        </div>
        """, unsafe_allow_html=True)

    with c_i2:
        st.markdown(f"<div class='card-title' style='margin-bottom:15px; margin-top:10px;'>O QUE SEUS {formata_br(patrimonio_final)} COMPRARIAM...</div>", unsafe_allow_html=True)
        
        for item, preco in dados_precos.items():
            p_antes = preco[ano_alvo]
            p_hoje = preco[2026]
            qtd_antes = patrimonio_final / p_antes
            qtd_hoje = patrimonio_final / p_hoje
            
            pct_variacao = ((qtd_hoje / qtd_antes) - 1) * 100
            
            cor_pct = "text-red" if pct_variacao < 0 else "text-green"
            sinal = "+" if pct_variacao > 0 else ""
            
            fmt = lambda q: f"{q:,.1f}" if q < 100 else f"{q:,.0f}"

            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(15,23,42,0.4); padding:15px 20px; border-radius:12px; margin-bottom:10px; border:1px solid rgba(255,255,255,0.02);">
                <div style="width:35%;">
                    <div style="color:#F8FAFC; font-weight:700; font-family:'Inter'; font-size:15px;">{item}</div>
                    <div style="color:#64748B; font-size:11px; margin-top:4px;">Unidade: {formata_br(p_antes)} ➔ {formata_br(p_hoje)}</div>
                </div>
                <div style="text-align:right; width:20%;">
                    <div style="font-size:10px; color:#64748B; font-weight:700;">EM {ano_alvo}</div>
                    <div style="color:#F8FAFC; font-family:'Rajdhani'; font-size:18px; font-weight:800;">{fmt(qtd_antes)}</div>
                </div>
                <div style="text-align:right; width:20%;">
                    <div style="font-size:10px; color:#64748B; font-weight:700;">HOJE (2026)</div>
                    <div style="color:#94A3B8; font-family:'Rajdhani'; font-size:18px; font-weight:600;">{fmt(qtd_hoje)}</div>
                </div>
                <div style="text-align:right; width:25%;">
                    <div style="font-size:10px; color:#EF4444; font-weight:700;">PODER DE COMPRA</div>
                    <div class="{cor_pct}" style="font-family:'Rajdhani'; font-size:18px; font-weight:800;">{sinal}{pct_variacao:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
