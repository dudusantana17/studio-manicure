import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import urllib.parse
from supabase import create_client, Client
import streamlit.components.v1 as components

# =======================================================
# CONFIGURAÇÃO DE PÁGINA
# =======================================================
st.set_page_config(
    page_title="Studio Belleza & Arte | Manicure & Academy",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown('<div id="topo-pagina"></div>', unsafe_allow_html=True)

# =======================================================
# CONEXÃO SUPABASE & DADOS DE COBRANÇA
# =======================================================
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
SENHA_MESTRE = st.secrets.get("GESTORA_PASSWORD", "studio2026")

VALOR_SINAL = 20.00
CHAVE_PIX = "21969861082"
BENEFICIARIO = "Rafaella Aquino – Stone IP S.A"
LINK_CARTAO = "https://payment-link-v3.ton.com.br/pl_3dPKpGv5Zrb9l9aH6tjlw1agNjLX0m4D"
WHATSAPP_NUMERO = "5521969861082"

if "servico_preselecionado" not in st.session_state:
    st.session_state["servico_preselecionado"] = None
if "scroll_para_agendamento" not in st.session_state:
    st.session_state["scroll_para_agendamento"] = False
if "scroll_para_topo" not in st.session_state:
    st.session_state["scroll_para_topo"] = False
if "conf_curso_pendente" not in st.session_state:
    st.session_state["conf_curso_pendente"] = None
if "recusa_pendente" not in st.session_state:
    st.session_state["recusa_pendente"] = None

# =======================================================
# CSS VISUAL COM BLINDAGEM TOTAL (MODO ESCURO / MOBILE)
# =======================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* 1. Forçar modo claro geral */
    :root, html, body, [data-testid="stAppViewContainer"], .stApp {
        color-scheme: light !important;
        supported-color-schemes: light !important;
        background-color: #faf5ff !important;
        color: #2e1065 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* 2. Ocultação de menus padrão */
    footer {visibility: hidden; display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}

    /* 3. Forçar contraste escuro legível em textos */
    h1, h2, h3, h4, h5, h6, p, span, label, div, small {
        color: #2e1065 !important;
    }

    /* 4. Rótulos de campos */
    .stTextInput label, .stDateInput label, .stSelectbox label, 
    .stRadio label, .stCheckbox label, .stTextArea label, .stTimeInput label {
        color: #2e1065 !important;
        font-weight: 700 !important;
    }

    [data-testid="stMarkdownContainer"] p, [data-testid="stWidgetLabel"] p {
        color: #2e1065 !important;
        font-weight: 600 !important;
    }

    /* 5. Campos de Entrada (Inputs fechados) */
    input, textarea, 
    [data-baseweb="input"], 
    [data-baseweb="input"] > div, 
    [data-baseweb="base-input"],
    [data-baseweb="select"],
    [data-baseweb="select"] > div,
    div[data-testid="stDateInput"] div {
        background-color: #ffffff !important;
        color: #1e1b4b !important;
        -webkit-text-fill-color: #1e1b4b !important;
        border-color: #d8b4fe !important;
    }

    [data-baseweb="input"], [data-baseweb="select"] {
        border: 1.5px solid #d8b4fe !important;
        border-radius: 10px !important;
    }

    /* 6. Blindagem do menu suspenso aberto (Dropdown / Popover) */
    [data-baseweb="popover"], 
    [data-baseweb="popover"] > div, 
    [data-baseweb="menu"], 
    ul[role="listbox"],
    div[role="listbox"] {
        background-color: #ffffff !important;
        border: 1.5px solid #c084fc !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(88, 28, 135, 0.15) !important;
    }

    li[role="option"], 
    li[role="option"] > div,
    div[role="option"],
    [data-baseweb="menu"] li {
        background-color: #ffffff !important;
        color: #2e1065 !important;
        -webkit-text-fill-color: #2e1065 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    li[role="option"]:hover, 
    li[aria-selected="true"],
    [data-baseweb="menu"] li:hover {
        background-color: #f3e8ff !important;
        color: #6b21a8 !important;
        -webkit-text-fill-color: #6b21a8 !important;
    }

    [data-baseweb="select"] svg, div[data-testid="stDateInput"] svg {
        fill: #581c87 !important;
    }

    /* 7. Blindagem dos Botões */
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #7e22ce 0%, #9333ea 100%) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border-radius: 50px !important;
        padding: 0.75rem 1.8rem !important;
        border: 1px solid #c084fc !important;
        box-shadow: 0 8px 22px rgba(126, 34, 206, 0.3) !important;
        width: 100% !important;
    }

    .stButton > button p, div[data-testid="stFormSubmitButton"] > button p {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 700 !important;
    }

    .stLinkButton > a {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 50px !important;
        padding: 0.85rem 2rem !important;
        border: none !important;
        display: inline-flex !important;
    }

    /* 8. Componentes estruturais e cartões */
    .site-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff !important;
        padding: 18px 24px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(88, 28, 135, 0.05);
        border: 1px solid #f3e8ff;
        margin-bottom: 24px;
    }
    .nav-brand {
        font-family: 'Playfair Display', serif;
        font-size: 24px;
        font-weight: 700;
        color: #581c87 !important;
    }
    .nav-tagline {
        font-size: 11px;
        color: #9333ea !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .hero-section {
        background: linear-gradient(135deg, #2e1065 0%, #581c87 50%, #7e22ce 100%) !important;
        border-radius: 24px;
        padding: 35px 24px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 16px 36px -6px rgba(88, 28, 135, 0.35);
        border: 1px solid #c084fc;
    }
    .hero-section h1, .hero-section p, .hero-section div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .site-card {
        background: #ffffff !important;
        border: 1px solid #f3e8ff;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 24px rgba(107, 33, 168, 0.05);
        border-top: 5px solid #7e22ce;
        margin-bottom: 20px;
    }
    .site-card h3 {
        font-family: 'Playfair Display', serif;
        font-size: 20px;
        color: #3b0764 !important;
        margin: 8px 0;
    }
    .card-price-value {
        font-size: 24px;
        font-weight: 700;
        color: #581c87 !important;
        margin: 10px 0;
    }
    .policy-card {
        background: #ffffff !important;
        border: 1px solid #e9d5ff;
        border-left: 5px solid #9333ea;
        border-radius: 14px;
        padding: 16px 20px;
        margin: 15px 0;
        font-size: 14px;
        line-height: 1.6;
        color: #3b0764 !important;
    }
    .policy-card strong, .policy-card b {
        color: #4a044e !important;
    }
    .metric-box {
        background: #ffffff !important;
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
        color: #7e22ce !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #3b0764 !important;
        margin: 6px 0 2px 0;
    }
    .modal-sucesso-box {
        text-align: center;
        padding: 10px;
    }
    .modal-sucesso-box h2 {
        font-family: 'Playfair Display', serif;
        color: #4c1d95 !important;
        margin-top: 10px;
    }
    .modal-detalhe {
        background: #faf5ff;
        border: 1px solid #e9d5ff;
        border-radius: 12px;
        padding: 16px;
        margin: 18px 0;
        text-align: left;
    }
    .site-footer {
        text-align: center;
        padding: 30px 20px;
        color: #7e22ce !important;
        font-size: 13px;
        border-top: 1px solid #f3e8ff;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# EXECUÇÃO DO SCROLL PARA O TOPO
if st.session_state.get("scroll_para_topo", False):
    components.html("""
        <script>
            setTimeout(() => {
                const doc = window.parent.document;
                const topo = doc.getElementById("topo-pagina");
                if (topo) {
                    topo.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
                const scrollContainer = doc.querySelector('[data-testid="stAppViewContainer"]');
                if (scrollContainer) {
                    scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
                }
                window.parent.scrollTo({ top: 0, behavior: 'smooth' });
            }, 100);
        </script>
    """, height=0, width=0)
    st.session_state["scroll_para_topo"] = False

# NAVBAR
st.markdown("""
    <div class="site-nav">
        <div>
            <div class="nav-brand">Studio Belleza & Arte</div>
            <div class="nav-tagline">Nail Design & Academy</div>
        </div>
        <div style="font-size: 14px; color: #581c87; font-weight: 600;">
            ✨ Atendimento Exclusivo • Agendamento Imediato
        </div>
    </div>
""", unsafe_allow_html=True)

DIAS_SEMANA_NOMES = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo"
}

def gerar_protocolo(agendamento_id: int, data_str: str) -> str:
    dt_limpa = data_str[:10].replace("-", "")
    return f"BA-{dt_limpa}-{int(agendamento_id):04d}"

# MODAL - AGENDAMENTO DE CLIENTE COM PROTOCOLO E WHATSAPP
@st.dialog("✨ Quase Lá! Confirme com o Sinal")
def exibir_modal_confirmacao(nome, servico, data_hora, total_val, restante_val, protocolo):
    msg_zap = (
        f"Olá Rafaella! Acabei de fazer minha pré-reserva no Studio Belleza & Arte:\n\n"
        f"👤 *Cliente:* {nome}\n"
        f"🔖 *Protocolo:* {protocolo}\n"
        f"💅 *Procedimento:* {servico}\n"
        f"📅 *Data:* {data_hora}\n"
        f"💰 *Total:* R$ {total_val:.2f} (Sinal: R$ {VALOR_SINAL:.2f} | Restante: R$ {restante_val:.2f})\n\n"
        f"Segue o comprovante do sinal de R$ 20,00 para garantir minha vaga!"
    )
    link_zap_comprovante = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(msg_zap)}"

    st.markdown(f"""
        <div class="modal-sucesso-box">
            <div style="font-size: 42px;">💅</div>
            <h2>Sua Vaga foi Pré-Reservada!</h2>
            <p style="font-size: 15px; color: #4c1d95; line-height: 1.6;">
                Olá, <b>{nome}</b>! Seu pedido para <b>{servico}</b> em <b>{data_hora}</b> está salvo.<br>
                Protocolo de Atendimento: <b>{protocolo}</b>
            </p>
            <div class="modal-detalhe">
                <p style="margin: 0 0 6px 0; font-size: 14px; color: #6b21a8;">
                    💵 <b>Sinal de Garantia:</b> R$ {VALOR_SINAL:.2f} (Restará R$ {restante_val:.2f} a pagar no local)
                </p>
                <p style="margin: 0; font-size: 13px; color: #6b21a8;">
                    🔴 <i>Lembrete: Sua vaga só é confirmada após o envio do comprovante de pagamento do sinal.</i>
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.link_button("📲 Enviar Comprovante do Sinal no WhatsApp", link_zap_comprovante, use_container_width=True)
    st.write("")
    if st.button("Concluir e Voltar ao Início", use_container_width=True):
        st.session_state["scroll_para_topo"] = True
        st.rerun()

# MODAL - INSCRIÇÃO EM CURSO
@st.dialog("🎓 Inscrição Registrada!")
def exibir_modal_curso(nome, curso, tipo_vaga, posicao=0):
    if tipo_vaga == "Titular":
        msg_tipo = "Sua vaga titular foi pré-reservada com sucesso!"
        icone = "🎉"
    else:
        msg_tipo = f"Você foi incluída na <b>{posicao}ª posição</b> da Lista de Espera!"
        icone = "📌"

    st.markdown(f"""
        <div class="modal-sucesso-box">
            <div style="font-size: 42px;">{icone}</div>
            <h2>Inscrição Enviada!</h2>
            <p style="font-size: 15px; color: #4c1d95; line-height: 1.6;">
                Olá, <b>{nome}</b>! Recebemos sua inscrição para a formação <b>{curso}</b>.<br>{msg_tipo}
            </p>
            <div class="modal-detalhe">
                <p style="margin: 0; font-size: 14px; color: #6b21a8;">
                    📲 <b>Próximo Passo:</b> A coordenação do Studio entrará em contato via <b>WhatsApp</b> para formalizar os detalhes da matrícula e instruções de acesso.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Entendido, fechar aviso!", key="btn_fechar_modal_curso", use_container_width=True):
        st.session_state["scroll_para_topo"] = True
        st.rerun()

opcoes_menu = ["✨ Início & Agendamento", "🎓 Academy (Cursos)", "🔐 Acesso Gestora"]
aba_selecionada = st.radio(
    "Navegação",
    opcoes_menu,
    horizontal=True,
    label_visibility="collapsed"
)

# =======================================================
# 1. INÍCIO & AGENDAMENTO
# =======================================================
if aba_selecionada == "✨ Início & Agendamento":
    st.markdown("""
        <div class="hero-section">
            <div style="text-transform: uppercase; letter-spacing: 3px; font-size: 11px; margin-bottom: 8px; color: #e9d5ff; font-weight: 700;">Alta Estética & Sofisticação</div>
            <h1>A excelência e a arte em cada detalhe das suas mãos.</h1>
            <p>Selecione um procedimento abaixo para consultar os horários disponíveis.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        res_srv = supabase.table("servicos").select("*").order("nome_servico").execute()
        servicos = res_srv.data if res_srv.data else []
    except Exception:
        servicos = []

    try:
        res_conf = supabase.table("configuracoes").select("*").execute()
        dict_conf = {row["chave"]: row["valor"] for row in (res_conf.data or [])}
    except Exception:
        dict_conf = {}

    status_agenda = dict_conf.get("agenda_status", "Aberta")
    meses_liberados_str = dict_conf.get("mes_liberado", "2026-09,2026-10")
    meses_liberados_lista = [m.strip() for m in meses_liberados_str.split(",") if m.strip()]
    dias_func_str = dict_conf.get("dias_funcionamento", "1,2,3,4,5")
    dias_func_lista = [int(d.strip()) for d in dias_func_str.split(",") if d.strip()]

    st.markdown("### 💅 Nossos Procedimentos & Valores")

    if not servicos:
        st.info("Nenhum procedimento cadastrado no momento. A gestora pode cadastrar novos serviços no Painel Administrativo.")
    else:
        cols = st.columns(min(len(servicos), 3))
        for idx, srv in enumerate(servicos):
            col_target = cols[idx % 3]
            with col_target:
                st.markdown(f"""
                    <div class="site-card">
                        <span style="font-size: 12px; font-weight: 700; color: #7e22ce; background: #faf5ff; padding: 4px 10px; border-radius: 12px;">⏱ {srv['duracao_minutos']} Minutos</span>
                        <h3>{srv['nome_servico']}</h3>
                        <p style="font-size: 14px; color: #6b21a8;">Higienização profunda, formato alinhado e finalização duradoura.</p>
                        <div class="card-price-value">R$ {float(srv['preco']):.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Agendar {srv['nome_servico']} ✨", key=f"btn_srv_{srv['id']}", use_container_width=True):
                    st.session_state["servico_preselecionado"] = srv["nome_servico"]
                    st.session_state["scroll_para_agendamento"] = True
                    st.rerun()

    st.divider()

    st.markdown('<div id="area-agendamento"></div>', unsafe_allow_html=True)
    st.markdown("### 📅 Escolha a Sua Data & Horário")

    if st.session_state.get("scroll_para_agendamento", False):
        components.html("""
            <script>
                const target = window.parent.document.getElementById("area-agendamento");
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            </script>
        """, height=0, width=0)
        st.session_state["scroll_para_agendamento"] = False

    if status_agenda == "Fechada":
        st.warning("🔒 Nossa agenda de atendimentos está temporariamente fechada para novos horários online.")
    else:
        nomes_meses_pt = {
            "01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril",
            "05": "Maio", "06": "Junho", "07": "Julho", "08": "Agosto",
            "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro"
        }
        meses_legenda = []
        for m in meses_liberados_lista:
            parts = m.split("-")
            if len(parts) == 2:
                meses_legenda.append(f"{nomes_meses_pt.get(parts[1], parts[1])}/{parts[0]}")
        legenda_str = ", ".join(meses_legenda) if meses_legenda else "Consulte a administração"

        dias_legenda = [DIAS_SEMANA_NOMES[d] for d in sorted(dias_func_lista)]
        st.info(f"🗓️ **Meses abertos:** {legenda_str} | **Dias:** {', '.join(dias_legenda)}")

        col_esq, col_dir = st.columns([1, 1])

        with col_esq:
            st.markdown("#### 1. Procedimento & Data")
            if not servicos:
                st.warning("Nenhum serviço disponível para agendamento.")
                srv_obj = None
                duracao_escolhida = 60
                data_selecionada = datetime.today().date()
            else:
                lista_nomes = [f"{s['nome_servico']} — R$ {float(s['preco']):.2f} ({s['duracao_minutos']} min)" for s in servicos]
                map_nomes = {f"{s['nome_servico']} — R$ {float(s['preco']):.2f} ({s['duracao_minutos']} min)": s for s in servicos}

                idx_default = 0
                if st.session_state["servico_preselecionado"]:
                    for i, s in enumerate(servicos):
                        if s["nome_servico"] == st.session_state["servico_preselecionado"]:
                            idx_default = i
                            break

                srv_escolhido_str = st.selectbox("Procedimento Selecionado:", lista_nomes, index=idx_default)
                srv_obj = map_nomes[srv_escolhido_str]
                duracao_escolhida = int(srv_obj["duracao_minutos"])

                data_selecionada = st.date_input(
                    "Dia do Atendimento:",
                    min_value=datetime.today(),
                    format="DD/MM/YYYY"
                )
                dia_da_semana = data_selecionada.weekday()
                mes_escolhido_str = data_selecionada.strftime("%Y-%m")

        with col_dir:
            st.markdown("#### 2. Horários Livres")
            horario_valido = False
            horario_selecionado = None

            if not servicos or srv_obj is None:
                st.info("Cadastre procedimentos no painel para listar os horários.")
            elif mes_escolhido_str not in meses_liberados_lista:
                st.error(f"⛔ Data indisponível. Agenda aberta apenas para: **{legenda_str}**.")
            elif dia_da_semana not in dias_func_lista:
                st.warning(f"🏖️ Não atendemos às {DIAS_SEMANA_NOMES.get(dia_da_semana, '')}s. Escolha outro dia.")
            else:
                data_inicio_dia = f"{data_selecionada.strftime('%Y-%m-%d')} 00:00:00"
                data_fim_dia = f"{data_selecionada.strftime('%Y-%m-%d')} 23:59:59"

                try:
                    res_ocupados = supabase.table("agendamentos").select(
                        "data_hora, servicos(duracao_minutos)"
                    ).gte("data_hora", data_inicio_dia).lte("data_hora", data_fim_dia).in_("status", ["Pendente", "Confirmado"]).execute()
                    ocupados = res_ocupados.data or []
                except Exception:
                    ocupados = []

                intervalos_ocupados = []
                for ag_oc in ocupados:
                    dt_hora_str = ag_oc["data_hora"][:19].replace("T", " ")
                    dt_inicio = datetime.strptime(dt_hora_str, "%Y-%m-%d %H:%M:%S")
                    dur_oc = ag_oc["servicos"]["duracao_minutos"] if ag_oc.get("servicos") else 60
                    dt_fim = dt_inicio + timedelta(minutes=int(dur_oc))
                    intervalos_ocupados.append((dt_inicio.time(), dt_fim.time()))

                grade_base = [
                    time(8, 0), time(9, 0), time(10, 0), time(11, 0),
                    time(13, 0), time(14, 0), time(15, 0), time(16, 0), time(17, 0)
                ]

                horarios_disponiveis = []
                hora_limite_studio = time(19, 0)

                for slot in grade_base:
                    inicio_slot = datetime.combine(data_selecionada, slot)
                    fim_slot = inicio_slot + timedelta(minutes=duracao_escolhida)

                    if fim_slot.time() > hora_limite_studio:
                        continue

                    colisao = False
                    for oc_ini, oc_fim in intervalos_ocupados:
                        oc_ini_dt = datetime.combine(data_selecionada, oc_ini)
                        oc_fim_dt = datetime.combine(data_selecionada, oc_fim)
                        if (inicio_slot < oc_fim_dt) and (fim_slot > oc_ini_dt):
                            colisao = True
                            break

                    if not colisao:
                        if data_selecionada == datetime.today().date() and slot <= datetime.now().time():
                            continue
                        horarios_disponiveis.append(slot.strftime("%H:%M"))

                if not horarios_disponiveis:
                    st.warning("⚠️ Todos os horários deste dia estão preenchidos para a duração deste procedimento.")
                else:
                    horario_selecionado = st.radio("Selecione o Horário:", horarios_disponiveis, horizontal=True)
                    horario_valido = True

        # =======================================================
        # 3. CONFIRMAÇÃO COM SINAL & PAGAMENTO (SEM NASCIMENTO)
        # =======================================================
        if horario_valido and horario_selecionado and srv_obj:
            st.write("")
            st.markdown("#### 3. Dados Pessoais, Sinal & Pagamento")
            
            add_decoracao = st.checkbox("✨ Adicionar Decoração (+ R$ 10,00)", value=False)
            
            preco_base = float(srv_obj["preco"])
            total_servico = preco_base + (10.00 if add_decoracao else 0.00)
            restante_estudio = max(0.00, total_servico - VALOR_SINAL)
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Valor Total", f"R$ {total_servico:.2f}")
            col_m2.metric("Sinal de Garantia", f"R$ {VALOR_SINAL:.2f}")
            col_m3.metric("Restante no Estúdio", f"R$ {restante_estudio:.2f}")
            
            st.markdown("""
                <div class="policy-card">
                    <strong>🔴 IMPORTANTE — Regras do Sinal & Agendamento:</strong><br>
                    • A sua vaga só estará garantida após o pagamento do sinal de <b>R$ 20,00</b>;<br>
                    • O sinal é válido por 30 dias e intransferível;<br>
                    • Você pode reagendar com o mesmo sinal avisando com pelo menos <b>24h de antecedência</b>;<br>
                    • O sinal <b>não é devolvido</b> em caso de cancelamento ou falta;<br>
                    • Tolerância máxima de <b>10 minutos</b> para atrasos.
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("##### 💳 Pagar Sinal de Garantia (R$ 20,00)")
            col_pag1, col_pag2 = st.columns(2)
            with col_pag1:
                st.info(f"🔑 **Chave PIX:** `{CHAVE_PIX}`  \n**Favorecido:** {BENEFICIARIO}")
            with col_pag2:
                st.write("Prefere pagar via cartão?")
                st.link_button("💳 Pagar Sinal no Cartão de Crédito (Ton)", LINK_CARTAO, use_container_width=True)

            with st.form("form_confirmacao_reserva"):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    nome_c = st.text_input("Seu Nome Completo:")
                with col_c2:
                    tel_c = st.text_input("WhatsApp (DDD + Número):", placeholder="Ex: 21969861082")
                
                observacao = st.text_area("Observações adicionais (opcional):", placeholder="Ex: Unha roída, preferência por formato amendoado...")

                aceitou_termos = st.checkbox("Li e concordo integralmente com as regras de agendamento e política do sinal.")

                btn_agendar = st.form_submit_button("Confirmar Agendamento & Liberar Envio ✨", use_container_width=True)

            if btn_agendar:
                tel_limpo = ''.join(filter(str.isdigit, tel_c.strip()))
                if not nome_c.strip() or len(tel_limpo) < 10:
                    st.error("Por favor, informe seu nome completo e WhatsApp válido com DDD.")
                elif not aceitou_termos:
                    st.error("Você precisa marcar o aceite das regras de cancelamento e sinal para prosseguir.")
                else:
                    supabase.table("clientes").upsert({
                        "nome": nome_c.strip(),
                        "telefone": tel_limpo
                    }, on_conflict="telefone").execute()

                    res_cli = supabase.table("clientes").select("id").eq("telefone", tel_limpo).execute()
                    cliente_id = res_cli.data[0]["id"]

                    data_hora_final = f"{data_selecionada.strftime('%Y-%m-%d')} {horario_selecionado}:00"
                    
                    obs_completa = observacao.strip()
                    if add_decoracao:
                        obs_completa = f"[Com Decoração +R$10] {obs_completa}".strip()

                    res_novo_ag = supabase.table("agendamentos").insert({
                        "cliente_id": cliente_id,
                        "servico_id": srv_obj["id"],
                        "data_hora": data_hora_final,
                        "status": "Pendente",
                        "observacoes": obs_completa
                    }).execute()

                    novo_id = res_novo_ag.data[0]["id"] if res_novo_ag.data else 1
                    prot_gerado = gerar_protocolo(novo_id, data_hora_final)
                    data_hora_str = f"{data_selecionada.strftime('%d/%m/%Y')} às {horario_selecionado}"
                    
                    nome_srv_final = srv_obj['nome_servico'] + (" + Decoração" if add_decoracao else "")
                    exibir_modal_confirmacao(nome_c.strip(), nome_srv_final, data_hora_str, total_servico, restante_estudio, prot_gerado)

# =======================================================
# 2. ACADEMY (CURSOS & INSCRIÇÃO COM FEEDBACK CLARO)
# =======================================================
elif aba_selecionada == "🎓 Academy (Cursos)":
    st.markdown("### 🎓 Capacitação & Formação em Nail Design")
    st.write("Aprenda as técnicas mais valorizadas com aulas práticas e acompanhamento individual.")

    try:
        res_turmas = supabase.table("turmas_curso").select("*").eq("status", "Aberta").execute()
        turmas = res_turmas.data if res_turmas.data else []
    except Exception as e:
        st.error(f"Erro ao buscar turmas: {e}")
        turmas = []

    if not turmas:
        st.info("Nenhuma turma com inscrições abertas no momento.")
    else:
        cols_t = st.columns(min(len(turmas), 3))
        for idx, turma in enumerate(turmas):
            t_id = turma["id"]
            
            res_titulares = supabase.table("inscricoes_curso").select("id").eq("turma_id", t_id).eq("tipo_vaga", "Titular").execute()
            titulares_count = len(res_titulares.data) if res_titulares.data else 0
            vagas_restantes = max(0, turma["vagas_limite"] - titulares_count)

            res_reserva = supabase.table("inscricoes_curso").select("id").eq("turma_id", t_id).eq("tipo_vaga", "Reserva").execute()
            reserva_count = len(res_reserva.data) if res_reserva.data else 0

            with cols_t[idx % 3]:
                st.markdown('<div class="site-card">', unsafe_allow_html=True)
                if vagas_restantes > 0:
                    st.markdown(f'<span style="background-color: #ecfdf5; color: #047857; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;">🟢 Vagas Abertas ({vagas_restantes} restantes)</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span style="background-color: #fffbeb; color: #b45309; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;">🟡 Lista de Espera ({reserva_count} na fila)</span>', unsafe_allow_html=True)

                st.markdown(f"""
                    <h3 style="margin-top: 10px;">{turma['nome_curso']}</h3>
                    <div style="font-size: 13px; color: #6b21a8; margin-bottom: 8px;">📅 Início: {turma['data_inicio']} • ⏱ {turma['horario']}</div>
                    <div class="card-price-value">R$ {float(turma['preco_curso']):.2f}</div>
                """, unsafe_allow_html=True)

                with st.expander("Inscrever-se Nesta Formação"):
                    with st.form(f"form_curso_{t_id}"):
                        nome_aluna = st.text_input("Nome Completo:")
                        tel_aluna = st.text_input("WhatsApp com DDD:", placeholder="Ex: 71999999999")
                        experiencia = st.selectbox("Seu Nível Atual:", ["Iniciante do Zero", "Manicure Tradicional", "Nail Designer em Aperfeiçoamento"])
                        texto_btn = "Garantir Vaga Titular ✨" if vagas_restantes > 0 else "Entrar na Fila de Espera 📌"
                        btn_curso = st.form_submit_button(texto_btn, use_container_width=True)

                    if btn_curso:
                        tel_limpo = ''.join(filter(str.isdigit, tel_aluna.strip()))
                        if not nome_aluna.strip() or len(tel_limpo) < 10:
                            st.error("Informe seu nome completo e WhatsApp com DDD.")
                        else:
                            try:
                                if vagas_restantes > 0:
                                    supabase.table("inscricoes_curso").insert({
                                        "turma_id": t_id,
                                        "nome_aluna": nome_aluna.strip(),
                                        "telefone": tel_limpo,
                                        "experiencia_previa": experiencia,
                                        "tipo_vaga": "Titular",
                                        "posicao_reserva": 0
                                    }).execute()
                                    exibir_modal_curso(nome_aluna.strip(), turma["nome_curso"], "Titular")
                                else:
                                    nova_pos = reserva_count + 1
                                    supabase.table("inscricoes_curso").insert({
                                        "turma_id": t_id,
                                        "nome_aluna": nome_aluna.strip(),
                                        "telefone": tel_limpo,
                                        "experiencia_previa": experiencia,
                                        "tipo_vaga": "Reserva",
                                        "posicao_reserva": nova_pos
                                    }).execute()
                                    exibir_modal_curso(nome_aluna.strip(), turma["nome_curso"], "Reserva", nova_pos)
                            except Exception as err:
                                st.error(f"Erro ao salvar inscrição: {err}")

                st.markdown('</div>', unsafe_allow_html=True)

# =======================================================
# 3. PAINEL DA GESTORA
# =======================================================
elif aba_selecionada == "🔐 Acesso Gestora":
    st.markdown("### 🔐 Painel Administrativo do Studio")

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
            st.success("Sessão autenticada na nuvem.")
        with col_t2:
            if st.button("Sair"):
                st.session_state.gestora_logada = False
                st.rerun()

        adm1, adm_curso, adm2, adm3, adm4, adm5 = st.tabs([
            "📋 Gestão da Agenda & Aprovações",
            "🎓 Gestão de Cursos & Turmas",
            "💅 Gerenciar Serviços (Criar / Excluir)",
            "📊 Faturamento & Métricas",
            "🗂️ Prontuário de Clientes",
            "💌 CRM & Retorno"
        ])

        # SUB-ABA 1: GESTÃO DA AGENDA
        with adm1:
            st.markdown("#### ⚙️ Controle de Agenda Geral")
            try:
                res_conf = supabase.table("configuracoes").select("*").execute()
                dict_conf = {row["chave"]: row["valor"] for row in (res_conf.data or [])}
            except Exception:
                dict_conf = {}

            col_cf1, col_cf2 = st.columns([1, 2])
            with col_cf1:
                status_atual = dict_conf.get("agenda_status", "Aberta")
                novo_status = st.toggle("Agenda Aberta ao Público", value=(status_atual == "Aberta"))
                v_status = "Aberta" if novo_status else "Fechada"
                if v_status != status_atual:
                    supabase.table("configuracoes").upsert({"chave": "agenda_status", "valor": v_status}).execute()
                    st.toast(f"Status alterado para: {v_status}")
                    st.rerun()

            with col_cf2:
                meses_atuais_str = dict_conf.get("mes_liberado", "2026-09,2026-10")
                meses_atuais_lista = [m.strip() for m in meses_atuais_str.split(",") if m.strip()]

                opcoes_meses = {
                    "2026-09": "Setembro / 2026",
                    "2026-10": "Outubro / 2026",
                    "2026-11": "Novembro / 2026",
                    "2026-12": "Dezembro / 2026",
                    "2027-01": "Janeiro / 2027",
                    "2027-02": "Fevereiro / 2027"
                }

                selecionados_meses = st.multiselect(
                    "Meses Liberados para Atendimento:",
                    options=list(opcoes_meses.keys()),
                    default=meses_atuais_lista,
                    format_func=lambda x: opcoes_meses.get(x, x)
                )

                if sorted(selecionados_meses) != sorted(meses_atuais_lista):
                    novo_meses_val = ",".join(selecionados_meses)
                    supabase.table("configuracoes").upsert({"chave": "mes_liberado", "valor": novo_meses_val}).execute()
                    st.toast("Meses atualizados!")
                    st.rerun()

            st.write("")
            dias_atuais_str = dict_conf.get("dias_funcionamento", "1,2,3,4,5")
            dias_atuais_lista = [int(d.strip()) for d in dias_atuais_str.split(",") if d.strip()]

            dias_selecionados = st.multiselect(
                "Dias de Atendimento na Semana:",
                options=list(DIAS_SEMANA_NOMES.keys()),
                default=dias_atuais_lista,
                format_func=lambda x: DIAS_SEMANA_NOMES.get(x, "")
            )

            if sorted(dias_selecionados) != sorted(dias_atuais_lista):
                novo_dias_val = ",".join([str(d) for d in sorted(dias_selecionados)])
                supabase.table("configuracoes").upsert({"chave": "dias_funcionamento", "valor": novo_dias_val}).execute()
                st.toast("Dias salvos!")
                st.rerun()

            st.divider()

            # ALERTA DE APROVAÇÃO PENDENTE DE NOTIFICAÇÃO NO WHATSAPP
            if "confirmacao_pendente" in st.session_state and st.session_state["confirmacao_pendente"]:
                d = st.session_state["confirmacao_pendente"]
                msg_conf = (
                    f"Olá {d['nome']}! ✨ Passando para confirmar que o seu agendamento no *Studio Belleza & Arte* foi CONFIRMADO!\n\n"
                    f"🔖 *Protocolo:* {d['protocolo']}\n"
                    f"💅 *Procedimento:* {d['servico']}\n"
                    f"📅 *Data e Horário:* {d['data_hora']}\n\n"
                    f"Estamos ansiosas para te receber! Qualquer imprevisto, é só nos avisar por aqui informando seu protocolo."
                )
                link_zap = f"https://api.whatsapp.com/send?phone=55{d['telefone']}&text={urllib.parse.quote(msg_conf)}"

                st.markdown(f"""
                    <div style="background: #f0fdf4; border: 2px solid #86efac; border-radius: 16px; padding: 18px; margin-bottom: 20px;">
                        <h4 style="color: #15803d; margin: 0 0 6px 0;">🎉 Horário de {d['nome']} Aprovado!</h4>
                        <div style="font-size: 14px; color: #166534; margin-bottom: 10px;">
                            Protocolo gerado: <b>{d['protocolo']}</b>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                col_z1, col_z2 = st.columns([3, 1])
                with col_z1:
                    st.link_button(f"📲 Notificar {d['nome']} no WhatsApp (com Protocolo)", link_zap)
                with col_z2:
                    if st.button("Fechar Alerta", key="btn_fechar_zap"):
                        st.session_state["confirmacao_pendente"] = None
                        st.rerun()

                st.divider()

            # ALERTA DE RECUSA PENDENTE DE NOTIFICAÇÃO NO WHATSAPP
            if "recusa_pendente" in st.session_state and st.session_state["recusa_pendente"]:
                r = st.session_state["recusa_pendente"]
                msg_rec = (
                    f"Olá {r['nome']}, aqui é do *Studio Belleza & Arte*.\n\n"
                    f"Infelizmente não foi possível confirmar o seu agendamento para o procedimento *{r['servico']}* "
                    f"marcado para *{r['data_hora']}* (Protocolo: {r['protocolo']}).\n\n"
                    f"📌 *Motivo:* {r['motivo']}\n\n"
                    f"Se desejar reagendar em outro dia ou horário, estamos à disposição no site ou por aqui! ✨"
                )
                link_zap_recusa = f"https://api.whatsapp.com/send?phone=55{r['telefone']}&text={urllib.parse.quote(msg_rec)}"

                st.markdown(f"""
                    <div style="background: #fef2f2; border: 2px solid #fca5a5; border-radius: 16px; padding: 18px; margin-bottom: 20px;">
                        <h4 style="color: #b91c1c; margin: 0 0 6px 0;">⚠️ Agendamento de {r['nome']} Recusado</h4>
                        <div style="font-size: 14px; color: #7f1d1d; margin-bottom: 6px;">
                            Protocolo: <b>{r['protocolo']}</b>
                        </div>
                        <div style="font-size: 14px; color: #7f1d1d; margin-bottom: 10px;">
                            Motivo registrado: <i>"{r['motivo']}"</i>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                col_zr1, col_zr2 = st.columns([3, 1])
                with col_zr1:
                    st.link_button(f"📲 Avisar {r['nome']} no WhatsApp (com Motivo)", link_zap_recusa)
                with col_zr2:
                    if st.button("Fechar Alerta", key="btn_fechar_zap_recusa"):
                        st.session_state["recusa_pendente"] = None
                        st.rerun()

                st.divider()

            st.markdown("#### ⏳ Solicitações Pendentes de Agendamento")
            try:
                res_pendentes = supabase.table("agendamentos").select(
                    "id, data_hora, observacoes, servicos(nome_servico), clientes(nome, telefone)"
                ).eq("status", "Pendente").order("data_hora").execute()
                pendentes = res_pendentes.data if res_pendentes.data else []
            except Exception:
                pendentes = []

            if not pendentes:
                st.info("Nenhuma solicitação pendente no momento.")
            else:
                for ag in pendentes:
                    ag_id = ag["id"]
                    c_nome = ag["clientes"]["nome"] if ag.get("clientes") else "Cliente"
                    c_tel = ag["clientes"]["telefone"] if ag.get("clientes") else ""
                    s_nome = ag["servicos"]["nome_servico"] if ag.get("servicos") else "Procedimento"
                    dh_formatada = ag["data_hora"][:16].replace("T", " ")
                    prot_ag = gerar_protocolo(ag_id, ag["data_hora"])

                    st.markdown(f"💅 **{c_nome}** — *{s_nome}*")
                    st.caption(f"🔖 Protocolo: `{prot_ag}` | 📅 Data/Hora: **{dh_formatada}** | WhatsApp: **{c_tel}**")
                    if ag.get("observacoes"):
                        st.caption(f"Obs da cliente: {ag['observacoes']}")

                    col_motivo, col_botoes = st.columns([3, 2])
                    with col_motivo:
                        motivo_recusa = st.text_input(
                            "Motivo da recusa (se for recusar):",
                            placeholder="Ex: Horário reservado para manutenção, comprovante não enviado...",
                            key=f"motivo_{ag_id}"
                        )

                    with col_botoes:
                        st.write("")
                        st.write("")
                        btn_aprovar, btn_recusar = st.columns(2)
                        with btn_aprovar:
                            if st.button("Aprovar", key=f"ap_{ag_id}", use_container_width=True):
                                supabase.table("agendamentos").update({"status": "Confirmado"}).eq("id", ag_id).execute()
                                st.session_state["confirmacao_pendente"] = {
                                    "protocolo": prot_ag,
                                    "nome": c_nome,
                                    "telefone": c_tel,
                                    "servico": s_nome,
                                    "data_hora": dh_formatada
                                }
                                st.toast("Horário Aprovado!")
                                st.rerun()
                        with btn_recusar:
                            if st.button("Recusar", key=f"rec_{ag_id}", use_container_width=True):
                                motivo_final = motivo_recusa.strip() if motivo_recusa.strip() else "Horário indisponível ou comprovante do sinal não validado."
                                supabase.table("agendamentos").update({
                                    "status": "Cancelado",
                                    "observacoes": f"[RECUSADO: {motivo_final}] " + (ag.get("observacoes") or "")
                                }).eq("id", ag_id).execute()

                                st.session_state["recusa_pendente"] = {
                                    "protocolo": prot_ag,
                                    "nome": c_nome,
                                    "telefone": c_tel,
                                    "servico": s_nome,
                                    "data_hora": dh_formatada,
                                    "motivo": motivo_final
                                }
                                st.toast("Agendamento recusado e horário liberado!")
                                st.rerun()
                    st.divider()

            st.markdown("#### ✅ Horários Confirmados (Atendimentos Agendados)")
            try:
                res_confirmados = supabase.table("agendamentos").select(
                    "id, data_hora, servicos(nome_servico), clientes(nome)"
                ).eq("status", "Confirmado").order("data_hora").execute()
                confirmados = res_confirmados.data if res_confirmados.data else []
            except Exception:
                confirmados = []

            if not confirmados:
                st.caption("Nenhum atendimento confirmado aguardando realização.")
            else:
                for conf in confirmados:
                    c1_c, c2_c, c3_c = st.columns([4, 1.2, 1.2])
                    c_nome = conf["clientes"]["nome"] if conf.get("clientes") else "Cliente"
                    s_nome = conf["servicos"]["nome_servico"] if conf.get("servicos") else "Procedimento"
                    dh_txt = conf["data_hora"][:16].replace("T", " ")
                    prot_conf = gerar_protocolo(conf["id"], conf["data_hora"])
                    with c1_c:
                        st.write(f"💅 **{c_nome}** — {s_nome} (`{prot_conf}`) às {dh_txt}")
                    with c2_c:
                        if st.button("Concluir", key=f"conc_{conf['id']}", use_container_width=True):
                            supabase.table("agendamentos").update({"status": "Concluído"}).eq("id", conf["id"]).execute()
                            st.toast("Marcado como Concluído!")
                            st.rerun()
                    with c3_c:
                        if st.button("Desmarcar", key=f"desm_{conf['id']}", use_container_width=True, help="Cancela e libera o horário imediatamente na grade pública"):
                            supabase.table("agendamentos").update({"status": "Cancelado"}).eq("id", conf["id"]).execute()
                            st.toast("Horário desmarcado e liberado na agenda!")
                            st.rerun()

        # SUB-ABA 2: GESTÃO DE CURSOS & TURMAS
        with adm_curso:
            st.markdown("#### 🎓 Gestão de Inscrições nos Cursos")

            if st.session_state.get("conf_curso_pendente"):
                al = st.session_state["conf_curso_pendente"]
                msg_aluna = (
                    f"Olá, {al['nome']}! ✨ Aqui é do *Studio Belleza & Arte*.\n\n"
                    f"Passando para te dar as boas-vindas e confirmar que a sua vaga no curso *{al['curso']}* foi GARANTIDA!\n\n"
                    f"📅 *Início:* {al['inicio']} | ⏱ *Horário:* {al['horario']}\n"
                    f"Caso tenha dúvidas sobre o material ou cronograma das aulas, estamos à total disposição."
                )
                link_zap_curso = f"https://api.whatsapp.com/send?phone=55{al['telefone']}&text={urllib.parse.quote(msg_aluna)}"

                st.markdown(f"""
                    <div style="background: #f0fdf4; border: 2px solid #86efac; border-radius: 16px; padding: 18px; margin-bottom: 20px;">
                        <h4 style="color: #15803d; margin: 0 0 6px 0;">🎉 Vaga de {al['nome']} Confirmada!</h4>
                        <div style="font-size: 14px; color: #166534; margin-bottom: 10px;">
                            Curso: <b>{al['curso']}</b> | Tipo: <b>{al['tipo']}</b>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                col_zc1, col_zc2 = st.columns([3, 1])
                with col_zc1:
                    st.link_button(f"📲 Notificar {al['nome']} no WhatsApp", link_zap_curso)
                with col_zc2:
                    if st.button("Fechar Alerta", key="btn_fechar_zap_curso"):
                        st.session_state["conf_curso_pendente"] = None
                        st.rerun()

                st.divider()

            st.markdown("##### 📝 Alunas Inscritas por Turma")
            try:
                res_all_turmas = supabase.table("turmas_curso").select("*").execute()
                turmas_cadastradas = res_all_turmas.data if res_all_turmas.data else []
            except Exception as e:
                st.error(f"Erro ao carregar turmas: {e}")
                turmas_cadastradas = []

            if not turmas_cadastradas:
                st.info("Nenhuma turma cadastrada no momento.")
            else:
                opcoes_turmas_adm = {f"{t['nome_curso']} (Início: {t['data_inicio']})": t for t in turmas_cadastradas}
                t_escolhida_nome = st.selectbox("Selecione a Turma:", list(opcoes_turmas_adm.keys()))
                t_obj = opcoes_turmas_adm[t_escolhida_nome]

                try:
                    res_inscritos = supabase.table("inscricoes_curso").select("*").eq("turma_id", t_obj["id"]).execute()
                    inscricoes = res_inscritos.data if res_inscritos.data else []
                except Exception as e:
                    st.error(f"Erro ao carregar inscrições: {e}")
                    inscricoes = []

                if not inscricoes:
                    st.caption("Nenhuma inscrição registrada nesta turma até o momento.")
                else:
                    for insc in inscricoes:
                        col_al_info, col_al_btn = st.columns([4, 2])
                        tipo_txt = "🟢 Titular" if insc["tipo_vaga"] == "Titular" else f"🟡 Fila de Espera ({insc.get('posicao_reserva', 1)}º)"
                        with col_al_info:
                            st.markdown(f"👩‍🎓 **{insc['nome_aluna']}** — {tipo_txt}")
                            st.caption(f"WhatsApp: **{insc['telefone']}** | Nível: {insc.get('experiencia_previa', 'Não informado')}")
                        with col_al_btn:
                            b_zap, b_rem = st.columns(2)
                            with b_zap:
                                if st.button("Confirmar", key=f"btn_conf_al_{insc['id']}", use_container_width=True):
                                    st.session_state["conf_curso_pendente"] = {
                                        "nome": insc["nome_aluna"],
                                        "telefone": insc["telefone"],
                                        "curso": t_obj["nome_curso"],
                                        "inicio": t_obj["data_inicio"],
                                        "horario": t_obj["horario"],
                                        "tipo": insc["tipo_vaga"]
                                    }
                                    st.rerun()
                            with b_rem:
                                if st.button("Remover", key=f"btn_rem_al_{insc['id']}", use_container_width=True):
                                    supabase.table("inscricoes_curso").delete().eq("id", insc["id"]).execute()
                                    st.toast("Inscrição removida!")
                                    st.rerun()
                        st.write("")

            st.divider()
            st.markdown("##### ➕ Criar Nova Turma de Formação")
            with st.form("form_nova_turma"):
                c_t1, c_t2 = st.columns(2)
                with c_t1:
                    novo_curso_nome = st.text_input("Nome da Formação:", placeholder="Ex: Formação Nail Designer Completa")
                    novo_curso_inicio = st.text_input("Data de Início:", placeholder="Ex: 10 de Outubro / 2026")
                with c_t2:
                    novo_curso_horario = st.text_input("Horário das Aulas:", placeholder="Ex: 09:00 às 17:00")
                    c_v1, c_v2 = st.columns(2)
                    with c_v1:
                        novo_curso_vagas = st.number_input("Vagas Titulares:", min_value=1, max_value=50, value=6)
                    with c_v2:
                        novo_curso_preco = st.number_input("Valor da Matrícula (R$):", min_value=0.0, step=50.0, value=450.0)

                btn_criar_turma = st.form_submit_button("Abrir Nova Turma ✨", use_container_width=True)

            if btn_criar_turma:
                if novo_curso_nome.strip() and novo_curso_inicio.strip():
                    supabase.table("turmas_curso").insert({
                        "nome_curso": novo_curso_nome.strip(),
                        "data_inicio": novo_curso_inicio.strip(),
                        "horario": novo_curso_horario.strip(),
                        "vagas_limite": int(novo_curso_vagas),
                        "preco_curso": float(novo_curso_preco),
                        "status": "Aberta"
                    }).execute()
                    st.toast("Turma criada e liberada no site!")
                    st.rerun()
                else:
                    st.error("Preencha o nome da formação e a data de início.")

        # SUB-ABA 3: GERENCIAR SERVIÇOS
        with adm2:
            st.markdown("#### ➕ Cadastrar Novo Procedimento")
            with st.form("form_novo_servico_gestora"):
                c_srv1, c_srv2, c_srv3 = st.columns([3, 2, 2])
                with c_srv1:
                    novo_srv_nome = st.text_input("Nome do Procedimento:", placeholder="Ex: Alongamento em Fibra de Vidro")
                with c_srv2:
                    novo_srv_duracao = st.number_input("Duração (Minutos):", min_value=15, max_value=240, step=15, value=60)
                with c_srv3:
                    novo_srv_preco = st.number_input("Preço (R$):", min_value=0.0, step=5.0, value=75.0)

                btn_salvar_srv = st.form_submit_button("Salvar Novo Serviço ✨", use_container_width=True)

            if btn_salvar_srv:
                if novo_srv_nome.strip():
                    supabase.table("servicos").insert({
                        "nome_servico": novo_srv_nome.strip(),
                        "duracao_minutos": int(novo_srv_duracao),
                        "preco": float(novo_srv_preco)
                    }).execute()
                    st.toast("Procedimento adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Informe o nome do procedimento.")

            st.divider()
            st.markdown("#### 🗑️ Procedimentos Atuais (Excluir Serviços)")
            try:
                res_lista_srv = supabase.table("servicos").select("*").order("nome_servico").execute()
                lista_srv_cadastrados = res_lista_srv.data if res_lista_srv.data else []
            except Exception:
                lista_srv_cadastrados = []

            if not lista_srv_cadastrados:
                st.info("Nenhum serviço cadastrado no momento.")
            else:
                for s_item in lista_srv_cadastrados:
                    col_info_s, col_del_s = st.columns([5, 1])
                    with col_info_s:
                        st.markdown(f"💅 **{s_item['nome_servico']}** — **R$ {float(s_item['preco']):.2f}** | ⏱ {s_item['duracao_minutos']} min")
                    with col_del_s:
                        if st.button("🗑️ Excluir", key=f"del_srv_{s_item['id']}", use_container_width=True):
                            supabase.table("servicos").delete().eq("id", s_item["id"]).execute()
                            st.toast(f"{s_item['nome_servico']} removido!")
                            st.rerun()
                    st.write("")

        # SUB-ABA 4: FATURAMENTO
        with adm3:
            st.markdown("#### 📈 Balanço Financeiro")
            try:
                res_concluidos = supabase.table("agendamentos").select(
                    "id, data_hora, servicos(nome_servico, preco), clientes(nome)"
                ).eq("status", "Concluído").execute()
                lista_concluidos = res_concluidos.data if res_concluidos.data else []
            except Exception:
                lista_concluidos = []

            if not lista_concluidos:
                st.info("Nenhum atendimento concluído registrado.")
            else:
                registros = []
                for item in lista_concluidos:
                    registros.append({
                        "Protocolo": gerar_protocolo(item["id"], item["data_hora"]),
                        "Data/Hora": item["data_hora"][:16].replace("T", " "),
                        "Cliente": item["clientes"]["nome"] if item.get("clientes") else "Não identificado",
                        "Procedimento": item["servicos"]["nome_servico"] if item.get("servicos") else "Não identificado",
                        "Valor": float(item["servicos"]["preco"]) if item.get("servicos") else 0.0,
                        "data_curta": item["data_hora"][:10],
                        "mes_ano": item["data_hora"][:7]
                    })
                df_concluidos = pd.DataFrame(registros)

                hoje_str = datetime.now().strftime("%Y-%m-%d")
                sete_dias = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                mes_atual = datetime.now().strftime("%Y-%m")

                lucro_dia = df_concluidos[df_concluidos["data_curta"] == hoje_str]["Valor"].sum()
                lucro_semana = df_concluidos[df_concluidos["data_curta"] >= sete_dias]["Valor"].sum()
                lucro_mes = df_concluidos[df_concluidos["mes_ano"] == mes_atual]["Valor"].sum()

                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.markdown(f'<div class="metric-box"><div class="metric-label">📅 Hoje</div><div class="metric-value">R$ {lucro_dia:.2f}</div></div>', unsafe_allow_html=True)
                c_m2.markdown(f'<div class="metric-box"><div class="metric-label">🗓️ 7 Dias</div><div class="metric-value">R$ {lucro_semana:.2f}</div></div>', unsafe_allow_html=True)
                c_m3.markdown(f'<div class="metric-box"><div class="metric-label">📊 Mês Atual</div><div class="metric-value">R$ {lucro_mes:.2f}</div></div>', unsafe_allow_html=True)

                st.dataframe(df_concluidos[["Protocolo", "Data/Hora", "Cliente", "Procedimento", "Valor"]], use_container_width=True, hide_index=True)

        # SUB-ABA 5: PRONTUÁRIO
        with adm4:
            st.markdown("#### 🗂️ Histórico por Cliente")
            try:
                res_clientes = supabase.table("clientes").select("id, nome, telefone").order("nome").execute()
                clientes_cad = res_clientes.data if res_clientes.data else []
            except Exception:
                clientes_cad = []

            if not clientes_cad:
                st.info("Nenhuma cliente cadastrada.")
            else:
                opcoes_c = {f"{c['nome']} ({c['telefone']})": c['id'] for c in clientes_cad}
                c_escolhida = st.selectbox("Buscar Cliente:", list(opcoes_c.keys()))
                cli_id = opcoes_c[c_escolhida]

                try:
                    res_hist = supabase.table("agendamentos").select(
                        "id, data_hora, status, observacoes, servicos(nome_servico, preco)"
                    ).eq("cliente_id", cli_id).order("data_hora", desc=True).execute()
                    hist_data = res_hist.data if res_hist.data else []
                except Exception:
                    hist_data = []

                concluidos = [h for h in hist_data if h["status"] == "Concluído"]
                total_investido = sum(float(h["servicos"]["preco"]) for h in concluidos if h.get("servicos"))

                ch1, ch2 = st.columns(2)
                ch1.metric("Atendimentos Concluídos", f"{len(concluidos)} sessão(ões)")
                ch2.metric("Total em Procedimentos", f"R$ {total_investido:.2f}")

                linhas_hist = []
                for h in hist_data:
                    linhas_hist.append({
                        "Protocolo": gerar_protocolo(h["id"], h["data_hora"]),
                        "Data/Hora": h["data_hora"][:16].replace("T", " "),
                        "Procedimento": h["servicos"]["nome_servico"] if h.get("servicos") else "N/A",
                        "Valor (R$)": float(h["servicos"]["preco"]) if h.get("servicos") else 0.0,
                        "Status": h["status"],
                        "Obs": h.get("observacoes") or ""
                    })
                st.dataframe(pd.DataFrame(linhas_hist), use_container_width=True, hide_index=True)

        # SUB-ABA 6: CRM
        with adm5:
            st.markdown("#### 💌 Alertas de Retorno (15 e 30 dias)")
            try:
                res_ret = supabase.table("agendamentos").select(
                    "data_hora, servicos(nome_servico), clientes(nome, telefone)"
                ).eq("status", "Concluído").execute()
                ret_data = res_ret.data if res_ret.data else []
            except Exception:
                ret_data = []

            lembrete_encontrado = False
            for item in ret_data:
                dt_atend = datetime.fromisoformat(item["data_hora"][:10])
                dias = (datetime.now().date() - dt_atend.date()).days
                if dias in [14, 15, 16, 29, 30, 31]:
                    lembrete_encontrado = True
                    c_nome = item["clientes"]["nome"]
                    c_tel = item["clientes"]["telefone"]
                    s_nome = item["servicos"]["nome_servico"]
                    msg_crm = f"Olá {c_nome}! Faz {dias} dias desde o seu procedimento de {s_nome} no Studio Belleza & Arte. Vamos agendar sua manutenção para manter suas unhas perfeitas?"
                    link_crm = f"https://api.whatsapp.com/send?phone=55{c_tel}&text={urllib.parse.quote(msg_crm)}"
                    st.info(f"💅 **{c_nome}** completou **{dias} dias** ({s_nome})")
                    st.link_button(f"📲 Chamar no WhatsApp ({c_tel})", link_crm)

            if not lembrete_encontrado:
                st.info("Nenhuma cliente no ciclo de retorno hoje.")

# RODAPÉ
st.markdown("""
    <div class="site-footer">
        <b>Studio Belleza & Arte</b> • Todos os direitos reservados.<br>
        <span style="opacity: 0.8;">Alongamento em Gel • Nail Art • Formação Profissional</span>
    </div>
""", unsafe_allow_html=True)
