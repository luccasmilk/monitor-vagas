from playwright.sync_api import sync_playwright
import os
import requests

# --------- Buscar variáveis de ambiente (Secrets do GitHub) ---------
USUARIO = os.getenv("PRENOTAMI_EMAIL")
SENHA = os.getenv("PRENOTAMI_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# --------------------------------------------------------------------

# Função para enviar alerta no Telegram
def enviar_telegram(mensagem):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensagem})
    else:
        print("⚠️ Telegram não configurado nos secrets.")

# Iniciar Playwright
p = sync_playwright().start()
browser = p.chromium.launch(headless=True)  # <-- HEADLESS no Actions
page = browser.new_page()

try:
    # Página inicial (login)
    page.goto("https://prenotami.esteri.it/Home?ReturnUrl=%2fServices")
    page.wait_for_timeout(3000)

    page.fill("input[name='Email']", USUARIO)
    page.fill("input[name='Password']", SENHA)
    page.click("text=Avanti")
    page.wait_for_timeout(5000)

    # Página de serviços
    page.goto("https://prenotami.esteri.it/Services")
    page.wait_for_selector("table")

    # Conteúdo da página em minúsculas
    page_content = page.content().lower()

    # Verificar se há vagas disponíveis
    if "posti disponibili" in page_content and "esauriti" not in page_content:
        mensagem = "🚨 POSSÍVEL VAGA NO PRENOTAMI! ENTRE AGORA!"
        enviar_telegram(mensagem)
        print(mensagem)
    else:
        print("⚠️ Ainda sem vagas disponíveis")

finally:
    # Fechar navegador e Playwright
    browser.close()
    p.stop()
