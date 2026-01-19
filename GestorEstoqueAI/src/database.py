import sqlite3
import pandas as pd
import os

# --- CONFIGURAÇÃO DO CAMINHO ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'estoque.db')

def init_db():
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
    cursor.execute('INSERT INTO produtos (nome, estoque_minimo) VALUES (?, ?)', (nome, int(minimo)))
    conn.commit()
    conn.close()

def registrar_movimentacao(id_produto, tipo, qtd):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    id_produto = int(id_produto)
    qtd = int(qtd)
    
    cursor.execute('INSERT INTO movimentacoes (id_produto, tipo, qtd) VALUES (?, ?, ?)', (id_produto, tipo, qtd))
    
    if tipo == 'entrada':
        cursor.execute('UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id = ?', (qtd, id_produto))
    elif tipo == 'saida':
        cursor.execute('UPDATE produtos SET estoque_atual = estoque_atual - ? WHERE id = ?', (qtd, id_produto))
        
    conn.commit()
    conn.close()

def ler_estoque():
    conn = sqlite3.connect(DB_PATH)
    # Traz produtos via pandas (geralmente funciona bem para tabelas simples)
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

def ler_dados_produto(id_produto):
    # --- MUDANÇA "MODO RAIZ" PARA EVITAR ERRO NA NUVEM ---
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Executa o SQL manualmente (sem usar o Pandas aqui)
    cursor.execute("SELECT * FROM movimentacoes WHERE id_produto = ?", (int(id_produto),))
    linhas = cursor.fetchall()
    conn.close()
    
    # 2. Constrói a tabela Pandas manualmente
    colunas = ['id', 'id_produto', 'tipo', 'qtd', 'data_hora']
    if linhas:
        df = pd.DataFrame(linhas, columns=colunas)
    else:
        # Se não tiver dados, cria tabela vazia para não quebrar o gráfico
        df = pd.DataFrame(columns=colunas)
        
    return df

def atualizar_produto(id_produto, novo_nome, novo_minimo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE produtos 
        SET nome = ?, estoque_minimo = ?
        WHERE id = ?
    ''',
