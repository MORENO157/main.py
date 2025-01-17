import telebot
import requests
import time
import datetime
import json
import os

# Substitua pelo token do seu bot do Telegram
TOKEN = '7228922184:AAHxnph7_lbfGKKz1UHNQDtv6GtA3y1O59c'  # Token do bot
API_URL = "https://gpt.nepdevsnepcoder.workers.dev/"  # URL da API
ADM_ID = 6059898510  # Seu ID de administrador
LOG_FILE = 'error_logs.json'  # Nome do arquivo para armazenar logs
bot = telebot.TeleBot(TOKEN)

start_time = time.time()  # Tempo de início do bot

# Inicializa o arquivo de logs se não existir
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        json.dump([], f)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Envie qualquer mensagem para começar a conversar com a IA.")

@bot.message_handler(commands=['status'])
def send_status(message):
    if message.from_user.id == ADM_ID:
        uptime = time.time() - start_time
        api_status = check_api_status()
        status_message = (
            f"**Status do Bot:**\n"
            f"Uptime: {datetime.timedelta(seconds=int(uptime))}\n"
            f"Status da API: {'Funcionando' if api_status else 'Indisponível'}"
        )
        bot.reply_to(message, status_message, parse_mode='Markdown')
    else:
        bot.reply_to(message, "Você não tem permissão para usar este comando.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text
    
    # Mostrar ação de digitando
    bot.send_chat_action(message.chat.id, 'typing')

    # Obter resposta da nova API
    try:
        response = get_gemini_response(user_text)
        if response:
            bot.reply_to(message, response)
        else:
            raise Exception("Resposta vazia da API.")
    except Exception as e:
        error_message = (
            "Desculpe, ocorreu um erro ao processar sua solicitação.\n\n"
            "Por favor, tente novamente mais tarde.\n"
            "Se o problema persistir, entre em contato com o administrador."
        )
        bot.reply_to(message, error_message)
        notify_admin(message.from_user.id, e)

def get_gemini_response(text):
    try:
        params = {'question': text}
        response = requests.get(API_URL, params=params)

        # Verificar o status da resposta
        if response.status_code == 200:
            result = response.json()
            return result.get('answer', "Erro na resposta da IA.")
        else:
            raise Exception(f"Erro na solicitação: {response.status_code}")
    except Exception as e:
        raise Exception(f"Erro ao conectar à API: {str(e)}")

def check_api_status():
    try:
        response = requests.get(API_URL)
        return response.status_code == 200
    except:
        return False

def notify_admin(user_id, error):
    # Armazena o erro no arquivo JSON
    log_error(user_id, error)
    
    # Envia a mensagem para o administrador com o último erro
    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)

    if logs:
        last_error = logs[-1]  # Pega o último erro registrado
        timestamp = datetime.datetime.fromisoformat(last_error['timestamp']).strftime("%d-%m-%Y %H:%M:%S")
        log_message = (
            f"Atenção! O usuário [{user_id}] encontrou um erro.\n"
            f"Último erro registrado:\n"
            f"**Data e Horário:** {timestamp}\n"
            f"**Usuário ID:** {last_error['user_id']}\n"
            f"**Erro:** {last_error['error']}"
        )
        bot.send_message(ADM_ID, log_message, parse_mode='Markdown')

        # Remove o log após o envio
        remove_log()
    else:
        bot.send_message(ADM_ID, f"Atenção! O usuário [{user_id}] encontrou um erro, mas não há logs registrados.")

def log_error(user_id, error):
    # Lê o arquivo existente
    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)

    # Adiciona o novo erro
    logs.append({
        'timestamp': datetime.datetime.now().isoformat(),
        'user_id': user_id,
        'error': str(error)
    })

    # Escreve de volta no arquivo
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f)

def remove_log():
    # Remove todos os logs do arquivo
    with open(LOG_FILE, 'w') as f:
        json.dump([], f)  # Escreve uma lista vazia

@bot.message_handler(commands=['log'])
def send_log(message):
    if message.from_user.id == ADM_ID:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
        
        if logs:
            last_error = logs.pop(0)  # Remove o primeiro erro da lista
            timestamp = datetime.datetime.fromisoformat(last_error['timestamp']).strftime("%d-%m-%Y %H:%M:%S")
            log_message = (
                f"Último erro registrado:\n"
                f"**Data e Horário:** {timestamp}\n"
                f"**Usuário ID:** {last_error['user_id']}\n"
                f"**Erro:** {last_error['error']}"
            )
            bot.reply_to(message, log_message, parse_mode='Markdown')

            # Atualiza o arquivo JSON após remover o erro
            with open(LOG_FILE, 'w') as f:
                json.dump(logs, f)
        else:
            bot.reply_to(message, "Não há erros registrados.")
    else:
        bot.reply_to(message, "Você não tem permissão para usar este comando.")

# Inicia o bot
def main():
    bot.polling()

if __name__ == "__main__":
    main()