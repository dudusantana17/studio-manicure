import streamlit as st
import urllib.parse
from datetime import datetime, date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Studio Belleza & Arte",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização visual limpa e elegante
st.markdown("""
    <style>
    footer {visibility: hidden; display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #4A154B;
        text-align: center;
        margin-top: 5px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #666;
        text-align: center;
        margin-bottom: 25px;
    }
    .card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
        margin-bottom: 20px;
        min-height: 220px;
    }
    .policy-box {
        background-color: #F8F9FA;
        padding: 16px;
        border-radius: 8px;
        border-left: 5px solid #7B1FA2;
        margin: 15px 0;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown('<div class="main-title">Studio Belleza & Arte</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Nail Design & Academy • Agendamento & Informações</div>', unsafe_allow_html=True)

# --- DADOS E CONSTANTES ---
SERVICOS_INFO = {
    "Alongamento de unhas (Gel Moldado)": {
        "preco": 150.00,
        "tempo": "120 min",
        "desc": "Alongamento estruturado respeitando a anatomia natural, com acabamento fino, alta resistência e aspecto impecável."
    },
    "Manutenção de Unha em Gel": {
        "preco": 100.00,
        "tempo": "90 min",
        "desc": "Nivelamento da estrutura, reforço do ponto de tensão e acabamento para manter seu alongamento sempre seguro."
    },
    "Esmaltação em gel": {
        "preco": 70.00,
        "tempo": "60 min",
        "desc": "Unhas secas instantaneamente na cabine com brilho espelhado e durabilidade prolongada de até 20 dias sem lascar."
    },
    "Pedicure simples": {
        "preco": 30.00,
        "tempo": "40 min",
        "desc": "Higienização profunda, cutilagem técnica delicada e acabamento tradicional para o cuidado e estética dos pés."
    }
}

VALOR_SINAL = 20.00
CHAVE_PIX = "21969861082"
BENEFICIARIO = "Rafaella Aquino – Stone IP S.A"
LINK_CARTAO = "https://payment-link-v3.ton.com.br/pl_3dPKpGv5Zrb9l9aH6tjlw1agNjLX0m4D"
WHATSAPP_NUMERO = "5521969861082"

# Controle de estado para saber qual serviço foi clicado
if "servico_selecionado" not in st.session_state:
    st.session_state["servico_selecionado"] = None

# --- NAVEGAÇÃO SUPERIOR ---
aba_vitrine, aba_academy, aba_gestao = st.tabs([
    "💅 Catálogo de Serviços",
    "🎓 Academy (Cursos)",
    "🔒 Acesso Gestora"
])

# =========================================================
# ABA 1: CATÁLOGO DE SERVIÇOS (VITRINE COM BOTÕES DE AGENDAR)
# =========================================================
with aba_vitrine:
    st.subheader("Procedimentos Disponíveis")
    st.write("Escolha o procedimento desejado para abrir os horários e concluir seu agendamento:")

    col1, col2 = st.columns(2)
    servicos_nomes = list(SERVICOS_INFO.keys())

    for idx, nome_serv in enumerate(servicos_nomes):
        dados = SERVICOS_INFO[nome_serv]
        coluna = col1 if idx % 2 == 0 else col2
        
        with coluna:
            st.markdown(f"""
            <div class="card">
                <h4 style="color: #4A154B; margin-bottom: 5px;">✨ {nome_serv}</h4>
                <p style="color: #555; font-size: 0.95rem;">{dados['desc']}</p>
                <p>⏱️ <strong>Duração:</strong> {dados['tempo']} &nbsp;|&nbsp; 💰 <strong>Valor:</strong> R$ {dados['preco']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"📅 Agendar {nome_serv}", key=f"btn_{idx}", use_container_width=True):
                st.session_state["servico_selecionado"] = nome_serv

    # --- MODAL / SEÇÃO DE AGENDAMENTO (SÓ APARECE AO CLICAR) ---
    if st.session_state["servico_selecionado"]:
        serv_atual = st.session_state["servico_selecionado"]
        preco_base = SERVICOS_INFO[serv_atual]["preco"]

        st.markdown("---")
        st.markdown(f"### 📝 Agendamento: <span style='color:#7B1FA2'>{serv_atual}</span>", unsafe_allow_html=True)

        col_cli1, col_cli2 = st.columns(2)
        with col_cli1:
            nome_cliente = st.text_input("Seu Nome Completo:")
        with col_cli2:
            telefone_cliente = st.text_input("WhatsApp com DDD (ex: 21969861082):")

        col_d, col_h, col_dec = st.columns([1.2, 1, 1.2])
        with col_d:
            data_agendamento = st.date_input("Escolha a Data:", min_value=date.today())
        with col_h:
            hora_agendamento = st.time_input("Escolha o Horário:")
        with col_dec:
            st.write("Adicionais:")
            add_decoracao = st.checkbox("Adicionar Decoração (+ R$ 10,00)")

        # Cálculo
        total_servico = preco_base + (10.00 if add_decoracao else 0.00)
        valor_restante = max(0.00, total_servico - VALOR_SINAL)

        # Resumo Financeiro
        st.markdown("#### Resumo do Atendimento")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total dos Serviços", f"R$ {total_servico:.2f}")
        c2.metric("Sinal de Garantia (Trava)", f"R$ {VALOR_SINAL:.2f}")
        c3.metric("Restante a pagar no Estúdio", f"R$ {valor_restante:.2f}")

        # Caixa com as Regras
        st.markdown("""
        <div class="policy-box">
            <strong>🔴 IMPORTANTE — Regras de Agendamento e Sinal:</strong><br>
            • Sua vaga só é garantida após o pagamento do sinal de <strong>R$ 20,00</strong>;<br>
            • O sinal é válido por 30 dias e intransferível;<br>
            • Reagendamentos são aceitos com no mínimo 24h de antecedência;<br>
            • O sinal não é devolvido em caso de cancelamento ou falta;<br>
            • Tolerância máxima de 10 minutos para atrasos.
        </div>
        """, unsafe_allow_html=True)

        aceitou_termos = st.checkbox("Li e concordo integralmente com as regras de agendamento e o sinal.")

        if aceitou_termos and nome_cliente.strip():
            st.markdown("#### Pagamento do Sinal (R$ 20,00)")
            col_pix, col_ton = st.columns(2)
            with col_pix:
                st.info(f"**Chave PIX:** `{CHAVE_PIX}`  \n**Favorecido:** {BENEFICIARIO}")
            with col_ton:
                st.write("Pagamento via Cartão:")
                st.link_button("💳 Pagar Sinal no Cartão de Crédito (Ton)", LINK_CARTAO, use_container_width=True)

            data_f = data_agendamento.strftime("%d/%m/%Y")
            hora_f = hora_agendamento.strftime("%H:%M")
            proc_f = serv_atual + (" + Decoração" if add_decoracao else "")

            msg = (
                f"Olá Rafaella! Acabei de agendar pelo site:\n\n"
                f"👤 *Cliente:* {nome_cliente}\n"
                f"📅 *Data:* {data_f} às {hora_f}\n"
                f"💅 *Procedimento:* {proc_f}\n"
                f"💰 *Total:* R$ {total_servico:.2f} (Sinal: R$ {VALOR_SINAL:.2f} | Restante: R$ {valor_restante:.2f})\n\n"
                f"Estou enviando em anexo o comprovante do sinal de R$ 20,00 para garantir minha vaga!"
            )
            url_wa = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(msg)}"

            st.write("")
            st.success("Tudo preenchido! Clique no botão abaixo para abrir o WhatsApp da Rafaella e anexar o comprovante:")
            st.link_button("📲 Enviar Comprovante no WhatsApp", url_wa, use_container_width=True)
        else:
            st.warning("Preencha seu nome e aceite as regras acima para liberar os links de pagamento do sinal.")

# =========================================================
# ABA 2: ACADEMY (CURSOS & FORMAÇÃO)
# =========================================================
with aba_academy:
    st.subheader("Cursos Profissionalizantes — Rafaella Aquino")
    st.write("Capacite-se na área da beleza e aprenda as técnicas de Nail Design mais requisitadas.")

    col_cur1, col_cur2 = st.columns(2)
    with col_cur1:
        st.markdown("""
        <div class="card">
            <h4 style="color: #4A154B;">🎓 Formação Nail Designer Iniciante</h4>
            <ul>
                <li>Anatomia das unhas e biossegurança completa;</li>
                <li>Técnica de gel moldado sem segredos;</li>
                <li>Controle de produto e lixamento simétrico;</li>
                <li>Certificado reconhecido + Suporte individual pós-curso.</li>
            </ul>
            <p><strong>Carga horária:</strong> 16h presenciais (Vagas limitadas)</p>
        </div>
        """, unsafe_allow_html=True)

    with col_cur2:
        st.markdown("""
        <div class="card">
            <h4 style="color: #4A154B;">⚡ Especialização: Rapidez em Mesa & Manutenção</h4>
            <ul>
                <li>Redução do tempo de atendimento para até 60 minutos;</li>
                <li>Técnicas com brocas de tungstênio e diamantadas;</li>
                <li>Precificação e gestão de clientes.</li>
            </ul>
            <p><strong>Carga horária:</strong> 8h de imersão prática</p>
        </div>
        """, unsafe_allow_html=True)

    msg_curso = "Olá Rafaella! Tenho interesse em saber datas e valores das próximas turmas dos cursos da Academy."
    link_curso_wa = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(msg_curso)}"
    st.link_button("💬 Consultar Turmas e Valores dos Cursos", link_curso_wa)

# =========================================================
# ABA 3: ÁREA DA GESTORA
# =========================================================
with aba_gestao:
    st.subheader("Painel Administrativo do Estúdio")
    senha = st.text_input("Senha de acesso da gestora:", type="password")
    
    if senha in ["admin123", "rafaella"]:
        st.success("Acesso autorizado!")
        m1, m2, m3 = st.columns(3)
        m1.metric("Status da Agenda", "Disponível")
        m2.metric("Sinal Obrigatório", f"R$ {VALOR_SINAL:.2f}")
        m3.metric("Tolerância", "10 min")
        
        st.markdown("#### Configurações Rápidas")
        st.checkbox("Bloquear agendamentos para o próximo Domingo", value=True)
        st.checkbox("Habilitar recebimento via link de cartão", value=True)
    elif senha:
        st.error("Senha incorreta. Acesso restrito.")
