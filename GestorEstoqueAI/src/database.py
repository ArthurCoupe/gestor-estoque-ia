import sqlite3
import pandas as pd
import os

# --- CORREÇÃO DO CAMINHO (O SEGREDO DA NUVEM) ---
# Descobre onde este arquivo (database.py) está
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Monta o caminho: Pasta Atual -> Voltar um nível (..) -> Pasta data -> estoque.db
DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'estoque.db')

def init_db():
    # Cria a pasta 'data' se ela não existir (evita o erro OperationalError)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            estoque_atual INTEGER DEFAULT 0,
            estoque_minimo INTEGER DEFAULT 5
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_produto INTEGER,
            tipo TEXT,
            qtd INTEGER,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(id_produto) REFERENCES produtos(id)
        )
    ''')
    conn.commit()
    conn.close()

def adicionar_produto(nome, minimo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (nome, estoque_minimo) VALUES (?, ?)', (nome, minimo))
    conn.commit()
    conn.close()

def registrar_movimentacao(id_produto, tipo, qtd):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Registra histórico
    cursor.execute('INSERT INTO movimentacoes (id_produto, tipo, qtd) VALUES (?, ?, ?)', (id_produto, tipo, qtd))
    
    # Atualiza saldo
    if tipo == 'entrada':
        cursor.execute('UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id = ?', (qtd, id_produto))
    elif tipo == 'saida':
        cursor.execute('UPDATE produtos SET estoque_atual = estoque_atual - ? WHERE id = ?', (qtd, id_produto))
        
    conn.commit()
    conn.close()

def ler_estoque():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

def ler_dados_produto(id_produto):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM movimentacoes WHERE id_produto = ?", conn, params=(id_produto,))
    conn.close()
    return df

def atualizar_produto(id_produto, novo_nome, novo_minimo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE produtos 
        SET nome = ?, estoque_minimo = ?
        WHERE id = ?
    ''', (novo_nome, novo_minimo, id_produto))
    conn.commit()
    conn.close()

def deletar_produto(id_produto):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM produtos WHERE id = ?', (id_produto,))
    cursor.execute('DELETE FROM movimentacoes WHERE id_produto = ?', (id_produto,))
    conn.commit()
    conn.close()
