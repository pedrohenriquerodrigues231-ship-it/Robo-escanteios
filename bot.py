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

# Conjunto para evitar alertas duplicados do mesmo jogo
jogos_notificados = set()

def enviar_alerta_telegram(mensagem):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro no Telegram: {e}")

def obter_estatisticas_jogo(fixture_id):
    """Busca as estatisticas detalhadas de um jogo especifico"""
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    try:
        res = requests.get(url, headers=headers_api)
        data = res.json()
        
        chutes_totais = 0
        escanteios = 0
        
        for team_stat in data.get("response", []):
            stats = team_stat.get("statistics", [])
            for s in stats:
                tipo = s.get("type")
                valor = s.get("value") or 0
                if tipo in ["Shots on Goal", "Shots off Goal"]:
                    chutes_totais += valor
                elif tipo == "Corner Kicks":
                    escanteios += valor
                    
        return chutes_totais, escanteios
    except Exception as e:
        print(f"Erro ao buscar estatisticas do fixture {fixture_id}: {e}")
        return 0, 0

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
            goals = jogo.get("goals", {})
            
            fixture_id = fixture.get("id")
            elapsed = fixture.get("status", {}).get("elapsed", 0)

            # Filtra jogos no 2º tempo entre o minuto 60 e 80
            if elapsed and 60 <= elapsed <= 80:
                if fixture_id not in jogos_notificados:
                    chutes, cantos = obter_estatisticas_jogo(fixture_id)
                    
                    # CRITÉRIOS DE PRESSÃO:
                    # - Pelo menos 6 finalizações acumuladas
                    # - Pelo menos 4 escanteios no jogo
                    if chutes >= 6 and cantos >= 4:
                        casa = teams.get("home", {}).get("name")
                        fora = teams.get("away", {}).get("name")
                        gols_casa = goals.get("home", 0)
                        gols_fora = goals.get("away", 0)
                        
                        msg = (
                            f"🔥 *SINAL DE PRESSÃO - ESCANTEIOS* 🔥\n\n"
                            f"⚽ *Jogo:* {casa} ({gols_casa}) x ({gols_fora}) {fora}\n"
                            f"⏱ *Tempo:* {elapsed}' min\n"
                            f"📊 *Estatísticas:* {cantos} Cantos | {chutes} Chutes\n"
                            f"🎯 *Mercado:* Over Cantos Limite / Asiáticos\n"
                            f"💰 *Stake Recomendada:* R$ 2,50\n"
                            f"⚠️ *Odd Mínima:* 1.60\n\n"
                            f"📲 *Verifique o gráfico de pressão na bet365 e entre!*"
                        )
                        enviar_alerta_telegram(msg)
                        jogos_notificados.add(fixture_id)
    except Exception as e:
        print(f"Erro na consulta de jogos: {e}")

def checar_loop():
    enviar_alerta_telegram("🚀 *Robô de Pressão de Cantos Ativado!*")
    while True:
        buscar_e_analisar_jogos()
        time.sleep(300) # Consulta a cada 5 minutos

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
