from playwright.sync_api import sync_playwright
import time

# --------- Usuário e senha ---------
USUARIO = "sofi.cruz95@gmail.com"
SENHA = "Luca2024!!"
# -----------------------------------

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Página inicial que redireciona para login se não estiver logado
    page.goto("https://prenotami.esteri.it/Home?ReturnUrl=%2fServices")
    page.wait_for_timeout(3000)

    # Preencher email e senha
    page.fill("input[name='Email']", USUARIO)
    page.fill("input[name='Password']", SENHA)

    # Clicar no botão "Avanti" para logar
    page.click("text=Avanti")
    page.wait_for_timeout(5000)

    # Ir para a página de serviços
    page.goto("https://prenotami.esteri.it/Services")
    page.wait_for_timeout(3000)

    # Espera a tabela carregar
    page.wait_for_selector("table")

    # Seleciona todas as linhas da tabela (menos o cabeçalho)
    rows = page.query_selector_all("table tbody tr")

    botao_encontrado = False

    for row in rows:
        tipologia = row.query_selector("td:nth-child(1)").inner_text().strip()
        servizio = row.query_selector("td:nth-child(2)").inner_text().strip()
        descrizione = row.query_selector("td:nth-child(3)").inner_text().strip()

        # Verifica as duas opções de Cittadinanza per discendenza
        if (tipologia == "CITTADINANZA" and 
            servizio == "Cittadinanza per discendenza" and 
            (descrizione == "cittadinanza figli minori" or descrizione == "Cittadinanza per discendenza maggiorenni (L. 74/2025)")):

            # Clica no botão PRENOTA da linha correspondente (4ª coluna)
            botao = row.query_selector("td:nth-child(4) button")
            if botao:
                botao.click()
                botao_encontrado = True
                break

    if not botao_encontrado:
        print("Botão PRENOTA não encontrado para o serviço desejado.")

    page.wait_for_timeout(2000)

    # Verificar se há vagas
    page_content = page.content().lower()
    if "stante l'elevata richiesta i posti disponibili per il servizio scelto sono esauriti" in page_content:
        print("⚠️ Ainda não há vagas disponíveis")
    else:
        print("🚨 POSSÍVEL VAGA! Entre agora!")

    # Manter navegador aberto por 10 segundos para visualização
    time.sleep(10)
    browser.close()
