import streamlit as st
import pandas as pd
from src.ai_engine import previsao_estoque
# Importação organizada verticalmente para evitar erros de sintaxe
from src.database import (
    init_db, 
    adicionar_produto, 
    registrar_movimentacao, 
    ler_estoque, 
    ler_dados_produto, 
    atualizar_produto, 
    deletar_produto
)
from src.google_cal import agendar_compra

# 1. Configuração da Página
st.set_page_config(page_title="Gestor de Estoque IA", layout="wide")
init_db()

# 2. Título
st.title("📦 Sistema de Estoque Inteligente")
st.caption("Gerenciado por Arthur Coupê Gonçalves")

# 3. Menu Lateral
st.sidebar.header("Navegação")
menu = st.sidebar.selectbox("Escolha uma opção:", ["Dashboard & IA", "Entrada/Saída", "Cadastrar Produto", "Gerenciar Cadastros"])

# --- PÁGINA 1: DASHBOARD ---
if menu == "Dashboard & IA":
    st.header("📊 Inteligência de Dados")
    df = ler_estoque()
    
    if df.empty:
        st.info("Nenhum produto cadastrado. Vá em 'Cadastrar Produto'.")
    else:
        # Alerta de Estoque Baixo
        criticos = df[df['estoque_atual'] <= df['estoque_minimo']]
        if not criticos.empty:
            st.error(f"🚨 Atenção! {len(criticos)} produtos estão com estoque crítico!")
            st.dataframe(criticos)
        
        # Tabela Geral
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        
        # Gráfico de IA
        st.subheader("📈 Tendência de Vendas (Histórico)")
        
        produto_grafico = st.selectbox("Selecione o Produto para Análise:", df['nome'].values)
        
        if produto_grafico:
            dados_prod = df[df['nome'] == produto_grafico].iloc[0]
            # Converte ID para int para evitar erros
            historico = ler_dados_produto(int(dados_prod['id']))
            
            if not historico.empty:
                # Prepara dados para o gráfico
                historico['data_hora'] = pd.to_datetime(historico['data_hora'])
                vendas = historico[historico['tipo'] == 'saida'].copy()
                
                if not vendas.empty:
                    # Agrupa por dia
                    vendas_diarias = vendas.groupby(vendas['data_hora'].dt.date)['qtd'].sum().reset_index()
                    vendas_diarias.columns = ['Data', 'Vendas']
                    
                    st.line_chart(vendas_diarias.set_index('Data'))
