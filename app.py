import streamlit as st
import urllib.parse
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
st.set_page_config(
    page_title="Studio Belleza & Arte",
    page_icon="💅",
    layout="centered"
)

# Ocultação de elementos visuais padrão do Streamlit para manter o design limpo
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
        margin-top: 10px;
    }
    .sub-title {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 25px;
    }
    .policy-box {
        background-color: #F8F9FA;
        padding: 16px;
        border-radius: 8px;
        border-left: 5px solid #7B1FA2;
        margin-top: 15px;
        margin-bottom: 15px;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

# Título do estúdio
st.markdown('<div class="main-title">Studio Belleza & Arte</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Nail Design & Academy • Agendamento Online</div>', unsafe_allow_html=True)

# --- DADOS DOS SERVIÇOS E POLÍTICA DE COBRANÇA ---
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

# --- ETAPA 1: DADOS DO CLIENTE E AGENDAMENTO ---
st.subheader("1. Identificação e Serviços")

col_nome, col_tel = st.columns(2)
with col_nome:
    nome_cliente = st.text_input("Nome completo:")
with col_tel:
    telefone_cliente = st.text_input("WhatsApp com DDD (ex: 21969861082):")

servicos_selecionados = st.multiselect(
    "Procedimentos pretendidos:",
    options=list(SERVICOS.keys()),
    default=["Alongamento de unhas (Gel Moldado)"]
)

add_decoracao = st.checkbox("Adicionar Decoração (+ R$ 10,00)")

col_data, col_hora = st.columns(2)
with col_data:
    data_agendamento = st.date_input("Data do agendamento:", min_value=datetime.today())
with col_hora:
    hora_agendamento = st.time_input("Horário pretendido:")

# --- CÁLCULO DOS TOTAIS ---
total_servicos = sum([SERVICOS[s] for s in servicos_selecionados])
if add_decoracao:
    total_servicos += 10.00

valor_restante = max(0.00, total_servicos - VALOR_SINAL)

# --- ETAPA 2: RESUMO E POLÍTICA ---
st.markdown("---")
st.subheader("2. Resumo de Valores e Condições")

col_val1, col_val2, col_val3 = st.columns(3)
col_val1.metric("Total dos Serviços", f"R$ {total_servicos:.2f}")
col_val2.metric("Sinal de Garantia", f"R$ {VALOR_SINAL:.2f}")
col_val3.metric("Restante no Estúdio", f"R$ {valor_restante:.2f}")

st.markdown("""
<div class="policy-box">
    <strong>🔴 IMPORTANTE — Regras do Sinal e Agendamento:</strong><br>
    • A vaga só é confirmada após o pagamento do sinal de <strong>R$ 20,00</strong>;<br>
    • Válido por 30 dias e intransferível;<br>
    • Reagendamentos são permitidos avisando com pelo menos 24 horas de antecedência;<br>
    • O sinal não é devolvido em caso de desistência, cancelamento ou falta;<br>
    • Tolerância máxima de 10 minutos para atrasos.
</div>
""", unsafe_allow_html=True)

aceitou_termos = st.checkbox("Li e concordo com os termos e regras de agendamento.")

# --- ETAPA 3: CONFIRMAÇÃO E PAGAMENTO ---
if aceitou_termos and len(servicos_selecionados) > 0 and nome_cliente.strip():
    st.markdown("---")
    st.subheader("3. Pagamento do Sinal (R$ 20,00)")
    
    st.info(f"**Chave PIX:** `{CHAVE_PIX}`  \n**Titular:** {BENEFICIARIO}")
    st.link_button("💳 Pagar Sinal por Cartão de Crédito (Ton)", LINK_CARTAO)

    # Preparação da mensagem formatada para o WhatsApp
    data_formatada = data_agendamento.strftime("%d/%m/%Y")
    hora_formatada = hora_agendamento.strftime("%H:%M")
    procedimentos_texto = ", ".join(servicos_selecionados)
    if add_decoracao:
        procedimentos_texto += " + Decoração"

    msg_whatsapp = (
        f"Olá Rafaella! Realizei o meu agendamento através do site:\n\n"
        f"👤 *Cliente:* {nome_cliente}\n"
        f"📅 *Data:* {data_formatada} às {hora_formatada}\n"
        f"💅 *Procedimentos:* {procedimentos_texto}\n"
        f"💰 *Total:* R$ {total_servicos:.2f} (Sinal: R$ {VALOR_SINAL:.2f} | Restante no local: R$ {valor_restante:.2f})\n\n"
        f"Segue em anexo o comprovativo do sinal de R$ 20,00 para confirmação da vaga!"
    )
    
    msg_url = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(msg_whatsapp)}"

    st.write("")
    st.success("Tudo preenchido! Clique no botão abaixo para anexar o comprovativo no WhatsApp:")
    st.link_button("📲 Enviar Comprovativo no WhatsApp", msg_url)
else:
    st.warning("Preencha os dados do agendamento e marque a caixa de concordância com as regras para prosseguir.")
