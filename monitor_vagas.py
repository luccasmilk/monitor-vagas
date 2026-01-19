import os
import requests
from playwright.sync_api import sync_playwright

# --------- Configurações via GitHub Secrets ---------
USUARIO = os.getenv("PRENOTAMI_EMAIL")
SENHA = os.getenv("PRENOTAMI_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensagem: str):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensagem})
            print(f"✅ Telegram: {mensagem}")
        except Exception as e:
            print(f"❌ Erro Telegram: {e}")

def executar_bot():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print("🌐 Acessando Prenotami...")
            page.goto("https://prenotami.esteri.it/Home?ReturnUrl=%2fServices", wait_until="domcontentloaded", timeout=90000)
            
            # Login
            page.wait_for_selector("input[name='Email']", timeout=45000)
            page.fill("input[name='Email']", USUARIO)
            page.fill("input[name='Password']", SENHA)
            page.click("text=Avanti")
            
            print("🔑 Aguardando página de serviços...")
            page.wait_for_url("**/Services", timeout=60000)
            page.wait_for_selector("table", timeout=30000)

            # --- BUSCA ESPECÍFICA ---
            rows = page.query_selector_all("table tbody tr")
            vaga_encontrada = False

            for row in rows:
                colunas = row.query_selector_all("td")
                if len(colunas) < 3: continue
                
                servizio = colunas[1].inner_text().strip()
                descrizione = colunas[2].inner_text().strip()
                
                # Filtro exato conforme seu print
                if "Cittadinanza per discendenza" in servizio and "maggiorenni (L. 74/2025)" in descrizione:
                    texto_completo = row.inner_text().lower()
                    
                    if "esauriti" not in texto_completo:
                        vaga_encontrada = True
                        msg = "🚨 VAGA ENCONTRADA: Cittadinanza per discendenza maggiorenni (L. 74/2025)!"
                        print(msg)
                        enviar_telegram(msg)
                        page.screenshot(path="VAGA_CONFIRMADA.png")
                        break
            
            if not vaga_encontrada:
                print("⚠️ Serviço encontrado, mas as vagas estão esgotadas (esauriti).")

        except Exception as e:
            print(f"💥 Erro: {e}")
            page.screenshot(path="erro_debug.png")
        finally:
            browser.close()

if __name__ == "__main__":
    executar_bot()
