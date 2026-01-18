from playwright.sync_api import sync_playwright
import os
import requests
import time

# --------- Usuário e senha via GitHub Secrets ---------
USUARIO = os.getenv("PRENOTAMI_EMAIL")
SENHA = os.getenv("PRENOTAMI_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# ------------------------------------------------------

def enviar_telegram(mensagem: str):
    """Envia alerta via Telegram"""
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensagem})
            print(f"Mensagem enviada: {mensagem}")
        except Exception as e:
            print(f"Erro ao enviar Telegram: {e}")
    else:
        print("⚠️ Telegram não configurado corretamente nos secrets.")

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)  # Headless obrigatório no GitHub Actions
page = browser.new_page()

try:
    # Página inicial (redireciona para login)
    page.goto("https://prenotami.esteri.it/Home?ReturnUrl=%2fServices")
    page.wait_for_selector("input[name='Email']", timeout=60000)  # Espera segura
    page.fill("input[name='Email']", USUARIO)
    page.fill("input[name='Password']", SENHA)
    page.click("text=Avanti")
    page.wait_for_timeout(5000)

    # Ir para a página de serviços
    page.goto("https://prenotami.esteri.it/Services")
    page.wait_for_selector("table", timeout=60000)

    # Seleciona as linhas da tabela
    rows = page.query_selector_all("table tbody tr")

    botao_encontrado = False

    for row in rows:
        tipologia = row.query_selector("td:nth-child(1)").inner_text().strip()
        servizio = row.query_selector("td:nth-child(2)").inner_text().strip()
        descrizione = row.query_selector("td:nth-child(3)").inner_text().strip()

        if (
            tipologia == "CITTADINANZA"
            and servizio == "Cittadinanza per discendenza"
            and "Cittadinanza per discendenza maggiorenni (L. 74/2025)" in descrizione
        ):
            botao = row.query_selector("td:nth-child(4) button")
            if botao:
                botao.click()
                botao_encontrado = True
                print("✅ Botão PRENOTA clicado")
                break

    if not botao_encontrado:
        print("❌ Botão PRENOTA não encontrado para o serviço desejado.")

    page.wait_for_timeout(3000)

    # Verificar se há vagas
    page_content = page.content().lower()

    if "posti disponibili" in page_content and "esauriti" not in page_content:
        mensagem = "🚨 POSSÍVEL VAGA! ENTRE AGORA!"
        enviar_telegram(mensagem)
        print(mensagem)
    else:
        print("⚠️ Ainda não há vagas disponíveis")

finally:
    browser.close()
    p.stop()
