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

def rodar_monitor():
    with sync_playwright() as p:
        # Launch com argumentos para evitar detecção
        browser = p.chromium.launch(headless=True)
        
        # Criar contexto simulando um computador real (Mac/Chrome)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        try:
            print("🌐 Acessando Prenotami...")
            # Timeout de 90s para aguentar a lentidão do site
            page.goto("https://prenotami.esteri.it/Home?ReturnUrl=%2fServices", wait_until="domcontentloaded", timeout=90000)
            
            # Espera o campo de e-mail aparecer
            try:
                page.wait_for_selector("input[name='Email']", timeout=30000)
            except:
                page.screenshot(path="erro_login.png")
                print("❌ Tela de login não carregou. Print salvo.")
                return

            # Login
            page.fill("input[name='Email']", USUARIO)
            page.fill("input[name='Password']", SENHA)
            page.click("text=Avanti")
            
            # Espera carregar a página de serviços
            page.wait_for_url("**/Services", timeout=60000)
            print("🔑 Login realizado com sucesso!")

            # Analisar a tabela
            page.wait_for_selector("table", timeout=30000)
            rows = page.query_selector_all("table tbody tr")

            vaga_encontrada = False
            for row in rows:
                desc = row.inner_text()
                # Verifica se é a linha correta e se NÃO está esgotado
                if "Cittadinanza per discendenza" in desc and "maggiorenni" in desc:
                    if "esauriti" not in desc.lower():
                        vaga_encontrada = True
                        print("🚨 VAGA DETECTADA!")
                        enviar_telegram("🚨 VAGA PARA CIDADANIA! Acesse o Prenotami AGORA!")
                        break
            
            if not vaga_encontrada:
                print("⚠️ Nenhuma vaga disponível no momento.")

        except Exception as e:
            page.screenshot(path="erro_execucao.png")
            print(f"💥 Erro crítico: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    rodar_monitor()
