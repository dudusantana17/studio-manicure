import streamlit as st
import sqlite3
import json
import os
from datetime import datetime
import pandas as pd
import pypdf
import io

# Tentar importar google.genai para o módulo do instrutor
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# ==========================================
# CONFIGURAÇÃO DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Marinha do Brasil - Escola de Formação de Recrutas",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# BANCO DE DADOS LOCAL (SQLite)
# ==========================================
DB_FILE = "simulado_recrutas.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Tabela de questões
    c.execute('''
        CREATE TABLE IF NOT EXISTS questoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia TEXT NOT NULL,
            enunciado TEXT NOT NULL,
            opcoes_json TEXT NOT NULL,
            correta TEXT NOT NULL,
            explicacao TEXT NOT NULL
        )
    ''')
    # Tabela de ranking / tentativas
    c.execute('''
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_guerra TEXT NOT NULL,
            materia TEXT NOT NULL,
            acertos INTEGER NOT NULL,
            total INTEGER NOT NULL,
            porcentagem REAL NOT NULL,
            data_hora TEXT NOT NULL
        )
    ''')
    
    # Inserir questões iniciais se a tabela estiver vazia
    c.execute("SELECT COUNT(*) FROM questoes")
    if c.fetchone()[0] == 0:
        questoes_iniciais = [
            (
                "RDM (Regulamento Disciplinar)",
                "Qual é o prazo regulamentar para apresentação de recurso disciplinar após a publicação formal da punição?",
                json.dumps({
                    "A": "24 horas úteis",
                    "B": "48 horas corridas",
                    "C": "5 dias úteis",
                    "D": "8 dias corridos"
                }, ensure_ascii=False),
                "D",
                "Conforme os preceitos regulamentares disciplinares, o prazo legal para interposição de recurso é de 8 dias contados da ciência formal da publicação da punição."
            ),
            (
                "RDM (Regulamento Disciplinar)",
                "A transgressão disciplinar militar classifica-se quanto à sua gravidade estritamente em:",
                json.dumps({
                    "A": "Leve, média e grave",
                    "B": "Simples, qualificada e gravíssima",
                    "C": "Primária, secundária e terciária",
                    "D": "Culposa e dolosa apenas"
                }, ensure_ascii=False),
                "A",
                "As transgressões disciplinares militares dividem-se legalmente quanto à intensidade em: leve, média e grave, influenciando diretamente na dosimetria da sanção aplicada."
            ),
            (
                "Armamento e Tiro",
                "Ao receber qualquer armamento em linha de tiro ou na rendição de serviço de quarto de guarda, a primeira conduta inegociável de segurança é:",
                json.dumps({
                    "A": "Apertar o gatilho a seco para inspecionar a percussão do cão",
                    "B": "Apontar para direção segura, retirar o carregador e inspecionar visual e tatilmente a câmara",
                    "C": "Desmontar as peças móveis do conjunto do ferrolho",
                    "D": "Engatilhar o armamento sucessivas vezes para conferir o curso"
                }, ensure_ascii=False),
                "B",
                "A regra capital de segurança em armamento exige: apontar para local seguro, desconectar a fonte de alimentação (carregador) e inspecionar visual e tatilmente a câmara de explosão."
            ),
            (
                "Armamento e Tiro",
                "Em relação aos fundamentos básicos do tiro de precisão militar, qual alternativa representa a correta sequência e execução?",
                json.dumps({
                    "A": "Postura, empunhadura, visada, controle da respiração e acionamento progressivo e suave do gatilho",
                    "B": "Acionamento rápido, visada binocular rápida e recuo antecipado",
                    "C": "Respiração profunda contínua e acionamento brusco do disparador",
                    "D": "Fixação exclusiva no alvo e relaxamento total da empunhadura"
                }, ensure_ascii=False),
                "A",
                "Os fundamentos clássicos de tiro exigem base estável, empunhadura firme e consistente, alinhamento rigoroso dos aparelhos de pontaria (alça e massa), pausa respiratória e pressão progressiva no gatilho sem alterar a visada (gatilhada zero)."
            )
        ]
        c.executemany('''
            INSERT INTO questoes (materia, enunciado, opcoes_json, correta, explicacao)
            VALUES (?, ?, ?, ?, ?)
        ''', questoes_iniciais)
        
    conn.commit()
    conn.close()

init_db()

# ==========================================
# CSS CUSTOMIZADO (IDENTIDADE VISUAL MARINHA DO BRASIL)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Cores Institucionais - Marinha do Brasil */
    :root {
        --azul-marinho-profundo: #002147;
        --azul-marinho-noite: #0a192f;
        --azul-aco: #1b3a57;
        --dourado-naval: #d4af37;
        --dourado-claro: #f3e5ab;
        --branco-puro: #ffffff;
        --cinza-nautico: #f4f7fb;
        --cinza-borda: #cbd5e1;
    }

    /* Banner Principal - Marinha do Brasil */
    .header-box {
        background: linear-gradient(135deg, #001733 0%, #002147 45%, #0a2540 80%, #102a45 100%);
        color: #ffffff;
        padding: 26px 32px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 33, 71, 0.4), 0 8px 10px -6px rgba(0, 33, 71, 0.25);
        border: 1px solid rgba(212, 175, 55, 0.35);
        border-bottom: 4px solid #d4af37;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-brasao {
        font-size: 46px;
        margin-right: 18px;
        filter: drop-shadow(0 2px 5px rgba(0,0,0,0.5));
    }
    .header-box h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.3px;
        color: #ffffff;
        text-transform: uppercase;
    }
    .header-box h2 {
        margin: 4px 0 0 0;
        font-size: 15px;
        font-weight: 600;
        color: #f3e5ab;
        letter-spacing: 0.2px;
    }
    .header-box p {
        margin: 5px 0 0 0;
        opacity: 0.88;
        font-size: 13.5px;
        color: #cbd5e1;
    }
    .header-badge {
        background: rgba(212, 175, 55, 0.15);
        color: #fde68a;
        border: 1px solid #d4af37;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    /* Abas estilizadas */
    button[data-baseweb="tab"] {
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px 20px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #002147 !important;
        border-bottom-color: #d4af37 !important;
    }

    /* Cards de Questões */
    .questao-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #002147;
        border-radius: 10px;
        padding: 18px 22px;
        margin-top: 15px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0, 33, 71, 0.04);
    }
    .questao-badge {
        display: inline-block;
        background-color: #f0f4f8;
        color: #002147;
        font-size: 12px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 6px;
        margin-bottom: 8px;
        border: 1px solid #d4af37;
    }
    .questao-enunciado {
        font-size: 15.5px;
        font-weight: 600;
        color: #0f172a;
        line-height: 1.55;
    }

    /* Alternativas (Radios) */
    div[data-testid="stRadio"] > div {
        gap: 8px;
        padding: 4px 0 12px 0;
    }
    div[data-testid="stRadio"] label {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 12px 16px;
        border-radius: 8px;
        transition: all 0.2s ease;
        cursor: pointer;
        width: 100%;
        color: #0f172a;
        font-size: 14.5px;
    }
    div[data-testid="stRadio"] label:hover {
        background: #f0f4f8;
        border-color: #002147;
        transform: translateX(2px);
    }

    /* Botão Primário Naval */
    .stButton > button {
        background: linear-gradient(135deg, #002147 0%, #1b3a57 100%);
        color: #ffffff !important;
        font-weight: 700;
        font-size: 15px;
        border-radius: 8px;
        padding: 0.65rem 1.4rem;
        border: 1px solid rgba(212, 175, 55, 0.4);
        box-shadow: 0 4px 12px rgba(0, 33, 71, 0.25);
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0a192f 0%, #002147 100%);
        border-color: #d4af37;
        box-shadow: 0 6px 16px rgba(0, 33, 71, 0.35);
        transform: translateY(-1px);
    }

    /* Cards do Pódio Naval */
    .podio-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 33, 71, 0.06);
    }
    .podio-ouro { border-top: 5px solid #d4af37; background: linear-gradient(180deg, #fffdf0 0%, #ffffff 60%); }
    .podio-prata { border-top: 5px solid #94a3b8; background: linear-gradient(180deg, #f8fafc 0%, #ffffff 60%); }
    .podio-bronze { border-top: 5px solid #cd7f32; background: linear-gradient(180deg, #fef7f0 0%, #ffffff 60%); }
    
    .podio-pos { font-size: 32px; margin-bottom: 6px; }
    .podio-nome { font-weight: 800; font-size: 17px; color: #0f172a; margin-bottom: 2px; }
    .podio-media { font-size: 24px; font-weight: 800; color: #002147; }
    .podio-detalhe { font-size: 12px; color: #64748b; margin-top: 4px; font-weight: 500; }

    /* Cards de Estatísticas e Métricas */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #002147;
        padding: 16px 20px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0, 33, 71, 0.04);
    }

    .mil-alert-warn {
        background-color: #fffdf0;
        border-left: 4px solid #d4af37;
        padding: 14px 18px;
        border-radius: 8px;
        color: #78350f;
        margin: 12px 0;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# BANNER HERO INSTITUCIONAL (MARINHA DO BRASIL)
# ==========================================
st.markdown("""
    <div class="header-box">
        <div style="display: flex; align-items: center;">
            <div class="header-brasao">⚓</div>
            <div>
                <h1>Marinha do Brasil</h1>
                <h2>Escola de Formação de Recrutas • EAM / CIAGA</h2>
                <p>Portal de Instrução Militar e Simulados de Formação Doutrinária</p>
            </div>
        </div>
        <div class="header-badge">⚓ Tradição & Prontidão Naval</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# ESTRUTURA DE ABAS PRINCIPAIS
# ==========================================
aba_recruta, aba_ranking, aba_instrutor = st.tabs([
    "📝 Área do Recruta (Simulados)",
    "🏆 Quadro de Honra (Ranking)",
    "🎖️ Área do Instrutor (Upload & IA)"
])

# ==============================================================================
# MÓDULO 1: ÁREA DO RECRUTA (SIMULADOS)
# ==============================================================================
with aba_recruta:
    st.markdown("### 📋 Caderno de Avaliação Teórica")
    
    col_rec1, col_rec2 = st.columns([1, 1])
    with col_rec1:
        nome_recruta = st.text_input(
            "Identificação (Nome de Guerra / Matrícula):",
            placeholder="Ex: SD SILVA / 123456",
            key="input_nome_recruta"
        ).strip().upper()

    conn = get_db_connection()
    materias_disponiveis = [row["materia"] for row in conn.cursor().execute("SELECT DISTINCT materia FROM questoes ORDER BY materia").fetchall()]
    conn.close()

    with col_rec2:
        if materias_disponiveis:
            materia_escolhida = st.selectbox(
                "Selecione a Disciplina / Módulo:",
                options=materias_disponiveis,
                key="select_materia_simulado"
            )
        else:
            materia_escolhida = None
            st.warning("Nenhuma matéria cadastrada no momento.")

    if not nome_recruta:
        st.info("ℹ️ Para iniciar o simulado, preencha sua identificação (Nome de Guerra ou Matrícula) acima.")
    elif not materia_escolhida:
        st.warning("⚠️ Solicite ao Instrutor o cadastro de módulos e questões para iniciar.")
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, materia, enunciado, opcoes_json, correta, explicacao FROM questoes WHERE materia = ? ORDER BY id ASC",
            (materia_escolhida,)
        )
        questoes_banco = cursor.fetchall()
        conn.close()

        if not questoes_banco:
            st.warning(f"Não há questões cadastradas para a matéria '{materia_escolhida}'.")
        else:
            st.markdown(f"**Total de Questões:** `{len(questoes_banco)}` | **Módulo:** `{materia_escolhida}` | **Instrução:** Leia atentamente cada item e selecione a alternativa correta.")
            st.write("---")

            # Form do simulado
            with st.form(key=f"form_simulado_{materia_escolhida}"):
                respostas_submetidas = {}
                
                for idx, row in enumerate(questoes_banco, start=1):
                    q_id = row["id"]
                    enunciado = row["enunciado"]
                    opcoes = json.loads(row["opcoes_json"])
                    correta = row["correta"]
                    explicacao = row["explicacao"]

                    st.markdown(f"""
                        <div class="questao-card">
                            <span class="questao-badge">Questão {idx:02d} / {len(questoes_banco):02d}</span>
                            <div class="questao-enunciado">{enunciado}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    opcoes_formatadas = [f"{letra}) {texto}" for letra, texto in sorted(opcoes.items())]
                    
                    escolha = st.radio(
                        label=f"Alternativas da questão {idx}",
                        options=opcoes_formatadas,
                        index=None,
                        key=f"radio_q_{q_id}",
                        label_visibility="collapsed"
                    )

                    respostas_submetidas[q_id] = {
                        "idx": idx,
                        "enunciado": enunciado,
                        "opcoes": opcoes,
                        "escolha": escolha[0] if escolha else None,
                        "escolha_texto": escolha if escolha else "Em branco",
                        "correta": correta,
                        "explicacao": explicacao
                    }

                st.write("")
                btn_finalizar = st.form_submit_button("🏁 Finalizar e Entregar Simulado", use_container_width=True)

            if btn_finalizar:
                # Validação: verificar se há questões em branco
                questoes_em_branco = [v["idx"] for v in respostas_submetidas.values() if v["escolha"] is None]

                if questoes_em_branco:
                    st.error(f"⚠️ **Atenção Recruta!** O simulado não pode ser entregue com questões em branco. Questões pendentes: **{', '.join([f'Questão {n:02d}' for n in questoes_em_branco])}**.")
                else:
                    total = len(questoes_banco)
                    acertos = sum(1 for v in respostas_submetidas.values() if v["escolha"] == v["correta"])
                    porcentagem = round((acertos / total) * 100, 1)
                    aprovado = porcentagem >= 70.0
                    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

                    # Gravar no ranking
                    conn = get_db_connection()
                    conn.execute('''
                        INSERT INTO ranking (nome_guerra, materia, acertos, total, porcentagem, data_hora)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (nome_recruta, materia_escolhida, acertos, total, porcentagem, data_hora))
                    conn.commit()
                    conn.close()

                    if aprovado:
                        st.balloons()
                    else:
                        st.snow()

                    # Painel de Métricas
                    st.markdown("### 📊 Relatório Individual de Desempenho")
                    m_col1, m_col2, m_col3 = st.columns(3)
                    with m_col1:
                        st.metric("Total de Acertos", f"{acertos} / {total}")
                    with m_col2:
                        st.metric("Aproveitamento", f"{porcentagem:.1f}%")
                    with m_col3:
                        status_txt = "APROVADO (APTO)" if aprovado else "RECUPERAÇÃO"
                        delta_txt = "Nota regulamentar" if aprovado else "Abaixo de 70%"
                        st.metric("Parecer Final", status_txt, delta=delta_txt)

                    if aprovado:
                        st.success(f"🎯 **Aprovado!** Excelente resultado, **{nome_recruta}**! Seu aproveitamento foi de **{porcentagem:.1f}%** ({acertos}/{total} acertos) e atende aos padrões de formação militar. Sua pontuação foi gravada no Quadro de Honra.")
                    else:
                        st.error(f"⚠️ **Em Recuperação.** Recruta **{nome_recruta}**, seu aproveitamento foi de **{porcentagem:.1f}%** ({acertos}/{total} acertos), abaixo do padrão mínimo regulamentar de 70%. Estude as justificativas no gabarito comentado abaixo.")

                    # Gabarito Comentado Retrátil
                    st.write("---")
                    st.markdown("### 📋 Gabarito Comentado e Justificativas Técnicas")
                    
                    for q_id, dados in respostas_submetidas.items():
                        acertou = dados["escolha"] == dados["correta"]
                        icone = "✅" if acertou else "❌"
                        titulo_expander = f"{icone} Questão {dados['idx']:02d} — Sua resposta: [{dados['escolha']}] | Gabarito: [{dados['correta']}]"
                        
                        with st.expander(titulo_expander, expanded=(not acertou)):
                            st.markdown(f"**Enunciado:** {dados['enunciado']}")
                            st.markdown("**Alternativas:**")
                            for ltr, txt in sorted(dados["opcoes"].items()):
                                if ltr == dados["correta"]:
                                    st.markdown(f"- **{ltr}) {txt}** 🟢 *(Alternativa Correta)*")
                                elif ltr == dados["escolha"] and not acertou:
                                    st.markdown(f"- ~~{ltr}) {txt}~~ 🔴 *(Sua escolha incorreta)*")
                                else:
                                    st.markdown(f"- {ltr}) {txt}")

                            st.info(f"💡 **Fundamentação Técnica / Justificativa:**\n\n{dados['explicacao']}")


# ==============================================================================
# MÓDULO 2: QUADRO DE HONRA (RANKING)
# ==============================================================================
with aba_ranking:
    st.markdown("### 🏆 Quadro de Honra & Classificação Geral")
    st.markdown("Acompanhamento contínuo da prontidão doutrinária e rendimento dos militares.")

    conn = get_db_connection()
    materias_ranking = [row["materia"] for row in conn.cursor().execute("SELECT DISTINCT materia FROM ranking ORDER BY materia").fetchall()]
    conn.close()

    opcoes_filtro = ["🌐 Visão Geral Acumulada (Todas as Disciplinas)"] + materias_ranking
    filtro_selecionado = st.selectbox("Filtrar Classificação por Disciplina:", opcoes_filtro)

    conn = get_db_connection()
    cursor = conn.cursor()

    if filtro_selecionado == "🌐 Visão Geral Acumulada (Todas as Disciplinas)":
        cursor.execute('''
            SELECT 
                nome_guerra as recruta,
                COUNT(id) as simulados_feitos,
                SUM(acertos) as total_acertos,
                SUM(total) as total_questoes,
                ROUND(AVG(porcentagem), 1) as media_aproveitamento,
                MAX(data_hora) as ultima_atividade
            FROM ranking
            GROUP BY nome_guerra
            ORDER BY media_aproveitamento DESC, total_acertos DESC
        ''')
    else:
        cursor.execute('''
            SELECT 
                nome_guerra as recruta,
                COUNT(id) as simulados_feitos,
                SUM(acertos) as total_acertos,
                SUM(total) as total_questoes,
                ROUND(AVG(porcentagem), 1) as media_aproveitamento,
                MAX(data_hora) as ultima_atividade
            FROM ranking
            WHERE materia = ?
            GROUP BY nome_guerra
            ORDER BY media_aproveitamento DESC, total_acertos DESC
        ''', (filtro_selecionado,))
    
    dados_ranking = cursor.fetchall()
    conn.close()

    if not dados_ranking:
        st.info("ℹ️ Ainda não há registros de simulados finalizados para este filtro.")
    else:
        # Pódio Top 3
        st.write("")
        col_pod1, col_pod2, col_pod3 = st.columns(3)
        
        # 1º Lugar (Ouro)
        if len(dados_ranking) >= 1:
            primeiro = dados_ranking[0]
            with col_pod1:
                st.markdown(f"""
                    <div class="podio-card podio-ouro">
                        <div class="podio-pos">🥇</div>
                        <div class="podio-nome">{primeiro['recruta']}</div>
                        <div class="podio-media">{primeiro['media_aproveitamento']}%</div>
                        <div class="podio-detalhe">1º Lugar Geral • {primeiro['total_acertos']} acertos ({primeiro['simulados_feitos']} sim.)</div>
                    </div>
                """, unsafe_allow_html=True)
        
        # 2º Lugar (Prata)
        if len(dados_ranking) >= 2:
            segundo = dados_ranking[1]
            with col_pod2:
                st.markdown(f"""
                    <div class="podio-card podio-prata">
                        <div class="podio-pos">🥈</div>
                        <div class="podio-nome">{segundo['recruta']}</div>
                        <div class="podio-media">{segundo['media_aproveitamento']}%</div>
                        <div class="podio-detalhe">2º Lugar Geral • {segundo['total_acertos']} acertos ({segundo['simulados_feitos']} sim.)</div>
                    </div>
                """, unsafe_allow_html=True)
        
        # 3º Lugar (Bronze)
        if len(dados_ranking) >= 3:
            terceiro = dados_ranking[2]
            with col_pod3:
                st.markdown(f"""
                    <div class="podio-card podio-bronze">
                        <div class="podio-pos">🥉</div>
                        <div class="podio-nome">{terceiro['recruta']}</div>
                        <div class="podio-media">{terceiro['media_aproveitamento']}%</div>
                        <div class="podio-detalhe">3º Lugar Geral • {terceiro['total_acertos']} acertos ({terceiro['simulados_feitos']} sim.)</div>
                    </div>
                """, unsafe_allow_html=True)

        st.write("")
        st.markdown("#### 📑 Classificação Geral da Tropa")

        tabela_ranking = []
        for rank_pos, r in enumerate(dados_ranking, start=1):
            badge_pos = f"{rank_pos}º"
            if rank_pos == 1:
                badge_pos = "🥇 1º"
            elif rank_pos == 2:
                badge_pos = "🥈 2º"
            elif rank_pos == 3:
                badge_pos = "🥉 3º"

            tabela_ranking.append({
                "Posição": badge_pos,
                "Nome de Guerra / Matrícula": r["recruta"],
                "Simulados Feitos": r["simulados_feitos"],
                "Total de Acertos": f"{r['total_acertos']} / {r['total_questoes']}",
                "Média de Aproveitamento": f"{r['media_aproveitamento']}%",
                "Última Avaliação": r["ultima_atividade"]
            })

        df_rank = pd.DataFrame(tabela_ranking)
        st.dataframe(df_rank, use_container_width=True, hide_index=True)


# ==============================================================================
# MÓDULO 3: ÁREA DO INSTRUTOR (UPLOAD DE PDF E GERAÇÃO VIA IA)
# ==============================================================================
with aba_instrutor:
    st.markdown("### 🎖️ Divisão de Doutrina e Instrução")
    st.caption("Painel reservado ao corpo de instrução para gestão de conteúdo e geração automatizada de avaliações via IA.")

    # Senha de proteção
    SENHA_INSTRUTOR_CORRETA = "instrutor123"
    
    if "instrutor_autenticado" not in st.session_state:
        st.session_state["instrutor_autenticado"] = False

    if not st.session_state["instrutor_autenticado"]:
        st.markdown("""
            <div class="mil-alert-warn">
                🔒 <strong>Acesso Restrito:</strong> Esta área requer autenticação de oficial ou sargento instrutor.
            </div>
        """, unsafe_allow_html=True)
        
        col_senha, col_btn_auth = st.columns([2, 1])
        with col_senha:
            senha_digitada = st.text_input("Senha do Instrutor:", type="password", key="input_senha_inst")
        with col_btn_auth:
            st.write("")
            st.write("")
            if st.button("Liberar Acesso", use_container_width=True):
                if senha_digitada == SENHA_INSTRUTOR_CORRETA:
                    st.session_state["instrutor_autenticado"] = True
                    st.success("Acesso autorizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Senha incorreta. Acesso negado.")
    else:
        col_inst_top, col_logout = st.columns([4, 1])
        with col_inst_top:
            st.success("✅ **Instrutor autenticado em sessão ativa.**")
        with col_logout:
            if st.button("Encerrar Sessão", key="btn_logout_instrutor", use_container_width=True):
                st.session_state["instrutor_autenticado"] = False
                st.rerun()

        st.write("---")

        # Chave Gemini API lida prioritariamente de st.secrets
        gemini_key = ""
        try:
            if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
                gemini_key = str(st.secrets["GEMINI_API_KEY"]).strip()
        except Exception:
            pass

        if not gemini_key:
            gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()

        with st.expander("🔑 Configuração da Chave da API Google Gemini", expanded=(not bool(gemini_key))):
            if gemini_key:
                st.success("✅ Chave `GEMINI_API_KEY` carregada com sucesso e pronta para uso permanente via secrets!")
            else:
                st.warning("⚠️ Nenhuma chave de API configurada no sistema. Insira sua chave abaixo para utilizar os recursos de inteligência artificial.")
            
            gemini_key_manual = st.text_input(
                "Chave da API Gemini:",
                value=gemini_key,
                type="password",
                help="Salva permanentemente no arquivo .streamlit/secrets.toml"
            )

        chave_efetiva = gemini_key_manual.strip() if gemini_key_manual else gemini_key

        # Sub-abas do Instrutor
        sub_aba_importar, sub_aba_gerar, sub_aba_manual, sub_aba_gerenciar = st.tabs([
            "📥 Importar Questões Prontas (Texto ou PDF)",
            "🤖 Gerador de Questões Inéditas via Apostila (IA)",
            "✍️ Cadastrar Questão Manualmente",
            "📚 Gerenciar Questões Cadastradas"
        ])

        # SUB-ABA NOVA: IMPORTAR QUESTÕES PRONTAS
        with sub_aba_importar:
            st.markdown("#### 📥 Importação e Estruturação de Questões Prontas")
            st.write("Importe provas anteriores, listas de exercícios ou cadernos de questões. O Gemini irá extrair automaticamente os enunciados, 4 alternativas (A, B, C, D), gabarito e justificativa técnica, inserindo tudo no banco com um clique.")

            col_imp1, col_imp2 = st.columns([2, 1])
            with col_imp1:
                materia_importar = st.text_input(
                    "Disciplina / Módulo de Destino:",
                    placeholder="Ex: RDM, Arte Marinheira, Navegação, Armamento e Tiro",
                    key="input_materia_importar"
                ).strip()
            with col_imp2:
                metodo_importacao = st.radio(
                    "Formato de Entrada:",
                    ["📝 Copiar e Colar Texto", "📄 Enviar PDF de Prova Antiga"],
                    horizontal=True,
                    key="radio_metodo_importar"
                )

            texto_para_importar = ""
            pdf_import_bytes = None
            is_pdf_import_scanned = False

            if metodo_importacao == "📝 Copiar e Colar Texto":
                texto_colado = st.text_area(
                    "Cole abaixo o texto com as questões e o gabarito:",
                    placeholder="Cole aqui suas questões (formato livre, exemplo):\n\n"
                                "1. Qual é a denominação da parte anterior (frente) de um navio?\n"
                                "A) Popa\n"
                                "B) Proa\n"
                                "C) Boreste\n"
                                "D) Bombordo\n"
                                "Gabarito: B\n\n"
                                "2. Conforme o RDM, a transgressão média acarreta sanção de:\n"
                                "A) Advertência apenas\n"
                                "B) Impedimento disciplinar até 10 dias\n"
                                "C) Repreensão ou detenção disciplinar\n"
                                "D) Exclusão imediata\n"
                                "Correta: C\n",
                    height=240,
                    key="textarea_importar_questoes"
                )
                texto_para_importar = texto_colado.strip()
            else:
                arquivo_prova_pdf = st.file_uploader(
                    "Selecione o arquivo PDF da Prova ou Caderno de Questões:",
                    type=["pdf"],
                    key="uploader_prova_pronta_pdf"
                )
                if arquivo_prova_pdf is not None:
                    pdf_import_bytes = arquivo_prova_pdf.getvalue()
                    txt_extraido_prova = ""
                    try:
                        reader_prova = pypdf.PdfReader(io.BytesIO(pdf_import_bytes))
                        for pg in reader_prova.pages:
                            t = pg.extract_text()
                            if t:
                                txt_extraido_prova += t + "\n"
                    except Exception:
                        pass
                    
                    qtd_char_prova = len(txt_extraido_prova.strip())
                    if qtd_char_prova < 50:
                        is_pdf_import_scanned = True
                        st.info("📷 **PDF Escaneado:** O documento contém imagens/páginas escaneadas. O arquivo será analisado visualmente via OCR multimodal pelo Gemini.")
                    else:
                        texto_para_importar = txt_extraido_prova
                        st.info(f"📄 **PDF Lido:** `{arquivo_prova_pdf.name}` | {len(reader_prova.pages)} página(s) | {qtd_char_prova:,} caracteres.")

            btn_processar_importacao = st.button("⚡ Analisar, Estruturar e Pré-visualizar Questões", use_container_width=True, key="btn_exec_importar")

            if btn_processar_importacao:
                if not materia_importar:
                    st.error("⚠️ Por favor, informe o **Nome da Disciplina / Módulo de Destino** antes de prosseguir.")
                elif metodo_importacao == "📝 Copiar e Colar Texto" and not texto_para_importar:
                    st.error("⚠️ Cole o texto das questões no campo correspondente antes de clicar em analisar.")
                elif metodo_importacao == "📄 Enviar PDF de Prova Antiga" and not pdf_import_bytes:
                    st.error("⚠️ Selecione um arquivo PDF de prova antes de prosseguir.")
                elif not chave_efetiva:
                    st.error("⚠️ Chave de API Google Gemini não configurada.")
                elif not GENAI_AVAILABLE:
                    st.error("⚠️ O pacote `google-genai` não está instalado no ambiente.")
                else:
                    with st.spinner("🤖 A IA do Gemini está analisando, extraindo e padronizando todas as questões da prova..."):
                        try:
                            client = genai.Client(api_key=chave_efetiva)

                            prompt_import = f"""
Você é um instrutor e especialista em avaliações pedagógicas e doutrina da Marinha do Brasil.
Sua missão é extrair, reconhecer e estruturar rigorosamente TODAS as questões de múltipla escolha contidas no material fornecido para o módulo: '{materia_importar}'.

DIRETRIZES FUNDAMENTAIS:
1. Extraia cada questão com seu enunciado claro e completo.
2. Cada questão DEVE ter exatamente 4 alternativas mapeadas pelas letras: 'A', 'B', 'C' e 'D'.
   - Se a questão original possuir 5 alternativas (A a E), elimine uma alternativa incorreta irrelevante e mantenha 4, garantindo que a resposta correta seja preservada.
3. Identifique a alternativa correta ('correta' = 'A', 'B', 'C' ou 'D'):
   - Se o gabarito estiver indicado no texto ou prova, utilize-o com exatidão.
   - Se o gabarito não estiver expresso, analise e resolva a questão tecnicamente para apontar a alternativa correta.
4. No campo 'explicacao', utilize a justificativa do texto (se houver) ou formule uma fundamentação técnica pedagógica concisa embasada nas normas e doutrina naval.
5. Retorne ESTRITAMENTE um array JSON válido, sem nenhum texto introdutório ou markdown extra.

FORMATO JSON EXATO:
[
  {{
    "enunciado": "Enunciado completo da questão...",
    "opcoes": {{
      "A": "Texto da alternativa A",
      "B": "Texto da alternativa B",
      "C": "Texto da alternativa C",
      "D": "Texto da alternativa D"
    }},
    "correta": "B",
    "explicacao": "Fundamentação técnica e regulamentar do gabarito."
  }}
]
"""

                            if is_pdf_import_scanned and pdf_import_bytes:
                                pdf_part_imp = types.Part.from_bytes(data=pdf_import_bytes, mime_type="application/pdf")
                                conteudos_imp = [pdf_part_imp, prompt_import]
                            else:
                                conteudos_imp = [f"{prompt_import}\n\nCONTEÚDO DAS QUESTÕES FORNECIDO:\n---\n{texto_para_importar[:40000]}\n---"]

                            modelos_tentar = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-3-flash-preview"]
                            resp_import = None
                            ultimo_err_imp = None

                            for mod in modelos_tentar:
                                try:
                                    response = client.models.generate_content(
                                        model=mod,
                                        contents=conteudos_imp,
                                        config=types.GenerateContentConfig(
                                            response_mime_type="application/json",
                                            temperature=0.2
                                        )
                                    )
                                    resp_import = response.text
                                    if resp_import:
                                        break
                                except Exception as e_mod:
                                    ultimo_err_imp = e_mod
                                    continue

                            if not resp_import:
                                raise RuntimeError(f"Falha ao processar com os modelos Gemini: {ultimo_err_imp}")

                            json_str_imp = resp_import.strip()
                            if json_str_imp.startswith("```json"):
                                json_str_imp = json_str_imp[7:]
                            if json_str_imp.startswith("```"):
                                json_str_imp = json_str_imp[3:]
                            if json_str_imp.endswith("```"):
                                json_str_imp = json_str_imp[:-3]
                            json_str_imp = json_str_imp.strip()

                            questoes_importadas = json.loads(json_str_imp)

                            st.session_state["questoes_import_preview"] = {
                                "materia": materia_importar,
                                "questoes": questoes_importadas
                            }
                            st.toast(f"{len(questoes_importadas)} questões estruturadas com sucesso!", icon="⚓")

                        except Exception as e:
                            st.error(f"❌ Erro ao estruturar questões com a IA: {str(e)}")

            # Pré-visualização das questões importadas
            if "questoes_import_preview" in st.session_state:
                dados_imp_prev = st.session_state["questoes_import_preview"]
                st.write("---")
                st.markdown(f"### 🔍 Revisão das Questões Prontas Importadas ({dados_imp_prev['materia']})")
                st.success(f"⚓ Foram identificadas e estruturadas **{len(dados_imp_prev['questoes'])} questões** com sucesso.")

                for idx, q in enumerate(dados_imp_prev["questoes"], start=1):
                    with st.expander(f"Item {idx:02d}: {q.get('enunciado', '')[:85]}...", expanded=False):
                        st.markdown(f"**Enunciado:** {q.get('enunciado')}")
                        opcoes = q.get("opcoes", {})
                        for ltr, txt in sorted(opcoes.items()):
                            if ltr == q.get("correta"):
                                st.markdown(f"- **{ltr}) {txt}** 🟢 *(Gabarito)*")
                            else:
                                st.markdown(f"- {ltr}) {txt}")
                        st.info(f"**Justificativa Técnica:** {q.get('explicacao')}")

                col_salvar_imp, col_desc_imp = st.columns([2, 1])
                with col_salvar_imp:
                    if st.button(f"💾 Salvar Todas as {len(dados_imp_prev['questoes'])} Questões no Banco", use_container_width=True, key="btn_salvar_importadas_db"):
                        conn = get_db_connection()
                        c = conn.cursor()
                        qtd_salvas = 0
                        for q in dados_imp_prev["questoes"]:
                            c.execute('''
                                INSERT INTO questoes (materia, enunciado, opcoes_json, correta, explicacao)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (
                                dados_imp_prev["materia"],
                                q["enunciado"],
                                json.dumps(q["opcoes"], ensure_ascii=False),
                                q["correta"].strip().upper(),
                                q["explicacao"]
                            ))
                            qtd_salvas += 1
                        conn.commit()
                        conn.close()

                        del st.session_state["questoes_import_preview"]
                        st.success(f"🎉 **{qtd_salvas} questões gravadas com sucesso** no módulo '{dados_imp_prev['materia']}'!")
                        st.rerun()

                with col_desc_imp:
                    if st.button("🗑️ Descartar Importação", use_container_width=True, key="btn_desc_importacao"):
                        del st.session_state["questoes_import_preview"]
                        st.info("Importação descartada.")
                        st.rerun()

        # SUB-ABA EXISTENTE: GERAÇÃO INÉDITA VIA IA
        with sub_aba_gerar:
            st.markdown("#### 📄 Upload de Manual/Apostila e Criação de Questões Inéditas com Google Gemini")
            st.write("Envie apostilas militares, regulamentos (RDM, OGSA, etc.) ou manuais técnicos em PDF para gerar questões inéditas de múltipla escolha com gabarito fundamentado.")

            col_cfg1, col_cfg2, col_cfg3 = st.columns([2, 1, 1])
            with col_cfg1:
                nome_materia_ia = st.text_input(
                    "Nome da Matéria / Módulo:",
                    placeholder="Ex: Regulamento Disciplinar, Armamento Leve, Sobrevivência",
                    key="input_materia_ia"
                ).strip()
            with col_cfg2:
                qtd_questoes = st.slider("Qtd de Questões:", min_value=1, max_value=10, value=3)
            with col_cfg3:
                dificuldade = st.selectbox("Nível:", ["Básico / Nivelamento", "Intermediário / Operacional", "Avançado / Doutrinário"])

            arquivo_pdf = st.file_uploader(
                "Selecione o arquivo PDF da Instrução (Apostila, Portaria ou Regulamento):",
                type=["pdf"],
                help="Arquivos PDF com texto selecionável são suportados."
            )

            if arquivo_pdf is not None:
                try:
                    pdf_bytes = arquivo_pdf.getvalue()
                    
                    # Tentativa de extração de texto local com pypdf
                    texto_extraido = ""
                    num_paginas = 0
                    try:
                        pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
                        num_paginas = len(pdf_reader.pages)
                        for p_num, page in enumerate(pdf_reader.pages, start=1):
                            txt = page.extract_text()
                            if txt:
                                texto_extraido += txt + "\n"
                    except Exception:
                        pass

                    qtd_caracteres = len(texto_extraido.strip())
                    modo_multimodal = qtd_caracteres < 50

                    if modo_multimodal:
                        st.info(f"📷 **Documento Escaneado/Visual Detectado:** `{arquivo_pdf.name}` ({num_paginas} página(s)). O leitor de texto local identificou poucos caracteres legíveis ({qtd_caracteres} caracteres). **Modo Multimodal ativado:** o arquivo binário PDF será enviado diretamente ao Gemini Flash para reconhecimento visual (OCR) e análise das páginas escaneadas.")
                    else:
                        st.info(f"📄 **PDF Textual Processado:** `{arquivo_pdf.name}` | **Páginas:** `{num_paginas}` | **Caracteres extraídos:** `{qtd_caracteres:,}`")
                        with st.expander("Visualizar amostra do texto extraído"):
                            st.text_area("Amostra do Texto:", value=texto_extraido[:1500] + ("..." if qtd_caracteres > 1500 else ""), height=160, disabled=True)

                    btn_gerar_ia = st.button("⚡ Gerar Questões com Inteligência Artificial", use_container_width=True)

                    if btn_gerar_ia:
                        if not nome_materia_ia:
                            st.error("⚠️ Por favor, informe o **Nome da Matéria / Módulo** antes de gerar.")
                        elif not chave_efetiva:
                            st.error("⚠️ Chave de API Google Gemini não informada! Insira a chave no campo de configuração acima.")
                        elif not GENAI_AVAILABLE:
                            st.error("⚠️ O pacote `google-genai` não está instalado no ambiente.")
                        else:
                            with st.spinner("🤖 Analisando o documento e elaborando questões doutrinárias com o Gemini Flash..."):
                                try:
                                    client = genai.Client(api_key=chave_efetiva)

                                    if modo_multimodal:
                                        # Leitura multimodal: PDF em bytes diretamente para o Gemini
                                        pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
                                        prompt_instrucao = f"""
Você é um instrutor militar sênior especialista em avaliação doutrinária e elaboração de provas objetivas para formação militar.
Sua missão é analisar visualmente todas as páginas do documento militar em anexo (realizando a leitura óptica/OCR das páginas e manuais escaneados) e elaborar exatamente {qtd_questoes} questões de múltipla escolha inéditas e de alto rigor pedagógico para o módulo: '{nome_materia_ia}'.
Nível de exigência: {dificuldade}.

DIRETRIZES TÉCNICAS E ESTRUTURAIS:
1. Cada questão deve possuir enunciado claro, contextualizado e objetivo, fundamentado nas páginas do documento escaneado.
2. Cada questão deve possuir exatamente 4 alternativas identificadas como 'A', 'B', 'C' e 'D'.
3. Apenas UMA alternativa deve ser correta.
4. O campo 'correta' deve conter APENAS a letra maiúscula: 'A', 'B', 'C' ou 'D'.
5. O campo 'explicacao' deve conter a justificativa técnica pedagógica e o embasamento baseado no documento.
6. A resposta DEVE ser estritamente um array JSON válido, sem nenhum bloco extra de texto.

FORMATO JSON EXATO:
[
  {{
    "enunciado": "Texto claro da pergunta militar...",
    "opcoes": {{
      "A": "Texto da alternativa A",
      "B": "Texto da alternativa B",
      "C": "Texto da alternativa C",
      "D": "Texto da alternativa D"
    }},
    "correta": "A",
    "explicacao": "Fundamentação técnica e pedagógica baseada no manual."
  }}
]
"""
                                        conteudos_envio = [pdf_part, prompt_instrucao]
                                    else:
                                        texto_prompt = texto_extraido[:35000]
                                        prompt_instrucao = f"""
Você é um instrutor militar sênior especialista em avaliação doutrinária e elaboração de provas objetivas para formação militar.
Sua tarefa é analisar o seguinte texto de apostila/manual e elaborar exatamente {qtd_questoes} questões de múltipla escolha inéditas e de alto rigor pedagógico para o módulo: '{nome_materia_ia}'.
Nível de exigência: {dificuldade}.

TEXTO DO MANUAL / REGULAMENTO:
---
{texto_prompt}
---

DIRETRIZES TÉCNICAS E ESTRUTURAIS:
1. Cada questão deve possuir enunciado claro, contextualizado e objetivo.
2. Cada questão deve possuir exatamente 4 alternativas identificadas como 'A', 'B', 'C' e 'D'.
3. Apenas UMA alternativa deve ser correta.
4. O campo 'correta' deve conter APENAS a letra maiúscula: 'A', 'B', 'C' ou 'D'.
5. O campo 'explicacao' deve conter a justificativa técnica pedagógica e o embasamento baseado no texto.
6. A resposta DEVE ser estritamente um array JSON válido, sem nenhum bloco extra de texto.

FORMATO JSON EXATO:
[
  {{
    "enunciado": "Texto claro da pergunta militar...",
    "opcoes": {{
      "A": "Texto da alternativa A",
      "B": "Texto da alternativa B",
      "C": "Texto da alternativa C",
      "D": "Texto da alternativa D"
    }},
    "correta": "A",
    "explicacao": "Fundamentação técnica e pedagógica baseada no manual."
  }}
]
"""
                                        conteudos_envio = [prompt_instrucao]

                                    modelos_tentar = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-3-flash-preview"]
                                    resposta_conteudo = None
                                    ultimo_erro = None

                                    for modelo in modelos_tentar:
                                        try:
                                            response = client.models.generate_content(
                                                model=modelo,
                                                contents=conteudos_envio,
                                                config=types.GenerateContentConfig(
                                                    response_mime_type="application/json",
                                                    temperature=0.3
                                                )
                                            )
                                            resposta_conteudo = response.text
                                            if resposta_conteudo:
                                                break
                                        except Exception as err_mod:
                                            ultimo_erro = err_mod
                                            continue

                                    if not resposta_conteudo:
                                        raise RuntimeError(f"Falha ao chamar modelos Gemini: {ultimo_erro}")

                                    json_str = resposta_conteudo.strip()
                                    if json_str.startswith("```json"):
                                        json_str = json_str[7:]
                                    if json_str.startswith("```"):
                                        json_str = json_str[3:]
                                    if json_str.endswith("```"):
                                        json_str = json_str[:-3]
                                    json_str = json_str.strip()

                                    questoes_geradas = json.loads(json_str)

                                    st.session_state["questoes_preview"] = {
                                        "materia": nome_materia_ia,
                                        "questoes": questoes_geradas
                                    }
                                    st.toast("Questões geradas pela IA com sucesso!", icon="✨")

                                except Exception as e:
                                    st.error(f"❌ Erro na integração com o Gemini: {str(e)}")

                except Exception as e:
                    st.error(f"Erro ao processar arquivo PDF: {str(e)}")

            # Pré-visualização e Aprovação
            if "questoes_preview" in st.session_state:
                dados_prev = st.session_state["questoes_preview"]
                st.write("---")
                st.markdown(f"### 🔍 Pré-visualização das Questões Geradas ({dados_prev['materia']})")
                st.caption("Revise os itens abaixo antes de autorizar o salvamento definitivo no banco de dados.")

                for idx, q in enumerate(dados_prev["questoes"], start=1):
                    with st.expander(f"Questão {idx:02d}: {q.get('enunciado', '')[:80]}...", expanded=True):
                        st.markdown(f"**Enunciado:** {q.get('enunciado')}")
                        opcoes = q.get("opcoes", {})
                        for ltr, txt in sorted(opcoes.items()):
                            if ltr == q.get("correta"):
                                st.markdown(f"- **{ltr}) {txt}** 🟢 *(Gabarito)*")
                            else:
                                st.markdown(f"- {ltr}) {txt}")
                        st.info(f"**Justificativa Técnica:** {q.get('explicacao')}")

                col_salvar, col_descartar = st.columns([2, 1])
                with col_salvar:
                    if st.button("💾 Aprovar e Gravar Questões no Banco de Dados", use_container_width=True):
                        conn = get_db_connection()
                        c = conn.cursor()
                        qtd_inseridas = 0
                        for q in dados_prev["questoes"]:
                            c.execute('''
                                INSERT INTO questoes (materia, enunciado, opcoes_json, correta, explicacao)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (
                                dados_prev["materia"],
                                q["enunciado"],
                                json.dumps(q["opcoes"], ensure_ascii=False),
                                q["correta"].strip().upper(),
                                q["explicacao"]
                            ))
                            qtd_inseridas += 1
                        conn.commit()
                        conn.close()

                        del st.session_state["questoes_preview"]
                        st.success(f"🎉 **{qtd_inseridas} questões gravadas com sucesso** no módulo '{dados_prev['materia']}'!")
                        st.rerun()

                with col_descartar:
                    if st.button("🗑️ Descartar Estas Questões", use_container_width=True):
                        del st.session_state["questoes_preview"]
                        st.info("Questões descartadas.")
                        st.rerun()

        # SUB-ABA 3: CADASTRO MANUAL
        with sub_aba_manual:
            st.markdown("#### ✍️ Adicionar Questão Manualmente")
            st.write("Cadastre uma questão específica diretamente sem necessidade de PDF:")

            with st.form("form_cadastro_manual"):
                materia_manual = st.text_input("Matéria / Módulo:", placeholder="Ex: RDM, Navegação Terrestre, Armamento")
                enunciado_manual = st.text_area("Enunciado da Questão:", placeholder="Digite o texto da pergunta...")
                
                col_op1, col_op2 = st.columns(2)
                with col_op1:
                    op_a = st.text_input("Alternativa A:", placeholder="Texto da opção A")
                    op_b = st.text_input("Alternativa B:", placeholder="Texto da opção B")
                with col_op2:
                    op_c = st.text_input("Alternativa C:", placeholder="Texto da opção C")
                    op_d = st.text_input("Alternativa D:", placeholder="Texto da opção D")

                col_gab, _ = st.columns([1, 2])
                with col_gab:
                    correta_manual = st.selectbox("Gabarito Correto:", ["A", "B", "C", "D"])
                
                explicacao_manual = st.text_area("Justificativa Técnica / Pedagógica:", placeholder="Fundamente com base no regulamento...")

                btn_salvar_manual = st.form_submit_button("Salvar Questão no Banco", use_container_width=True)

            if btn_salvar_manual:
                if not (materia_manual and enunciado_manual and op_a and op_b and op_c and op_d and explicacao_manual):
                    st.error("⚠️ Todos os campos são de preenchimento obrigatório.")
                else:
                    opcoes_dict = {"A": op_a, "B": op_b, "C": op_c, "D": op_d}
                    conn = get_db_connection()
                    conn.execute('''
                        INSERT INTO questoes (materia, enunciado, opcoes_json, correta, explicacao)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (materia_manual.strip(), enunciado_manual.strip(), json.dumps(opcoes_dict, ensure_ascii=False), correta_manual, explicacao_manual.strip()))
                    conn.commit()
                    conn.close()
                    st.success("✅ Questão salva no banco de dados com sucesso!")

        # SUB-ABA 4: GERENCIAR QUESTÕES
        with sub_aba_gerenciar:
            st.markdown("#### 📚 Gestão do Acervo de Questões")
            
            conn = get_db_connection()
            materias_gerencia = [row["materia"] for row in conn.cursor().execute("SELECT DISTINCT materia FROM questoes ORDER BY materia").fetchall()]
            conn.close()

            if not materias_gerencia:
                st.info("Nenhuma questão cadastrada no banco de dados.")
            else:
                filtro_mat_gerencia = st.selectbox("Selecione o módulo para visualizar ou gerenciar:", materias_gerencia, key="select_materia_gerencia")
                
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, enunciado, correta, explicacao FROM questoes WHERE materia = ? ORDER BY id ASC", (filtro_mat_gerencia,))
                itens_materia = cursor.fetchall()
                conn.close()

                st.write(f"Total de questões cadastradas neste módulo: **{len(itens_materia)}**")
                
                for idx, itm in enumerate(itens_materia, start=1):
                    with st.expander(f"Q{idx:02d} (ID #{itm['id']}): {itm['enunciado'][:70]}..."):
                        st.markdown(f"**Enunciado:** {itm['enunciado']}")
                        st.markdown(f"**Gabarito Oficial:** `{itm['correta']}`")
                        st.markdown(f"**Justificativa:** {itm['explicacao']}")
                        
                        if st.button(f"🗑️ Excluir Questão #{itm['id']}", key=f"btn_del_q_{itm['id']}"):
                            conn = get_db_connection()
                            conn.execute("DELETE FROM questoes WHERE id = ?", (itm["id"],))
                            conn.commit()
                            conn.close()
                            st.success(f"Questão #{itm['id']} excluída com sucesso.")
                            st.rerun()
