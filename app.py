import streamlit as st
import urllib.parse
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL E ESTILO ---
st.set_page_config(page_title="Studio Belleza & Arte", page_icon="💅", layout="centered")

# Oculta elementos padrão do Streamlit para manter o visual limpo
st.markdown("""
    <style>
    footer {visibility: hidden; display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    .main-title {font-size: 2.2rem; font-weight: 700; color: #4A154B; text-align: center;}
    .sub-title {font-size: 1rem; color: #666; text-align: center; margin-bottom: 25px;}
    .policy-box {background-color: #F8F9FA; padding: 15px; border-radius: 8px; border-left: 4px solid #7B1FA2; margin: 15px 0;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Studio Belleza & Arte</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Nail Design & Academy • Agendamento Online</div>', unsafe_allow_html=True)

# --- DADOS DOS SERVIÇOS E POLÍTICA ---
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

# --- ETAPA 1: DADOS DA CLIENTE E SERVIÇOS ---
st.subheader("1. Seus Dados e Procedimentos")

col_nome, col_tel = st.columns(2)
with col_nome:
    nome_cliente = st.text_input("Seu nome completo:")
with col_tel:
    telefone_cliente = st.text_input("WhatsApp com DDD (ex: 21999999999):")

servicos_selecionados = st.multiselect(
    "Selecione os procedimentos desejados:",
    options=list(SERVICOS.keys()),
    default=["Alongamento de unhas (Gel Moldado)"]
)

add_decoracao = st.checkbox("Adicionar Decoração (+ R$ 10,00)")

col_data, col_hora = st.columns(2)
with col_data:
    data_agendamento = st.date_input("Escolha a data:", min_value=datetime.today())
with col_hora:
    hora_agendamento = st.time_input("Escolha o horário:")

# --- CÁLCULO DOS VALORES ---
total_servicos = sum([SERVICOS[s] for s in servicos_selecionados])
if add_decoracao:
    total_servicos += 10.00

valor_restante = max(0.00, total_servicos - VALOR_SINAL)

# --- ETAPA 2: RESUMO E POLÍTICA ---
st.markdown("---")
st.subheader("2. Resumo do Agendamento")

col_val1, col_val2, col_val3 = st.columns(3)
col_val1.metric("Total dos Serviços", f"R$ {total_servicos:.2f}")
col_val2.metric("Sinal de Garantia", f"R$ {VALOR_SINAL:.2f}")
col_val3.metric("Restante no Atendimento", f"R$ {valor_restante:.2f}")

st.markdown("""
<div class="policy-box">
    <strong>📌 Regras de Agendamento e Sinal:</strong><br>
    • Sua vaga só é confirmada após a realização do pagamento do sinal;<br>
    • O sinal é válido por 30 dias e intransferível;<br>
    • Reagendamentos são permitidos com no mínimo 24h de antecedência;<br>
    • O sinal não é devolvido em caso de cancelamento ou falta;<br>
    • Tolerância máxima de 10 minutos para atrasos.
</div>
""", unsafe_allow_html=True)

aceitou_termos = st.checkbox("Li e concordo integralmente com as regras de agendamento.")

# --- ETAPA 3: PAGAMENTO DO SINAL E ENVIO ---
if aceitou_termos and len(servicos_selecionados) > 0 and nome_cliente.strip():
    st.markdown("---")
    st.subheader("3. Garantir Vaga com Sinal (R$ 20,00)")
    
    st.info(f"**Chave PIX:** `{CHAVE_PIX}`\n\n**Titular:** {BENEFICIARIO}")
    st.link_button("💳 Pagar Sinal no Cartão de Crédito", LINK_CARTAO)

    # Montagem da mensagem automática para o WhatsApp
    data_formatada = data_agendamento.strftime("%d/%m/%Y")
    hora_formatada = hora_agendamento.strftime("%H:%M")
    lista_procedimentos = ", ".join(servicos_selecionados)
    if add_decoracao:
        lista_procedimentos += " + Decoração"

    msg_whatsapp = (
        f"Olá Rafaella! Agendei meu horário pelo site:\n\n"
        f"👤 *Cliente:* {nome_cliente}\n"
        f"📅 *Data:* {data_formatada} às {hora_formatada}\n"
        f"💅 *Procedimentos:* {lista_procedimentos}\n"
        f"💰 *Total:* R$ {total_servicos:.2f} (Sinal: R$ {VALOR_SINAL:.2f} | Restante: R$ {valor_restante:.2f})\n\n"
        f"Segue em anexo o comprovante do sinal de R$ 20,00 para confirmação!"
    )
    msg_url = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(msg_whatsapp)}"

    st.write("")
    st.success("Tudo pronto! Clique no botão abaixo para enviar o comprovante diretamente no WhatsApp da Rafaella:")
    st.link_button("📲 Enviar Comprovante no WhatsApp", msg_url)
else:
    st.warning("Preencha seu nome, selecione os serviços e confirme o aceite das regras para liberar o pagamento do sinal.")
