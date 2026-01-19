import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def previsao_estoque(estoque_atual, historico_vendas):
    """
    Calcula em quantos dias o estoque vai acabar baseada na média de vendas.
    """
    # Se não tiver dados suficientes (menos de 2 dias de vendas), retorna previsão padrão
    if historico_vendas.empty or len(historico_vendas) < 2:
        return 30  # Chute seguro de 1 mês
        
    try:
        # Prepara os dados para a IA (Regressão Linear Simples)
        historico_vendas['dias'] = (historico_vendas['data_hora'] - historico_vendas['data_hora'].min()).dt.days
        
        X = historico_vendas['dias'].values.reshape(-1, 1)
        y = historico_vendas['qtd'].values
        
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        # Prever vendas futuras (tendência diária)
        venda_media_diaria = modelo.coef_[0]
        
        # Se a venda média for negativa ou zero (não está vendendo), estoque dura "infinito"
        if venda_media_diaria <= 0:
            return 999
            
        dias_restantes = estoque_atual / venda_media_diaria
        return dias_restantes
        
    except Exception:
        # Se a IA falhar por qualquer motivo matemático, retorna 15 dias por segurança
        return 15
