import sqlite3
import datetime
import os

class DatabaseProdutos:
    def __init__(self):
        data_hora = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.nome_bd = os.path.join("app/sql", f"consulta_{data_hora}.db") #Sem permissão para gerar na raiz então criei um subdiretorio
        self.connect = sqlite3.connect(self.nome_bd)
        
        self.cursor = self.connect.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                vendedor TEXT,
                avaliacao TEXT,
                qtdavaliacao TEXT,
                valor TEXT,
                parcela TEXT,
                desconto TEXT
            )
        ''')

    def inserir(self, nome, vendedor, avaliacao, qtdavaliacao, valor, parcela, desconto):
        self.cursor.execute('''
        INSERT INTO produtos (nome, vendedor, avaliacao, qtdavaliacao, valor, parcela, desconto)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, vendedor, avaliacao, qtdavaliacao, valor, parcela, desconto))
        self.connect.commit()

    def close(self):
        self.connect.close()