from playwright.sync_api import sync_playwright
import os
import requests

# ------------------ Ler Secrets do GitHub ------------------
USUARIO = os.getenv("PRENOTAMI_EMAIL")
SENHA = os.getenv("PRENOTAMI_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# ------------------------------------------------------------

def enviar_telegram(mensagem: str):
    """Envia mensagem para Telegram usando bot token e chat_id"""
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensagem})
            print(f"Mensagem enviada: {mensagem}")
        except Exception as e:
            print(f"Erro ao enviar mensagem Telegram: {e}")
    else:
        print("⚠️ Telegram não configurado corretamente nos secrets.")

# ------------------ Iniciar Playwright ------------------
p = sync_playwright().start()
browser = p.chromium.launch(headless=True)  # HEADLESS obrigatório no Actions
page = browser.new_page()

try:
    # Página inicial (login)
    page.goto("https://prenotami.esteri.it/Home?ReturnUrl=%2fServices")

    # Esperar o campo Email aparecer (até 60s)
    page.wait_for_selector("input[name='Email']", timeout=60000)
    page.fill("input[name='Email']", USUARIO)

    page.wait_for_selector("input[name='Password']", timeout=60000)
    page.fill("input[name='Password']", SENHA)

    # Clicar em Avanti
    page.click("text=Avanti")

    # Esperar página carregar
    page.wait_for_timeout(5000)

    # Ir para página de serviços
    page.goto("https://prenotami.esteri.it/Services")
    page.wait_for_selector("table", timeo
