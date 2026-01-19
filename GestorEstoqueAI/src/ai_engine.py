import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime

def prever_esgotamento(df_historico, estoque_atual):
    """
    Retorna em quantos dias o estoque vai acabar.
    """
    # Verifica se tem dados suficientes (pelo menos 5 vendas para ter precisão)
    if len(df_historico) < 5:
        return "Dados insuficientes para IA (mínimo 5 vendas)"

    # Preparação dos dados
    df_historico['data_hora'] = pd.to_datetime(df_historico['data_hora'])
    
    # Transforma datas em números (dias) para a matemática funcionar
    # Ex: dia 1, dia 2, dia 3...
    df_historico['dias_ordinal'] = df_historico['data_hora'].map(datetime.toordinal)
    
    # X = Tempo, Y = Vendas Acumuladas
    # A IA vai entender a "velocidade" de venda
    X = df_historico[['dias_ordinal']].values
    y = df_historico['qtd'].cumsum().values # Acumulado de vendas

    # Cria o modelo de Regressão Linear
    model = LinearRegression()
    model.fit(X, y)
    
    # Coeficiente angular = Vendas por dia (velocidade)
    vendas_por_dia = model.coef_[0]
    
    # Evita divisão por zero ou números negativos se as vendas pararam
    if vendas_por_dia <= 0:
        return "Vendas estagnadas (Estoque seguro)"

    # Previsão final
    dias_restantes = int(estoque_atual / vendas_por_dia)
    return dias_restantes