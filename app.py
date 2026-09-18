import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import os

# =======================================================
# CONFIGURAÇÃO DA PÁGINA
# =======================================================
st.set_page_config(
    page_title="Studio Belleza & Arte | Manicure & Academy",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =======================================================
# BANCO DE DADOS LOCAL (SQLite)
# =======================================================
DB_FILE = "studio_manicure.db"

try:
    SENHA_MESTRE = st.secrets.get("GESTORA_PASSWORD", "studio2026")
except Exception:
    SENHA_MESTRE = os.environ.get("GESTORA_PASSWORD", "studio2026")

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL UNIQUE,
            data_nascimento TEXT,
            data_cadastro TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_servico TEXT NOT NULL,
            duracao_minutos INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            servico_id INTEGER,
            data_hora TEXT NOT NULL,
            status TEXT DEFAULT 'Pendente',
            observacoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (servico_id) REFERENCES servicos (id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS turmas_curso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_curso TEXT NOT NULL,
            data_inicio TEXT NOT NULL,
            horario TEXT NOT NULL,
            vagas_limite INTEGER NOT NULL DEFAULT 6,
            preco_curso REAL NOT NULL,
            status TEXT DEFAULT 'Aberta'
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS inscricoes_curso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turma_id INTEGER,
            nome_aluna TEXT NOT NULL,
            telefone TEXT NOT NULL,
            experiencia_previa TEXT,
            tipo_vaga TEXT DEFAULT 'Titular',
            posicao_reserva INTEGER DEFAULT 0,
            status_pagamento TEXT DEFAULT 'Pendente',
            FOREIGN KEY (turma_id) REFERENCES turmas_curso (id)
        )
    ''')

    c.execute("INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES ('agenda_status', 'Aberta')")
    c.execute("INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES ('mes_liberado', '2026-10')")

    c.execute("SELECT COUNT(*) FROM servicos")
    if c.fetchone()[0] == 0:
        c.executemany('''
            INSERT INTO servicos (nome_servico, duracao_minutos, preco)
            VALUES (?, ?, ?)
        ''', [
            ("Pé e Mão Tradicional", 60, 65.0),
            ("Alongamento em Gel Moldado", 120, 150.0),
            ("Manutenção de Unha em Gel", 90, 100.0)
        ])

    c.execute("SELECT COUNT(*) FROM turmas_curso")
    if c.fetchone()[0] == 0:
        c.executemany('''
            INSERT INTO turmas_curso (nome_curso, data_inicio, horario, vagas_limite, preco_curso, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [
            ("Formação Profissional em Gel & Fibra", "20/10/2026", "09:00 às 17:00", 6, 650.0, "Aberta"),
            ("Imersão em Decorações & Nail Art", "27/10/2026", "13:00 às 18:00", 4, 450.0, "Aberta")
        ])

    c.execute("SELECT COUNT(*) FROM clientes")
    if c.fetchone()[0] == 0:
        hoje = datetime.now()
        data_hoje = hoje.strftime("%Y-%m-%d 10:00")
        data_15dias = (hoje - timedelta(days=15)).strftime("%Y-%m-%d 14:00")
        data_30dias = (hoje - timedelta(days=30)).strftime("%Y-%m-%d 16:00")

        c.execute("INSERT INTO clientes (nome, telefone, data_nascimento, data_cadastro) VALUES (?, ?, ?, ?)",
                  ("Camila Oliveira", "71991234567", hoje.strftime("%Y-%m-%d"), hoje.strftime("%Y-%m-%d")))
        c.execute("INSERT INTO clientes (nome, telefone, data_nascimento, data_cadastro) VALUES (?, ?, ?, ?)",
                  ("Beatriz Lima", "71992345678", "1998-11-20", hoje.strftime("%Y-%m-%d")))

        c.execute("INSERT INTO agendamentos (cliente_id, servico_id, data_hora, status) VALUES (1, 1, ?, 'Concluído')", (data_hoje,))
        c.execute("INSERT INTO agendamentos (cliente_id, servico_id, data_hora, status) VALUES (1, 2, ?, 'Concluído')", (data_15dias,))
        c.execute("INSERT INTO agendamentos (cliente_id, servico_id, data_hora, status) VALUES (2, 3, ?, 'Concluído')", (data_30dias,))

    conn.commit()
    conn.close()

init_db()

# =======================================================
# CSS COMPLETO
# =======================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #2e1065;
    }
    .stApp {
        background-color: #faf5ff;
    }

    .site-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        padding: 18px 36px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(88, 28, 135, 0.05);
        border: 1px solid #f3e8ff;
        margin-bottom: 24px;
    }
    .nav-brand {
        font-family: 'Playfair Display', serif;
        font-size: 24px;
        font-weight: 700;
        color: #581c87;
    }
    .nav-tagline {
        font-size: 11px;
        color: #9333ea;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .hero-section {
        background: linear-gradient(135deg, #2e1065 0%, #581c87 50%, #7e22ce 100%);
        border-radius: 24px;
        padding: 50px 32px;
        color: #ffffff;
        text-align: center;
        margin-bottom: 32px;
        box-shadow: 0 16px 36px -6px rgba(88, 28, 135, 0.35);
        border: 1px solid #c084fc;
    }
    .hero-section h1 {
        font-family: 'Playfair Display', serif;
        font-size: 40px;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
    }
    .hero-section p {
        font-size: 16px;
        color: #f5f3ff;
        max-width: 650px;
        margin: 12px auto 0 auto;
    }

    .site-card {
        background: #ffffff;
        border: 1px solid #f3e8ff;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(107, 33, 168, 0.05);
        border-top: 5px solid #7e22ce;
        margin-bottom: 20px;
    }
    .site-card h3 {
        font-family: 'Playfair Display', serif;
        font-size: 20px;
        color: #3b0764;
        margin: 6px 0;
    }
    .card-price-value {
        font-size: 24px;
        font-weight: 700;
        color: #581c87;
        margin: 10px 0;
    }

    .metric-box {
        background: #ffffff;
        border-radius: 16px;
        padding: 20px;
        border-left: 5px solid #7e22ce;
        box-shadow: 0 4px 16px rgba(107, 33, 168, 0.06);
        text-align: center;
        margin-bottom: 15px;
    }
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #7e22ce;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #3b0764;
        margin: 6px 0 2px 0;
    }
    .metric-sub {
        font-size: 12px;
        color: #64748b;
    }

    /* CARD DE DESTAQUE PARA O WHATSAPP DA GESTORA */
    .zap-destaque-box {
        background: #f0fdf4;
        border: 2px solid #86efac;
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 25px;
        box-shadow: 0 6px 20px rgba(34, 197, 94, 0.12);
    }

    .stButton > button {
        background: linear-gradient(135deg, #7e22ce 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        border-radius: 50px !important;
        padding: 0.75rem 1.8rem !important;
        border: none !important;
        box-shadow: 0 8px 20px rgba(126, 34, 206, 0.28) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #6b21a8 0%, #9333ea 100%) !important;
        box-shadow: 0 12px 28px rgba(126, 34, 206, 0.42) !important;
        transform: translateY(-2px) scale(1.01) !important;
    }
    .stLinkButton > a {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border-radius: 50px !important;
        padding: 0.85rem 2rem !important;
        border: none !important;
        box-shadow: 0 8px 22px rgba(34, 197, 94, 0.35) !important;
        transition: all 0.3s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .stLinkButton > a:hover {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
        box-shadow: 0 12px 28px rgba(34, 197, 94, 0.45) !important;
        transform: translateY(-2px) !important;
        color: #ffffff !important;
    }

    .badge-vagas-abertas {
        background-color: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
    }
    .badge-reserva-aberta {
        background-color: #fffbeb;
        color: #b45309;
        border: 1px solid #fde68a;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
    }

    .site-footer {
        text-align: center;
        padding: 30px 20px;
        color: #7e22ce;
        font-size: 13px;
        border-top: 1px solid #f3e8ff;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# =======================================================
# NAVBAR
# =======================================================
st.markdown("""
    <div class="site-nav">
        <div>
            <div class="nav-brand">Studio Belleza & Arte</div>
            <div class="nav-tagline">Nail Design & Academy</div>
        </div>
        <div style="font-size: 14px; color: #581c87; font-weight: 600;">
            ✨ Atendimento Exclusivo • Cursos com Certificado
        </div>
    </div>
""", unsafe_allow_html=True)

aba_selecionada = st.radio(
    "Navegação",
    ["✨ Início", "💅 Serviços & Valores", "🎓 Cursos & Turmas", "📅 Agendar Horário", "🔐 Acesso Gestora"],
    horizontal=True,
    label_visibility="collapsed"
)

# =======================================================
# PÁGINA 1: INÍCIO
# =======================================================
if aba_selecionada == "✨ Início":
    st.markdown("""
        <div class="hero-section">
            <div style="text-transform: uppercase; letter-spacing: 3px; font-size: 11px; margin-bottom: 8px; color: #e9d5ff; font-weight: 700;">Estética de Luxo & Durabilidade</div>
            <h1>A excelência e a arte em cada detalhe das suas mãos.</h1>
            <p>Alongamentos impecáveis com acabamento fino, alta resistência e cursos práticos de capacitação para novas profissionais da beleza.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
            <div class="site-card" style="text-align: center;">
                <div style="font-size: 30px;">💎</div>
                <h4 style="color: #4c1d95; margin: 8px 0 4px 0;">Alongamento Natural</h4>
                <p style="font-size: 14px; color: #6b21a8; margin: 0;">Curvatura simétrica e estrutura resistente sem deixar a lâmina grossa.</p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class="site-card" style="text-align: center;">
                <div style="font-size: 30px;">🛡️</div>
                <h4 style="color: #4c1d95; margin: 8px 0 4px 0;">Biossegurança Total</h4>
                <p style="font-size: 14px; color: #6b21a8; margin: 0;">Materiais 100% esterilizados em autoclave e insumos de uso individual.</p>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
            <div class="site-card" style="text-align: center;">
                <div style="font-size: 30px;">🎓</div>
                <h4 style="color: #4c1d95; margin: 8px 0 4px 0;">Formação Prática</h4>
                <p style="font-size: 14px; color: #6b21a8; margin: 0;">Turmas com limite reduzido de alunas para aprendizado direto de bancada.</p>
            </div>
        """, unsafe_allow_html=True)

# =======================================================
# PÁGINA 2: SERVIÇOS
# =======================================================
elif aba_selecionada == "💅 Serviços & Valores":
    st.markdown("### 💅 Procedimentos Disponíveis")
    st.caption("Consulte os serviços realizados com padrão de excelência.")

    conn = get_connection()
    servicos_df = pd.read_sql_query("SELECT * FROM servicos", conn)
    conn.close()

    colunas = st.columns(len(servicos_df))
    for idx, srv in servicos_df.iterrows():
        with colunas[idx]:
            st.markdown(f"""
                <div class="site-card">
                    <span style="font-size: 12px; font-weight: 700; color: #7e22ce; background: #faf5ff; padding: 4px 10px; border-radius: 12px;">⏱ {srv['duracao_minutos']} Minutos</span>
                    <h3>{srv['nome_servico']}</h3>
                    <p style="font-size: 14px; color: #6b21a8;">Higienização profunda, acabamento refinado e top coat de alto brilho.</p>
                    <div class="card-price-value">R$ {srv['preco']:.2f}</div>
                </div>
            """, unsafe_allow_html=True)

# =======================================================
# PÁGINA 3: CURSOS
# =======================================================
elif aba_selecionada == "🎓 Cursos & Turmas":
    st.markdown("### 🎓 Formação Profissional em Nail Design")
    st.caption("Aprenda do zero ou aperfeiçoe suas técnicas com acompanhamento individual.")

    conn = get_connection()
    turmas_df = pd.read_sql_query("SELECT * FROM turmas_curso WHERE status = 'Aberta'", conn)

    cols = st.columns(len(turmas_df) if len(turmas_df) > 0 else 1)
    for idx, turma in turmas_df.iterrows():
        t_id = turma['id']
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM inscricoes_curso WHERE turma_id = ? AND tipo_vaga = 'Titular'", (t_id,))
        titulares = c.fetchone()[0]
        vagas_restantes = turma['vagas_limite'] - titulares

        c.execute("SELECT COUNT(*) FROM inscricoes_curso WHERE turma_id = ? AND tipo_vaga = 'Reserva'", (t_id,))
        fila_reserva = c.fetchone()[0]

        with cols[idx]:
            st.markdown('<div class="site-card">', unsafe_allow_html=True)
            if vagas_restantes > 0:
                st.markdown(f'<span class="badge-vagas-abertas">🟢 Vagas Abertas ({vagas_restantes} de {turma["vagas_limite"]})</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="badge-reserva-aberta">🟡 Turma Cheia (Fila de Espera: {fila_reserva})</span>', unsafe_allow_html=True)

            st.markdown(f"""
                <h3 style="margin-top: 10px;">{turma['nome_curso']}</h3>
                <div style="font-size: 13px; color: #6b21a8; margin-bottom: 8px;">📅 Início: {turma['data_inicio']} • ⏱ {turma['horario']}</div>
                <div class="card-price-value">R$ {turma['preco_curso']:.2f}</div>
            """, unsafe_allow_html=True)

            with st.expander("Inscrever-se Nesta Turma"):
                with st.form(f"form_curso_{t_id}"):
                    nome_aluna = st.text_input("Nome Completo:")
                    tel_aluna = st.text_input("WhatsApp (DDD + Número):", placeholder="Ex: 71999999999")
                    experiencia = st.selectbox("Seu Nível Atual:", ["Iniciante do Zero", "Já atuo como Manicure", "Nail Designer em Aperfeiçoamento"])
                    
                    texto_btn = "Garantir Vaga Titular" if vagas_restantes > 0 else "Entrar na Lista de Espera"
                    btn_enviar_curso = st.form_submit_button(texto_btn, use_container_width=True)

                if btn_enviar_curso:
                    tel_limpo = ''.join(filter(str.isdigit, tel_aluna.strip()))
                    if not nome_aluna.strip() or len(tel_limpo) < 10:
                        st.error("Informe seu nome e WhatsApp completo com DDD.")
                    else:
                        if vagas_restantes > 0:
                            c.execute('''
                                INSERT INTO inscricoes_curso (turma_id, nome_aluna, telefone, experiencia_previa, tipo_vaga, posicao_reserva)
                                VALUES (?, ?, ?, ?, 'Titular', 0)
                            ''', (t_id, nome_aluna.strip(), tel_limpo, experiencia))
                            conn.commit()
                            st.success("🎉 Inscrição confirmada como Titular! A gestora entrará em contato via WhatsApp.")
                        else:
                            nova_pos = fila_reserva + 1
                            c.execute('''
                                INSERT INTO inscricoes_curso (turma_id, nome_aluna, telefone, experiencia_previa, tipo_vaga, posicao_reserva)
                                VALUES (?, ?, ?, ?, 'Reserva', ?)
                            ''', (t_id, nome_aluna.strip(), tel_limpo, experiencia, nova_pos))
                            conn.commit()
                            st.warning(f"📌 Turma lotada! Você foi incluída na {nova_pos}ª posição da reserva. Avisaremos caso surjam desistências.")
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
    conn.close()

# =======================================================
# PÁGINA 4: AGENDAR HORÁRIO (PORTAL DA CLIENTE)
# =======================================================
elif aba_selecionada == "📅 Agendar Horário":
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT valor FROM configuracoes WHERE chave = 'agenda_status'")
    status_agenda = c.fetchone()[0]

    c.execute("SELECT valor FROM configuracoes WHERE chave = 'mes_liberado'")
    mes_liberado_chave = c.fetchone()[0]
    conn.close()

    ano_lib, mes_lib = mes_liberado_chave.split("-")
    meses_pt = {
        "01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril",
        "05": "Maio", "06": "Junho", "07": "Julho", "08": "Agosto",
        "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro"
    }
    nome_mes_liberado = f"{meses_pt.get(mes_lib, mes_lib)} de {ano_lib}"

    st.markdown("### 📅 Solicitação de Agendamento Online")

    if status_agenda == "Fechada":
        st.warning("🔒 Nossa agenda de atendimentos está temporariamente fechada para novos horários online.")
    else:
        st.info(f"🗓️ **Atenção:** A agenda está atualmente aberta exclusivamente para agendamentos do mês de **{nome_mes_liberado}**.")

        conn = get_connection()
        servicos_df = pd.read_sql_query("SELECT * FROM servicos", conn)
        conn.close()

        with st.form("form_site_agendamento"):
            col1, col2 = st.columns(2)
            with col1:
                nome_c = st.text_input("Seu Nome Completo:")
                tel_c = st.text_input("Seu WhatsApp com DDD (apenas números):", placeholder="Ex: 71999999999")
                nasc_c = st.date_input("Data de Nascimento:", value=datetime(2000, 1, 1), min_value=datetime(1940, 1, 1))

            with col2:
                opcoes_servicos = {f"{row['nome_servico']} — R$ {row['preco']:.2f} ({row['duracao_minutos']} min)": row['id'] for _, row in servicos_df.iterrows()}
                srv_escolhido = st.selectbox("Procedimento Desejado:", list(opcoes_servicos.keys()))
                data_atend = st.date_input("Data Desejada:", min_value=datetime.today())
                hora_atend = st.time_input("Horário Desejado:", value=datetime.strptime("09:00", "%H:%M").time())
                observacao = st.text_area("Observações (opcional):", placeholder="Ex: Alongamento inicial, formato amendoado...")

            btn_agendar = st.form_submit_button("Solicitar Agendamento ✨", use_container_width=True)

        if btn_agendar:
            tel_limpo = ''.join(filter(str.isdigit, tel_c.strip()))
            mes_escolhido_cliente = data_atend.strftime("%Y-%m")

            if not nome_c.strip() or len(tel_limpo) < 10:
                st.error("Informe seu nome e WhatsApp válido com DDD.")
            elif mes_escolhido_cliente != mes_liberado_chave:
                st.error(f"⛔ Data indisponível! A agenda está aberta apenas para o mês de **{nome_mes_liberado}**. Por favor, escolha uma data dentro deste período.")
            else:
                conn = get_connection()
                c = conn.cursor()
                c.execute('''
                    INSERT INTO clientes (nome, telefone, data_nascimento, data_cadastro)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(telefone) DO UPDATE SET
                        nome = excluded.nome,
                        data_nascimento = excluded.data_nascimento
                ''', (nome_c.strip(), tel_limpo, str(nasc_c), datetime.now().strftime("%Y-%m-%d")))
                
                c.execute("SELECT id FROM clientes WHERE telefone = ?", (tel_limpo,))
                c_id = c.fetchone()[0]

                s_id = opcoes_servicos[srv_escolhido]
                data_hora_txt = f"{data_atend.strftime('%Y-%m-%d')} {hora_atend.strftime('%H:%M')}"

                c.execute('''
                    INSERT INTO agendamentos (cliente_id, servico_id, data_hora, status, observacoes)
                    VALUES (?, ?, ?, 'Pendente', ?)
                ''', (c_id, s_id, data_hora_txt, observacao.strip()))

                conn.commit()
                conn.close()

                st.success("✨ Sua solicitação de agendamento foi registrada com sucesso!")
                st.info("Assim que a gestora analisar a disponibilidade, você receberá a confirmação oficial diretamente no seu WhatsApp.")

# =======================================================
# PÁGINA 5: PAINEL DA GESTORA
# =======================================================
elif aba_selecionada == "🔐 Acesso Gestora":
    st.markdown("### 🔐 Painel Administrativo da Gestora")

    if "gestora_logada" not in st.session_state:
        st.session_state.gestora_logada = False

    if not st.session_state.gestora_logada:
        with st.form("form_login_gestora"):
            senha_digitada = st.text_input("Senha de Acesso:", type="password")
            btn_login = st.form_submit_button("Entrar no Painel", use_container_width=True)
            if btn_login:
                if senha_digitada == SENHA_MESTRE:
                    st.session_state.gestora_logada = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
    else:
        col_t1, col_t2 = st.columns([4, 1])
        with col_t1:
            st.success("Sessão da gestora conectada com segurança.")
        with col_t2:
            if st.button("Sair"):
                st.session_state.gestora_logada = False
                st.rerun()

        adm1, adm2, adm3, adm4, adm5 = st.tabs([
            "📊 Faturamento & Métricas",
            "📋 Gestão da Agenda",
            "🗂️ Prontuário & Histórico de Clientes",
            "🎓 Turmas de Cursos",
            "💌 CRM & Retenção"
        ])

        conn = get_connection()
        c = conn.cursor()

        # SUB-ABA 1: FATURAMENTO
        with adm1:
            st.markdown("#### 📈 Balanço de Atendimentos e Faturamento")
            st.caption("Estatísticas calculadas a partir dos procedimentos finalizados com status 'Concluído'.")

            query_concluidos = '''
                SELECT a.id, a.data_hora, s.preco, s.nome_servico, c.nome as cliente
                FROM agendamentos a
                JOIN servicos s ON a.servico_id = s.id
                JOIN clientes c ON a.cliente_id = c.id
                WHERE a.status = 'Concluído'
            '''
            df_concluidos = pd.read_sql_query(query_concluidos, conn)

            hoje_str = datetime.now().strftime("%Y-%m-%d")
            sete_dias_atras = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            mes_atual_prefix = datetime.now().strftime("%Y-%m")

            if df_concluidos.empty:
                st.info("Nenhum atendimento concluído para gerar estatísticas.")
            else:
                df_concluidos['data_apenas'] = df_concluidos['data_hora'].str.slice(0, 10)
                df_concluidos['mes_ano'] = df_concluidos['data_hora'].str.slice(0, 7)

                df_dia = df_concluidos[df_concluidos['data_apenas'] == hoje_str]
                qtd_dia = len(df_dia)
                lucro_dia = df_dia['preco'].sum()

                df_semana = df_concluidos[df_concluidos['data_apenas'] >= sete_dias_atras]
                qtd_semana = len(df_semana)
                lucro_semana = df_semana['preco'].sum()

                df_mes = df_concluidos[df_concluidos['mes_ano'] == mes_atual_prefix]
                qtd_mes = len(df_mes)
                lucro_mes = df_mes['preco'].sum()

                c_m1, c_m2, c_m3 = st.columns(3)
                with c_m1:
                    st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-label">📅 Hoje</div>
                            <div class="metric-value">R$ {lucro_dia:.2f}</div>
                            <div class="metric-sub">{qtd_dia} atendimento(s)</div>
                        </div>
                    """, unsafe_allow_html=True)
                with c_m2:
                    st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-label">🗓️ Últimos 7 Dias</div>
                            <div class="metric-value">R$ {lucro_semana:.2f}</div>
                            <div class="metric-sub">{qtd_semana} atendimento(s)</div>
                        </div>
                    """, unsafe_allow_html=True)
                with c_m3:
                    st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-label">📊 Mês Corrente</div>
                            <div class="metric-value">R$ {lucro_mes:.2f}</div>
                            <div class="metric-sub">{qtd_mes} atendimento(s)</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.write("")
                st.markdown("##### 🔍 Detalhamento dos Últimos Serviços Concluídos")
                st.dataframe(
                    df_concluidos[['data_hora', 'cliente', 'nome_servico', 'preco']].rename(
                        columns={'data_hora': 'Data/Hora', 'cliente': 'Cliente', 'nome_servico': 'Procedimento', 'preco': 'Valor (R$)'}
                    ),
                    use_container_width=True,
                    hide_index=True
                )

        # SUB-ABA 2: GESTÃO DA AGENDA
        with adm2:
            st.markdown("#### ⚙️ Controle e Liberação da Agenda")

            c.execute("SELECT valor FROM configuracoes WHERE chave = 'agenda_status'")
            status_atual = c.fetchone()[0]

            col_cf1, col_cf2 = st.columns(2)
            with col_cf1:
                novo_status = st.toggle("Agenda Geral Aberta para Clientes", value=(status_atual == "Aberta"))
                valor_toggle = "Aberta" if novo_status else "Fechada"
                if valor_toggle != status_atual:
                    c.execute("UPDATE configuracoes SET valor = ? WHERE chave = 'agenda_status'", (valor_toggle,))
                    conn.commit()
                    st.toast(f"Status geral: {valor_toggle}!")
                    st.rerun()

            with col_cf2:
                c.execute("SELECT valor FROM configuracoes WHERE chave = 'mes_liberado'")
                mes_lib_atual = c.fetchone()[0]

                opcoes_meses = {
                    "2026-09": "Setembro / 2026",
                    "2026-10": "Outubro / 2026",
                    "2026-11": "Novembro / 2026",
                    "2026-12": "Dezembro / 2026",
                    "2027-01": "Janeiro / 2027",
                    "2027-02": "Fevereiro / 2027"
                }
                mes_selecionado = st.selectbox(
                    "Definir Mês Liberado para Agendamentos:",
                    options=list(opcoes_meses.keys()),
                    index=list(opcoes_meses.keys()).index(mes_lib_atual) if mes_lib_atual in opcoes_meses else 0,
                    format_func=lambda x: opcoes_meses.get(x, x)
                )

                if mes_selecionado != mes_lib_atual:
                    c.execute("UPDATE configuracoes SET valor = ? WHERE chave = 'mes_liberado'", (mes_selecionado,))
                    conn.commit()
                    st.toast(f"Agenda liberada para: {opcoes_meses[mes_selecionado]}!")
                    st.rerun()

            st.divider()

            # =======================================================
            # BLOCO DESTACADO: BOTÃO VERDE DO WHATSAPP DA GESTORA
            # =======================================================
            if "confirmacao_pendente" in st.session_state and st.session_state["confirmacao_pendente"]:
                d = st.session_state["confirmacao_pendente"]
                msg_confirmacao = (
                    f"Olá {d['nome']}! ✨ Passando para confirmar que o seu agendamento no *Studio Belleza & Arte* foi CONFIRMADO!\n\n"
                    f"💅 *Procedimento:* {d['servico']}\n"
                    f"📅 *Data e Horário:* {d['data_hora']}\n\n"
                    f"Estamos ansiosas para te receber! Qualquer imprevisto, é só nos avisar por aqui."
                )
                link_whatsapp_conf = f"https://api.whatsapp.com/send?phone=55{d['telefone']}&text={urllib.parse.quote(msg_confirmacao)}"

                st.markdown(f"""
                    <div class="zap-destaque-box">
                        <h4 style="color: #15803d; margin: 0 0 6px 0;">🎉 Horário de {d['nome']} Aprovado com Sucesso!</h4>
                        <p style="color: #166534; font-size: 14px; margin-bottom: 12px;">
                            Clique no botão abaixo para abrir a conversa no WhatsApp e notificar a cliente agora:
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                col_zap1, col_zap2 = st.columns([3, 1])
                with col_zap1:
                    st.link_button(f"📲 Enviar Mensagem de Confirmação para {d['nome']} no WhatsApp", link_whatsapp_conf)
                with col_zap2:
                    if st.button("Fechar Alerta", key="btn_fechar_zap"):
                        st.session_state["confirmacao_pendente"] = None
                        st.rerun()

                st.divider()

            # LISTA DE SOLICITAÇÕES PENDENTES
            st.markdown("#### ⏳ Solicitações Pendentes de Aprovação")
            pendentes = pd.read_sql_query('''
                SELECT a.id, c.nome, c.telefone, s.nome_servico, a.data_hora, a.observacoes
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN servicos s ON a.servico_id = s.id
                WHERE a.status = 'Pendente'
                ORDER BY a.data_hora ASC
            ''', conn)

            if pendentes.empty:
                st.info("Nenhuma solicitação de horário pendente no momento.")
            else:
                for _, ag in pendentes.iterrows():
                    ag_id = ag['id']
                    col_info, col_acao = st.columns([3, 2])
                    with col_info:
                        st.markdown(f"💅 **{ag['nome']}** — *{ag['nome_servico']}*")
                        st.caption(f"📅 Data/Hora Solicitada: **{ag['data_hora']}** | WhatsApp: **{ag['telefone']}**")
                        if ag['observacoes']:
                            st.caption(f"Obs: {ag['observacoes']}")

                    with col_acao:
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button("Aprovar Horário", key=f"ap_{ag_id}", use_container_width=True):
                                c.execute("UPDATE agendamentos SET status = 'Confirmado' WHERE id = ?", (ag_id,))
                                conn.commit()
                                # Salva na sessão e aciona o card com o botão verde no topo
                                st.session_state["confirmacao_pendente"] = {
                                    "nome": ag['nome'],
                                    "telefone": ag['telefone'],
                                    "servico": ag['nome_servico'],
                                    "data_hora": ag['data_hora']
                                }
                                st.toast("Horário Aprovado!")
                                st.rerun()

                        with btn_col2:
                            if st.button("Recusar", key=f"rec_{ag_id}", use_container_width=True):
                                c.execute("UPDATE agendamentos SET status = 'Cancelado' WHERE id = ?", (ag_id,))
                                conn.commit()
                                st.toast("Agendamento recusado!")
                                st.rerun()

                    st.write("")

            st.divider()

            # CONFIRMADOS (FINALIZAR)
            st.markdown("#### ✅ Atendimentos Confirmados (Finalizar)")
            confirmados = pd.read_sql_query('''
                SELECT a.id, c.nome, c.telefone, s.nome_servico, a.data_hora
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN servicos s ON a.servico_id = s.id
                WHERE a.status = 'Confirmado'
                ORDER BY a.data_hora ASC
            ''', conn)

            if confirmados.empty:
                st.caption("Nenhum atendimento confirmado aguardando realização.")
            else:
                for _, conf in confirmados.iterrows():
                    col_c1, col_c2 = st.columns([4, 1])
                    with col_c1:
                        st.write(f"💅 **{conf['nome']}** — {conf['nome_servico']} ({conf['data_hora']})")
                    with col_c2:
                        if st.button("Finalizar", key=f"conc_{conf['id']}", use_container_width=True):
                            c.execute("UPDATE agendamentos SET status = 'Concluído' WHERE id = ?", (conf['id'],))
                            conn.commit()
                            st.toast("Atendimento concluído e computado no faturamento!")
                            st.rerun()

        # SUB-ABA 3: HISTÓRICO E PRONTUÁRIO
        with adm3:
            st.markdown("#### 🗂️ Prontuário e Histórico de Atendimentos das Clientes")
            st.caption("Pesquise por uma cliente para analisar a frequência, procedimentos já feitos e total investido.")

            clientes_db = pd.read_sql_query("SELECT id, nome, telefone, data_nascimento FROM clientes ORDER BY nome ASC", conn)

            if clientes_db.empty:
                st.info("Nenhuma cliente cadastrada.")
            else:
                lista_nomes = {f"{row['nome']} ({row['telefone']})": row['id'] for _, row in clientes_db.iterrows()}
                cliente_selecionada = st.selectbox("Selecione a Cliente para Visualizar o Prontuário:", list(lista_nomes.keys()))
                id_cliente = lista_nomes[cliente_selecionada]

                query_hist = f'''
                    SELECT a.data_hora, s.nome_servico, s.preco, a.status, a.observacoes
                    FROM agendamentos a
                    JOIN servicos s ON a.servico_id = s.id
                    WHERE a.cliente_id = {id_cliente}
                    ORDER BY a.data_hora DESC
                '''
                df_hist = pd.read_sql_query(query_hist, conn)

                total_visitas = len(df_hist[df_hist['status'] == 'Concluído'])
                total_gasto = df_hist[df_hist['status'] == 'Concluído']['preco'].sum()
                procedimento_favorito = df_hist[df_hist['status'] == 'Concluído']['nome_servico'].mode()
                favorito_txt = procedimento_favorito[0] if not procedimento_favorito.empty else "Nenhum concluído"

                c_h1, c_h2, c_h3 = st.columns(3)
                c_h1.metric("Visitas Realizadas", f"{total_visitas} sessão(ões)")
                c_h2.metric("Total Investido no Studio", f"R$ {total_gasto:.2f}")
                c_h3.metric("Procedimento Favorito", favorito_txt)

                st.write("")
                st.markdown("##### 📜 Histórico Cronológico de Sessões")
                if df_hist.empty:
                    st.caption("Esta cliente ainda não possui histórico registrado.")
                else:
                    st.dataframe(
                        df_hist.rename(columns={
                            'data_hora': 'Data/Hora',
                            'nome_servico': 'Procedimento',
                            'preco': 'Valor (R$)',
                            'status': 'Status',
                            'observacoes': 'Anotações Técnicas'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

        # SUB-ABA 4: CURSOS & RESERVA
        with adm4:
            st.markdown("#### 🎓 Gestão de Turmas e Lista de Reserva")
            turmas_cadastradas = pd.read_sql_query("SELECT * FROM turmas_curso", conn)
            for _, t_item in turmas_cadastradas.iterrows():
                turma_id_adm = t_item['id']
                st.markdown(f"**{t_item['nome_curso']}** (Limite: {t_item['vagas_limite']} alunas)")
                
                inscritas_t = pd.read_sql_query(f"SELECT id, nome_aluna, telefone FROM inscricoes_curso WHERE turma_id = {turma_id_adm} AND tipo_vaga = 'Titular'", conn)
                reservas_t = pd.read_sql_query(f"SELECT id, nome_aluna, telefone, posicao_reserva FROM inscricoes_curso WHERE turma_id = {turma_id_adm} AND tipo_vaga = 'Reserva' ORDER BY posicao_reserva ASC", conn)

                col_titu, col_res = st.columns(2)
                with col_titu:
                    st.caption(f"Titulares ({len(inscritas_t)} de {t_item['vagas_limite']}):")
                    if not inscritas_t.empty:
                        st.dataframe(inscritas_t, hide_index=True, use_container_width=True)
                    else:
                        st.caption("Nenhuma titular inscrita.")

                with col_res:
                    st.caption(f"Fila de Reserva ({len(reservas_t)} alunas):")
                    if not reservas_t.empty:
                        st.dataframe(reservas_t, hide_index=True, use_container_width=True)
                        if st.button("Promover 1ª da Reserva para Titular", key=f"prom_{turma_id_adm}"):
                            primeira_reserva_id = reservas_t.iloc[0]['id']
                            c.execute("UPDATE inscricoes_curso SET tipo_vaga = 'Titular', posicao_reserva = 0 WHERE id = ?", (int(primeira_reserva_id),))
                            conn.commit()
                            st.toast("Aluna promovida para titular!")
                            st.rerun()
                    else:
                        st.caption("Fila vazia.")
                st.write("")

        # SUB-ABA 5: CRM
        with adm5:
            st.markdown("#### ⏳ Lembretes de Retorno (15 e 30 dias)")
            atendimentos_concluidos = pd.read_sql_query('''
                SELECT c.nome, c.telefone, s.nome_servico, a.data_hora,
                       CAST((julianday('now') - julianday(a.data_hora)) AS INTEGER) as dias_decorridos
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN servicos s ON a.servico_id = s.id
                WHERE a.status = 'Concluído'
            ''', conn)

            encontrou_lembrete = False
            for _, item in atendimentos_concluidos.iterrows():
                dias = item['dias_decorridos']
                if dias in [14, 15, 16, 29, 30, 31]:
                    encontrou_lembrete = True
                    msg = f"Olá {item['nome']}! Já fazem {dias} dias desde o seu procedimento de {item['nome_servico']} no Studio Belleza & Arte. Vamos agendar sua manutenção para manter suas unhas impecáveis?"
                    link_zap = f"https://api.whatsapp.com/send?phone=55{item['telefone']}&text={urllib.parse.quote(msg)}"

                    st.info(f"💅 **{item['nome']}** completou **{dias} dias** ({item['nome_servico']})")
                    st.link_button(f"📲 Chamar no WhatsApp ({item['telefone']})", link_zap)

            if not encontrou_lembrete:
                st.info("Nenhuma cliente no ciclo exato de 15 ou 30 dias na data de hoje.")

            st.divider()
            st.markdown("#### 🎂 Aniversariantes do Dia")
            hoje_md = datetime.now().strftime("%m-%d")
            aniversariantes = pd.read_sql_query(f"SELECT nome, telefone FROM clientes WHERE strftime('%m-%d', data_nascimento) = '{hoje_md}'", conn)

            if aniversariantes.empty:
                st.info("Nenhuma aniversariante para a data de hoje.")
            else:
                for _, niver in aniversariantes.iterrows():
                    msg_niver = f"Parabéns, {niver['nome']}! 💅 O Studio Belleza & Arte deseja a você um feliz aniversário! Preparamos um mimo especial para o seu próximo atendimento."
                    link_niver = f"https://api.whatsapp.com/send?phone=55{niver['telefone']}&text={urllib.parse.quote(msg_niver)}"
                    st.success(f"🎉 **{niver['nome']}** comemora aniversário hoje!")
                    st.link_button(f"🎂 Enviar Mimo via WhatsApp", link_niver)

        conn.close()

# =======================================================
# RODAPÉ
# =======================================================
st.markdown("""
    <div class="site-footer">
        <b>Studio Belleza & Arte</b> • Todos os direitos reservados.<br>
        <span style="opacity: 0.8;">Alongamento em Gel • Nail Art • Formação Profissional</span>
    </div>
""", unsafe_allow_html=True)