import os
import requests
from playwright.sync_api import sync_playwright

# --------- Configurações ---------
USUARIO = os.getenv("PRENOTAMI_EMAIL")
SENHA = os.getenv("PRENOTAMI_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensagem: str):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensagem})
            print(f"✅ Telegram enviado: {mensagem}")
        except Exception as e:
            print(f"❌ Erro Telegram: {e}")

def monitorar():
    with sync_playwright() as p:
        # Launch com argumentos para esconder o rastro de automação
        browser = p.chromium.launch(headless=True, args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox"
        ])
        
        # Contexto com User-Agent real e linguagem em português/italiano
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR",
            viewport={'width': 1280, 'height': 720}
        )
        
        page = context.new_page()
        
        # Script injetado para remover a marca de "bot" do navegador
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            print("🚀 Iniciando acesso ao Prenotami...")
            # Aumentamos o timeout para 90 segundos devido à lentidão do site
            page.goto("https://prenotami.esteri.it/Home?ReturnUrl=%2fServices", wait_until="networkidle", timeout=90000)

            # Tenta encontrar o campo de login
            try:
                page.wait_for_selector("input[name='Email']", timeout=45000)
            except Exception:
                page.screenshot(path="erro_login.png")
                print("❌ Falha ao carregar formulário. Print 'erro_login.png' salvo.")
                return

            # Preenchimento
            page.fill("input[name='Email']", USUARIO)
            page.fill("input[name='Password']", SENHA)
            page.click("text=Avanti")
            
            # Espera carregar a página de serviços
            print("🔑 Aguardando redirecionamento após login...")
            page.wait_for_url("**/Services", timeout=60000)
            
            # Analisar tabela de serviços
            page.wait_for_selector("table", timeout=30000)
            rows = page.query_selector_all("table tbody tr")
            
            vaga_encontrada = False
            for row in rows:
                texto_linha = row.inner_text()
                if "Cittadinanza per discendenza" in texto_linha and "maggiorenni" in texto_linha:
                    if "esauriti" not in texto_linha.lower():
                        vaga_encontrada = True
                        print("🚨 VAGA ENCONTRADA!")
                        enviar_telegram("🚨 VAGA DISPONÍVEL! Corra para o Prenotami!")
                        break
            
            if not vaga_encontrada:
                print("⚠️ Nenhuma vaga livre no momento.")

        except Exception as e:
            print(f"💥 Erro durante execução: {str(e)[:100]}...")
            page.screenshot(path="erro_execucao.png")
        finally:
            browser.close()

if __name__ == "__main__":
    monitorar()
