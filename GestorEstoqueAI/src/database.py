import sqlite3
import pandas as pd
from datetime import datetime

# Define onde o banco será salvo
DB_PATH = "data/estoque.db"

def init_db():
    """Cria as tabelas se elas não existirem"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tabela de Produtos
    c.execute('''CREATE TABLE IF NOT EXISTS produtos 
                 (id INTEGER PRIMARY KEY, nome TEXT, estoque_atual INTEGER, estoque_minimo INTEGER)''')
    # Tabela de Movimentações (Histórico para a IA)
    c.execute('''CREATE TABLE IF NOT EXISTS movimentacoes 
                 (id INTEGER PRIMARY KEY, produto_id INTEGER, tipo TEXT, qtd INTEGER, data_hora TEXT)''')
    conn.commit()
    conn.close()

def adicionar_produto(nome, estoque_minimo):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO produtos (nome, estoque_atual, estoque_minimo) VALUES (?, 0, ?)", (nome, estoque_minimo))
    conn.commit()
    conn.close()

def registrar_movimentacao(produto_id, tipo, qtd):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Atualiza Estoque Atual
    if tipo == 'entrada':
        c.execute("UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id = ?", (qtd, produto_id))
    elif tipo == 'saida':
        c.execute("UPDATE produtos SET estoque_atual = estoque_atual - ? WHERE id = ?", (qtd, produto_id))
    
    # Registra Histórico
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO movimentacoes (produto_id, tipo, qtd, data_hora) VALUES (?, ?, ?, ?)", 
              (produto_id, tipo, qtd, data_atual))
    
    conn.commit()
    conn.close()

def ler_dados_produto(produto_id):
    conn = sqlite3.connect(DB_PATH)
    # Pega histórico de saídas (vendas) para a IA
    query = f"SELECT data_hora, qtd FROM movimentacoes WHERE produto_id = {produto_id} AND tipo = 'saida'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def ler_estoque():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

def atualizar_produto(id_produto, novo_nome, novo_minimo):
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE produtos 
        SET nome = ?, estoque_minimo = ?
        WHERE id = ?
    ''', (novo_nome, novo_minimo, id_produto))
    conn.commit()
    conn.close()

def deletar_produto(id_produto):
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    # Deleta o produto
    cursor.execute('DELETE FROM produtos WHERE id = ?', (id_produto,))
    # Opcional: Deletar o histórico de vendas desse produto para não sujar o banco
    cursor.execute('DELETE FROM movimentacoes WHERE id_produto = ?', (id_produto,))
    conn.commit()
    conn.close()