import os
import requests
from playwright.sync_api import sync_playwright

USUARIO = os.getenv("PRENOTAMI_EMAIL")
SENHA = os.getenv("PRENOTAMI_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensagem: str):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensagem})
        except Exception as e:
            print(f"Erro Telegram: {e}")

def executar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, id Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()

        try:
            print("🌐 Acessando Prenotami...")
            page.goto("https://prenotami.esteri.it/Home?ReturnUrl=%2fServices", timeout=90000)
            
            page.wait_for_selector("input[name='Email']", timeout=45000)
            page.fill("input[name='Email']", USUARIO)
            page.fill("input[name='Password']", SENHA)
            page.click("text=Avanti")
            
            page.wait_for_url("**/Services", timeout=60000)
            page.wait_for_selector("table", timeout=30000)

            rows = page.query_selector_all("table tbody tr")
            vaga = False
            for row in rows:
                txt = row.inner_text()
                if "Cittadinanza per discendenza maggiorenni (L. 74/2025)" in txt:
                    if "esauriti" not in txt.lower():
                        vaga = True
                        enviar_telegram("🚨 VAGA ENCONTRADA!")
                        break
            
            if not vaga:
                print("⚠️ Sem vagas no momento.")

        except Exception as e:
            print(f"💥 Erro detectado: {e}")
            # SALVA O PRINT COM NOME SIMPLES
            page.screenshot(path="debug.png", full_page=True)
            raise e 
        finally:
            browser.close()

if __name__ == "__main__":
    executar()
