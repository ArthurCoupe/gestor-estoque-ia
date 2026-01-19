import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def agendar_compra(nome_produto, qtd_atual):
    creds = None
    
    # Tenta carregar o token existente
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Se não houver credenciais válidas, limpa e pede login novo
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                # Se falhar o refresh, deleta o token ruim e força login
                if os.path.exists('token.json'):
                    os.remove('token.json')
                return "Erro de autenticação. Tente registrar a venda novamente."
        else:
            if not os.path.exists('credentials.json'):
                return "Erro: Arquivo credentials.json não encontrado!"
            
            # Força a abertura do navegador de forma limpa
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0, prompt='select_account')
            
        # Salva o novo token limpo
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Cria o evento na agenda
        evento = {
            'summary': f'🚨 COMPRAR: {nome_produto}',
            'description': f'O sistema de IA detectou estoque baixo: {qtd_atual} unidades.',
            'start': {
                'dateTime': datetime.datetime.now().isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'colorId': '11' # Cor Vermelha
        }

        event = service.events().insert(calendarId='primary', body=evento).execute()
        return f"Agendado na Agenda! (ID: {event.get('id')})"
        
    except Exception as e:
        return f"Erro ao criar evento: {str(e)}"