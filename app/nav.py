from app.db import DatabaseProdutos
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())

class Produtos:
    def __init__(self, nome, vendedor, avaliacao, qtdavaliacao, valor, parcela, desconto):
        self.nome = nome
        self.vendedor = vendedor
        self.avaliacao = avaliacao
        self.qtdavaliacao = qtdavaliacao
        self.valor = valor
        self.parcela = parcela
        self.desconto = desconto

    def __str__(self):
        return f"Produto: {self.nome}\nVendedor: {self.vendedor}\nAvaliação: {self.avaliacao}\nQtd Avaliações: {self.qtdavaliacao}\nPreço: R$ {self.valor} {self.parcela}\nDesconto: {self.desconto}\n" + "="*50

class Browser:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.brs = webdriver.Chrome(service=service, options=options)
        self.brs.get("https://mercadolivre.com.br")
        self.brs.maximize_window()

    def regexValor(self, multi):
        m = re.search(r'(\d+)x', multi).group(1)
        return m
    
    def calcular_media(self, valores):
        if len(valores) == 0:
            return 0
        soma = sum(valores)
        media = soma / len(valores)
        return round(media, 2)
    
    def busca_produto(self, produto, qtd):
        self.brs.find_element(By.ID, "cb1-edit").send_keys(produto, Keys.ENTER)

        produtos = []
        media = []

        for i in range(1, qtd + 1):

            xnome = f"//div[contains(@class, 'ui-search-main') and contains(@class, 'ui-search-main--only-products')]//section//ol//li[contains(@class, 'ui-search-layout__item') and not(contains(@class, 'ui-search-layout__item--intervention'))][{i}]//div//div//div[2]//div[contains(@class, 'ui-search-item__group--title')]//a//h2"
            nome = self.brs.find_element(By.XPATH, xnome).text

            xvendedor = f"//div[contains(@class, 'ui-search-main') and contains(@class, 'ui-search-main--only-products')]//section//ol//li[contains(@class, 'ui-search-layout__item') and not(contains(@class, 'ui-search-layout__item--intervention'))][{i}]//div//div//div[2]//div[contains(@class, 'ui-search-item__group--title')]//p[contains(@class, 'ui-search-official-store-label')]"
            try: 
                vendedor = self.brs.find_element(By.XPATH, xvendedor).text[4:]
            except NoSuchElementException:
                vendedor = ""
            
            xavaliacao = f"//div[contains(@class, 'ui-search-main') and contains(@class, 'ui-search-main--only-products')]//section//ol//li[contains(@class, 'ui-search-layout__item') and not(contains(@class, 'ui-search-layout__item--intervention'))][{i}]//span[contains(@class, 'ui-search-reviews__rating-number')]"
            try:
                avaliacao = self.brs.find_element(By.XPATH, xavaliacao).text
            except NoSuchElementException:
                avaliacao = ""

            xqtdavaliacao = f"//div[contains(@class, 'ui-search-main') and contains(@class, 'ui-search-main--only-products')]//section//ol//li[contains(@class, 'ui-search-layout__item') and not(contains(@class, 'ui-search-layout__item--intervention'))][{i}]//span[contains(@class, 'ui-search-reviews__amount')]"
            try:
                qtdavaliacao = self.brs.find_element(By.XPATH, xqtdavaliacao).text[1:-1]
            except NoSuchElementException:
                qtdavaliacao = ""
            
            xpreco = f"//div[contains(@class, 'ui-search-main') and contains(@class, 'ui-search-main--only-products')]//section//ol//li[contains(@class, 'ui-search-layout__item') and not(contains(@class, 'ui-search-layout__item--intervention'))][{i}]//div[contains(@class, 'ui-search-item__group--price ui-search-item__group--price-grid-container')]//span[contains(@class, 'andes-money-amount--cents-superscript')]//span[contains(@class, 'andes-money-amount__fraction')]"
            xcents = f"//div[contains(@class, 'ui-search-main') and contains(@class, 'ui-search-main--only-products')]//section//ol//li[contains(@class, 'ui-search-layout__item') and not(contains(@class, 'ui-search-layout__item--intervention'))][{i}]//div[contains(@class, 'ui-search-item__group--price ui-search-item__group--price-grid-container')]//span[contains(@class, 'andes-money-amount__cents--superscript-24')]"
            try:
                preco = self.brs.find_element(By.XPATH, xpreco).text
            except NoSuchElementException:
                preco = ""
            
            try:
                cents = self.brs.find_element(By.XPATH, xcents).text
                valor = preco + "," + cents
            except NoSuchElementException:
                valor = preco
                cents = ""

            media.append(float(valor.replace(".", "").replace(",", ".")))

            xmulti = f"//div[contains(@class, 'ui-search-main') and contains(@class, 'ui-search-main--only-products')]//section//ol//li[contains(@class, 'ui-search-layout__item') and not(contains(@class, 'ui-search-layout__item--intervention'))][{i}]//span[contains(@class, 'ui-search-item__group__element ui-search-installments')]"
            try:
                parcelado = self.brs.find_element(By.XPATH, xmulti).text.replace("\n", " ").replace(" , ", ",")
            except:
                parcelado = ""

            xdesconto = f"//div[contains(@class, 'ui-search-main') and contains(@class, 'ui-search-main--only-products')]//section//ol//li[contains(@class, 'ui-search-layout__item') and not(contains(@class, 'ui-search-layout__item--intervention'))][{i}]//p[contains(@class, 'coupon')]"
            try:
                desconto = self.brs.find_element(By.XPATH, xdesconto).text[6:]
            except NoSuchElementException:
                desconto = ""     

            produtoEncontrado = Produtos(nome, vendedor, avaliacao, qtdavaliacao, valor, parcelado, desconto)
            produtos.append(produtoEncontrado)

        data = DatabaseProdutos()
        for produto in produtos:
            data.inserir(produto.nome, produto.vendedor, produto.avaliacao, produto.qtdavaliacao, produto.valor, produto.parcela, produto.desconto)
        data.close()

        mediafinal = str(self.calcular_media(media)).replace(".", ",")

        return produtos, mediafinal

    def quit(self):
        self.brs.quit()