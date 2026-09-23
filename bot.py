import os
import time
import threading
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("RAPIDAPI_KEY")

headers_api = {
    "x-apisports-key": API_KEY
}

def enviar_alerta_telegram(mensagem):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro no Telegram: {e}")

def buscar_e_analisar_jogos():
    if not API_KEY:
        print("Chave de API nao configurada.")
        return

    url = "https://v3.football.api-sports.io/fixtures?live=all"
    try:
        response = requests.get(url, headers=headers_api)
        data = response.json()
        
        jogos = data.get("response", [])
        for jogo in jogos:
            fixture = jogo.get("fixture", {})
            teams = jogo.get("teams", {})
            elapsed = fixture.get("status", {}).get("elapsed", 0)

            # Filtra partidas ao vivo entre o minuto 1 e 10
            if elapsed and 1 <= elapsed <= 10:
                casa = teams.get("home", {}).get("name")
                fora = teams.get("away", {}).get("name")
                
                msg = (
                    f"🚨 *SINAL DETETADO - ESCANTEIOS 10 MIN* 🚨\n\n"
                    f"⚽ *Jogo:* {casa} x {fora}\n"
                    f"⏱ *Tempo:* {elapsed}' min\n"
                    f"🎯 *Mercado:* Over 0.5 Cantos (10 Min)\n"
                    f"💰 *Stake Recomendada:* 1 Unidade (R$ 2,50)\n"
                    f"⚠️ *Odd Minima:* 1.60\n\n"
                    f"📲 *Entre na bet365 e confirme a entrada!*"
                )
                enviar_alerta_telegram(msg)
    except Exception as e:
        print(f"Erro na consulta de jogos: {e}")

def checar_loop():
    enviar_alerta_telegram("🚀 *Robô de Sinais Automáticos Ativado com Sucesso!*")
    while True:
        buscar_e_analisar_jogos()
        time.sleep(300)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Robo Ativo!")

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=run_http_server)
    t.daemon = True
    t.start()
    checar_loop()
