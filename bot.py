import os
import requests
import time

# Configurações com suas chaves do Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def enviar_alerta_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")


def checar_jogos():
    # Exemplo de lógica de verificação
    # O bot irá rodar em segundo plano e notificar oportunidades
    mensagem = (
        "🚨 *SINAL DETECTADO: CANTOS 0-10'* 🚨\n\n"
        "⚽ *Jogo Analisado*\n"
        "📊 *Estratégia:* Over 0.5 Cantos nos Primeiros 10 Minutos\n"
        "💰 *Entrada:* 1 Stake (R$ 2,50)\n"
        "🎯 *Odd mínima:* 1.60\n\n"
        "Abra a Bet365 e confira a intensidade do jogo!"
    )
    enviar_alerta_telegram(mensagem)


if __name__ == "__main__":
    enviar_alerta_telegram("✅ *Robô de Cantos Iniciado com Sucesso!*")
    while True:
        # Checa a cada 5 minutos
        time.sleep(300)
