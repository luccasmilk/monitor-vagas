from playwright.sync_api import sync_playwright
import time
import os
import requests

USUARIO = os.getenv("PRENOTAMI_EMAIL")
SENHA = os.getenv("PRENOTAMI_PASSWORD")

def enviar_telegram(mensagem):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": mensagem})

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
page = browser.new_page()

page.goto("https://prenotami.esteri.it/Home?ReturnUrl=%2fServices")
page.wait_for_timeout(3000)

page.fill("input[name='Email']", USUARIO)
page.fill("input[name='Password']", SENHA)
page.click("text=Avanti")
page.wait_for_timeout(5000)

page.goto("https://prenotami.esteri.it/Services")
page.wait_for_selector("table")

page_content = page.content().lower()

if "posti disponibili" in page_content and "esauriti" not in page_content:
    enviar_telegram("🚨 POSSÍVEL VAGA NO PRENOTAMI! ENTRE AGORA!")
    print("Vaga encontrada")
else:
    print("Ainda sem vagas")

browser.close()
p.stop()
