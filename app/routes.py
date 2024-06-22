from flask import render_template
from flask import request
from app.init import app
from app.nav import Browser

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods = ['POST'])
def search():
    produto = request.form.get("produto")
    qtd = request.form.get("qtd")

    browser = Browser()
    produtos, media = browser.busca_produto(produto, int(qtd))
    browser.quit()

    return render_template('busca.html', produtos = produtos, p = produto, media = media)