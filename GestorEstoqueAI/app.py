import streamlit as st
import pandas as pd
from src.database import init_db, adicionar_produto, registrar_movimentacao, ler_estoque, ler_dados_produto, atualizar_produto, deletar_produto
from src.ai_engine import prever_esgotamento
from src.google_cal import agendar_compra

# 1. Configura a página
st.set_page_config(page_title="Gestão de Estoque IA", layout="wide")
init_db()

# 2. Título Principal
st.title("📦 Sistema de Estoque Inteligente")

# 3. Menu Lateral
st.sidebar.header("Navegação")
menu = st.sidebar.selectbox("Escolha uma opção:", ["Dashboard & IA", "Entrada/Saída", "Cadastrar Produto", "Gerenciar Cadastros"])

# 4. Lógica das Telas
if menu == "Cadastrar Produto":
    st.header("📝 Novo Produto")
    nome = st.text_input("Nome do Produto")
    minimo = st.number_input("Estoque Mínimo (Ponto de Pedido)", min_value=1, value=10)
    if st.button("Salvar Produto"):
        adicionar_produto(nome, minimo)
        st.success(f"Produto '{nome}' cadastrado com sucesso!")

elif menu == "Entrada/Saída":
    st.header("🔄 Movimentação")
    df = ler_estoque()
    
    if not df.empty:
        produto_selecionado = st.selectbox("Selecione o Produto", df['nome'].values)
        # Pega os dados do produto selecionado
        dados_prod = df[df['nome'] == produto_selecionado].iloc[0]
        id_produto = int(dados_prod['id'])
        estoque_atual = int(dados_prod['estoque_atual'])
        minimo_seguranca = int(dados_prod['estoque_minimo'])
        
        st.metric("Estoque Atual", estoque_atual)
        
        col1, col2 = st.columns(2)
        
        # Coluna de Entrada (Compra)
        with col1:
            st.subheader("Entrada (Compra)")
            qtd_entrada = st.number_input("Qtd a adicionar", min_value=1, key="ent")
            if st.button("Registrar Entrada"):
                registrar_movimentacao(id_produto, 'entrada', qtd_entrada)
                st.success("Estoque adicionado!")
                st.rerun()
                
        # Coluna de Saída (Venda)
        with col2:
            st.subheader("Saída (Venda)")
            qtd_saida = st.number_input("Qtd a vender", min_value=1, key="sai")
            if st.button("Registrar Venda"):
                if qtd_saida <= estoque_atual:
                    registrar_movimentacao(id_produto, 'saida', qtd_saida)
                    
                    # Checagem da IA
                    novo_estoque = estoque_atual - qtd_saida
                    
                    # --- CORREÇÃO AQUI ---
                    if novo_estoque <= minimo_seguranca:
                        msg = agendar_compra(produto_selecionado, novo_estoque)
                        # Removemos o rerun() daqui para a mensagem não sumir
                        st.warning(f"⚠️ ESTOQUE CRÍTICO! {msg}")
                        st.write(f"O estoque caiu para: **{novo_estoque}**") 
                    else:
                        st.success("Venda realizada!")
                        st.rerun() # Se estiver tudo bem, pode recarregar
                else:
                    st.error("Erro: Você não tem estoque suficiente!")
    else:
        st.info("Nenhum produto cadastrado. Vá ao menu 'Cadastrar Produto' primeiro.")

elif menu == "Dashboard & IA":
    st.header("📊 Inteligência de Dados")
    df = ler_estoque()
    
    if not df.empty:
        # Mostra a Tabela
        st.dataframe(df, use_container_width=True)
        st.divider()
        
        st.subheader("📈 Tendência de Vendas (Histórico)")
        
        # Cria um gráfico para cada produto
        for index, row in df.iterrows():
            historico = ler_dados_produto(row['id'])
            previsao = prever_esgotamento(historico, row['estoque_atual'])
            
            with st.expander(f"Análise Completa: {row['nome']}"):
                # 1. Mostra a previsão em texto
                if isinstance(previsao, int):
                    st.write(f"📉 Previsão de Esgotamento: **{previsao} dias**")
                else:
                    st.info(previsao)
                
                # 2. Mostra o Gráfico (NOVIDADE)
                if not historico.empty:
                    # Agrupa vendas por dia para o gráfico ficar bonito
                    historico['data_hora'] = pd.to_datetime(historico['data_hora'])
                    grafico_data = historico.set_index('data_hora')['qtd']
                    st.line_chart(grafico_data)
                else:
                    st.write("Sem dados de vendas para gerar gráfico.")
    else:
        st.write("Sem dados para analisar.")

elif menu == "Gerenciar Cadastros":
    st.header("⚙️ Gerenciar Produtos")
    df = ler_estoque()
    
    if not df.empty:
        # Seleciona o produto para editar/excluir
        produto_selecionado = st.selectbox("Selecione o Produto para Editar/Excluir:", df['nome'].values)
        
        # Pega os dados atuais desse produto
        dados_prod = df[df['nome'] == produto_selecionado].iloc[0]
        id_selecionado = int(dados_prod['id'])
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        # --- COLUNA DE EDIÇÃO ---
        with col1:
            st.subheader("✏️ Editar")
            with st.form(key='form_edicao'):
                novo_nome = st.text_input("Nome do Produto", value=dados_prod['nome'])
                novo_minimo = st.number_input("Estoque Mínimo", min_value=1, value=int(dados_prod['estoque_minimo']))
                btn_editar = st.form_submit_button("Salvar Alterações")
                
                if btn_editar:
                    atualizar_produto(id_selecionado, novo_nome, novo_minimo)
                    st.success("Produto atualizado com sucesso!")
                    st.rerun()

        # --- COLUNA DE EXCLUSÃO ---
        with col2:
            st.subheader("🗑️ Excluir")
            st.warning("Atenção: A exclusão é permanente e apaga o histórico deste produto.")
            if st.button("Excluir Produto Permanentemente", type="primary"):
                deletar_produto(id_selecionado)
                st.success("Produto excluído!")
                st.rerun()
                
    else:

        st.info("Nenhum produto cadastrado.")
