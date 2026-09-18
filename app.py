import streamlit as st
import urllib.parse
from datetime import datetime, date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Studio Belleza & Arte",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização visual (mantém o visual limpo sem cabeçalhos/rodapés do Streamlit)
st.markdown("""
    <style>
    footer {visibility: hidden; display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    .main-title {
        font-size: 2.2rem;
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
    .policy-box {
        background-color: #F8F9FA;
        padding: 16px;
        border-radius: 8px;
        border-left: 5px solid #7B1FA2;
        margin: 15px 0;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .card {
        background: #FFFFFF;
        border: 1px solid #EEE;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown('<div class="main-title">Studio Belleza & Arte</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Nail Design & Academy • Sistema Integrado</div>', unsafe_allow_html=True)

# --- NAVEGAÇÃO POR ABAS / MÓDULOS ---
aba_agendamento, aba_servicos, aba_academy, aba_gestao = st.tabs([
    "📅 Agendamento Online",
    "💅 Catálogo de Serviços",
    "🎓 Academy (Cursos)",
    "🔒 Acesso Gestora"
])

# Constantes da Rafaella
SERVICOS = {
    "Alongamento de unhas (Gel Moldado)": 150.00,
    "Manutenção de Unha em Gel": 100.00,
    "Esmaltação em gel": 70.00,
    "Pedicure simples": 30.00
}
VALOR_SINAL = 20.00
CHAVE_PIX = "21969861082"
BENEFICIARIO = "Rafaella Aquino – Stone IP S.A"
LINK_CARTAO = "https://payment-link-v3.ton.com.br/pl_3dPKpGv5Zrb9l9aH6tjlw1agNjLX0m4D"
WHATSAPP_NUMERO = "5521969861082"

# =========================================================
# ABA 1: AGENDAMENTO ONLINE (COM AS REGRAS E POLÍTICA)
# =========================================================
with aba_agendamento:
    st.subheader("Reserve o seu Horário")
    
    col_cli1, col_cli2 = st.columns(2)
    with col_cli1:
        nome_cliente = st.text_input("Nome completo:")
    with col_cli2:
        telefone_cliente = st.text_input("WhatsApp com DDD (ex: 21969861082):")

    servicos_selecionados = st.multiselect(
        "Selecione os procedimentos desejados:",
        options=list(SERVICOS.keys()),
        default=["Alongamento de unhas (Gel Moldado)"]
    )

    add_decoracao = st.checkbox("Adicionar Decoração (+ R$ 10,00)")

    col_d, col_h = st.columns(2)
    with col_d:
        data_agendamento = st.date_input("Escolha a data:", min_value=date.today())
    with col_h:
        hora_agendamento = st.time_input("Escolha o horário:")

    # Cálculo dos valores
    total_servicos = sum([SERVICOS[s] for s in servicos_selecionados])
    if add_decoracao:
        total_servicos += 10.00
    valor_restante = max(0.00, total_servicos - VALOR_SINAL)

    st.markdown("---")
    st.markdown("#### Resumo do Atendimento")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total do Atendimento", f"R$ {total_servicos:.2f}")
    c2.metric("Sinal de Garantia (Trava)", f"R$ {VALOR_SINAL:.2f}")
    c3.metric("Restante no Estúdio", f"R$ {valor_restante:.2f}")

    st.markdown("""
    <div class="policy-box">
        <strong>🔴 IMPORTANTE — Regras de Agendamento e Sinal:</strong><br>
        • Sua vaga só estará garantida após a confirmação do pagamento do sinal de <strong>R$ 20,00</strong>;<br>
        • O sinal é válido por 30 dias e intransferível;<br>
        • Reagendamentos são permitidos com no mínimo 24h de antecedência;<br>
        • O sinal não é devolvido em caso de desistência, cancelamento ou falta;<br>
        • Tolerância máxima de 10 minutos para atrasos.
    </div>
    """, unsafe_allow_html=True)

    aceitou_termos = st.checkbox("Li e concordo com as regras de agendamento e política do sinal.")

    if aceitou_termos and len(servicos_selecionados) > 0 and nome_cliente.strip():
        st.markdown("---")
        st.markdown("#### Pagamento do Sinal (R$ 20,00)")
        
        col_pay1, col_pay2 = st.columns(2)
        with col_pay1:
            st.info(f"**Chave PIX:** `{CHAVE_PIX}`  \n**Favorecido:** {BENEFICIARIO}")
        with col_pay2:
            st.write("Prefere pagar com cartão?")
            st.link_button("💳 Pagar Sinal no Cartão (Ton)", LINK_CARTAO)

        # Montagem do WhatsApp
        data_f = data_agendamento.strftime("%d/%m/%Y")
        hora_f = hora_agendamento.strftime("%H:%M")
        procs_f = ", ".join(servicos_selecionados)
        if add_decoracao:
            procs_f += " + Decoração"

        msg = (
            f"Olá Rafaella! Acabei de agendar pelo site:\n\n"
            f"👤 *Cliente:* {nome_cliente}\n"
            f"📅 *Data:* {data_f} às {hora_f}\n"
            f"💅 *Procedimentos:* {procs_f}\n"
            f"💰 *Total:* R$ {total_servicos:.2f} (Sinal: R$ {VALOR_SINAL:.2f} | Restante: R$ {valor_restante:.2f})\n\n"
            f"Estou enviando o comprovante do sinal de R$ 20,00 em anexo!"
        )
        url_wa = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(msg)}"

        st.success("Tudo certo! Clique abaixo para confirmar seu agendamento no WhatsApp:")
        st.link_button("📲 Enviar Comprovante no WhatsApp", url_wa)
    else:
        st.info("Informe seu nome, marque os procedimentos e confirme o aceite das regras para liberar a etapa do sinal.")

# =========================================================
# ABA 2: CATÁLOGO DE SERVIÇOS E PROCEDIMENTOS
# =========================================================
with aba_servicos:
    st.subheader("Procedimentos do Estúdio")
    st.write("Conheça as especialidades oferecidas pelo Studio Belleza & Arte:")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("""
        <div class="card">
            <h4>✨ Alongamento em Gel Moldado</h4>
            <p>Alongamento estruturado respeitando a anatomia da lâmina natural. Acabamento fino, resistente e com aspecto super natural.</p>
            <p><strong>Duração média:</strong> 120 min | <strong>Investimento:</strong> R$ 150,00</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
            <h4>🔄 Manutenção de Unha em Gel</h4>
            <p>Nivelamento, troca de estrutura e fortalecimento para manter seu alongamento sempre impecável e seguro.</p>
            <p><strong>Duração média:</strong> 90 min | <strong>Investimento:</strong> R$ 100,00</p>
        </div>
        """, unsafe_allow_html=True)

    with col_s2:
        st.markdown("""
        <div class="card">
            <h4>💎 Esmaltação em Gel</h4>
            <p>Unhas secas instantaneamente na cabine com brilho espelhado e durabilidade estendida de 15 a 25 dias sem lascar.</p>
            <p><strong>Duração média:</strong> 60 min | <strong>Investimento:</strong> R$ 70,00</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
            <h4>🦶 Pedicure Simples & Spa dos Pés</h4>
            <p>Higienização profunda, cutilagem alinhada e esmaltação tradicional para o bem-estar e estética dos pés.</p>
            <p><strong>Duração média:</strong> 40 min | <strong>Investimento:</strong> R$ 30,00</p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# ABA 3: ACADEMY (CURSOS & TREINAMENTOS)
# =========================================================
with aba_academy:
    st.subheader("Cursos Profissionalizantes — Rafaella Aquino")
    st.write("Torne-se uma Nail Designer reconhecida com as técnicas mais atualizadas do mercado.")

    col_cur1, col_cur2 = st.columns(2)
    with col_cur1:
        st.markdown("""
        <div class="card">
            <h4>🎓 Formação Nail Designer Iniciante</h4>
            <ul>
                <li>Anatomia das unhas e biossegurança completa;</li>
                <li>Técnica de gel moldado sem segredos;</li>
                <li>Controle de produto e lixamento técnico simétrico;</li>
                <li>Certificado reconhecido + Suporte pós-curso.</li>
            </ul>
            <p><strong>Carga horária:</strong> 16h presenciais (Vagas limitadas)</p>
        </div>
        """, unsafe_allow_html=True)

    with col_cur2:
        st.markdown("""
        <div class="card">
            <h4>⚡ Especialização: Rapidez em Mesa & Manutenção</h4>
            <ul>
                <li>Redução do tempo de atendimento para até 60 minutos;</li>
                <li>Técnicas com brocas de tungstênio e diamantadas;</li>
                <li>Precificação e gestão da agenda de clientes.</li>
            </ul>
            <p><strong>Carga horária:</strong> 8h de imersão prática</p>
        </div>
        """, unsafe_allow_html=True)

    msg_curso = "Olá Rafaella! Tenho interesse em obter mais informações sobre as próximas turmas dos cursos da Academy."
    link_curso_wa = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(msg_curso)}"
    st.link_button("💬 Consultar Turmas e Valores dos Cursos", link_curso_wa)

# =========================================================
# ABA 4: ÁREA DA GESTORA (PAINEL ADMINISTRATIVO)
# =========================================================
with aba_gestao:
    st.subheader("Painel de Controle da Gestora")
    
    senha = st.text_input("Digite a senha de acesso administrativo:", type="password")
    
    # Exemplo simples de barreira de acesso para a Rafaella
    if senha == "admin123" or senha == "rafaella":
        st.success("Autenticação realizada com sucesso!")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Status da Agenda", "Disponível")
        m2.metric("Sinal Obrigatório", f"R$ {VALOR_SINAL:.2f}")
        m3.metric("Tempo de Tolerância", "10 min")
        
        st.markdown("#### Configurações Rápidas")
        st.write("Nesta área a gestora visualiza o fluxo de caixa, relatórios de atendimentos e bloqueia datas específicas da semana.")
        st.checkbox("Bloquear agendamentos para o próximo Domingo", value=True)
        st.checkbox("Habilitar recebimento via link de cartão", value=True)
    elif senha:
        st.error("Senha incorreta. Acesso restrito à gestora do estúdio.")
