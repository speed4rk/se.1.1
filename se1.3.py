import telebot
import yfinance as yf
import matplotlib.pyplot as plt
from io import BytesIO
import sys
from datetime import datetime, timedelta

# Token do seu bot do Telegram
token = "7009596555:AAF5eH8zqWmnVK5bLLmbH4K0Awygv7b6B7g"

# Lista de códigos de ações do Ibovespa (com base na composição atual)
ibovespa_stocks = [
    "ABEV3.SA", "ASAI3.SA", "AZUL4.SA", "B3SA3.SA", "BBAS3.SA", "BBDC4.SA",
    "BBSE3.SA", "BPAC11.SA", "BRDT3.SA", "BRFS3.SA", "BRKM5.SA", "BRML3.SA",
    "BTOW3.SA", "CCRO3.SA", "CIEL3.SA", "CMIG4.SA", "COGN3.SA", "CPFE3.SA",
    "CPLE6.SA", "CRFB3.SA", "CSAN3.SA", "CSNA3.SA", "CVCB3.SA", "CYRE3.SA",
    "ECOR3.SA", "EGIE3.SA", "ELET3.SA", "ELET6.SA", "EMBR3.SA", "ENBR3.SA",
    "ENEV3.SA", "ENGI11.SA", "EQTL3.SA", "FLRY3.SA", "GGBR4.SA", "GNDI3.SA",
    "GOAU4.SA", "GOLL4.SA", "HAPV3.SA", "HGTX3.SA", "HYPE3.SA", "IGTA3.SA",
    "IRBR3.SA", "ITSA4.SA", "ITUB4.SA", "JBSS3.SA", "JHSF3.SA", "KLBN11.SA",
    "LAME4.SA", "LCAM3.SA", "LREN3.SA", "MGLU3.SA", "MRFG3.SA", "MRVE3.SA",
    "MULT3.SA", "NTCO3.SA", "PCAR3.SA", "PETR3.SA", "PETR4.SA", "QUAL3.SA",
    "RADL3.SA", "RAIL3.SA", "RENT3.SA", "SANB11.SA", "SBSP3.SA", "SULA11.SA",
    "SUZB3.SA", "TAEE11.SA", "TIMS3.SA", "TOTS3.SA", "UGPA3.SA", "USIM5.SA",
    "VALE3.SA", "VIVT3.SA", "VVAR3.SA", "WEGE3.SA", "YDUQ3.SA"
]

# Criação do objeto bot
bot = telebot.TeleBot(token)


# Função para lidar com o comando /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
                 "Bem-vindo! Digite o código da ação da bolsa brasileira para obter o último preço de negociação.")


# Função para lidar com mensagens de texto
@bot.message_handler(func=lambda message: True)
def get_stock_info(message):
    # Obtém o texto da mensagem
    text = message.text.upper()

    # Verifica se algum dos códigos de ações do Ibovespa está presente na mensagem
    for stock_code in ibovespa_stocks:
        if stock_code in text:
            try:
                # Obtém a data atual
                end_date = datetime.now()
                # Calcula a data de início (30 dias atrás)
                start_date = end_date - timedelta(days=30)

                # Obtém os dados históricos da ação nos últimos 30 dias com intervalo diário
                stock_data = yf.download(stock_code, start=start_date, end=end_date, interval='1d')

                # Verifica se há dados disponíveis
                if len(stock_data) == 0:
                    bot.reply_to(message, f"Não há dados disponíveis para a ação {stock_code} nos últimos 30 dias.")
                    sys.exit()  # Encerra a execução do bot

                # Calcula a variação da ação no dia
                variation_today = (stock_data["Close"].iloc[-1] - stock_data["Close"].iloc[-2]) / stock_data["Close"].iloc[-2] * 100

                # Gera o gráfico de linha
                plt.figure(figsize=(10, 6))
                plt.plot(stock_data.index, stock_data["Close"], label="Preço de Fechamento")
                plt.title(f"Gráfico Diário de Preço de Fechamento (Últimos 30 dias) - {stock_code}")
                plt.xlabel("Data")
                plt.ylabel("Preço (R$)")
                plt.legend()

                # Salva o gráfico em um buffer de bytes
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)

                # Envia o gráfico como foto
                bot.send_photo(message.chat.id, buffer)

                # Obtém o último preço de negociação da ação
                last_price = stock_data["Close"].iloc[-1]
                bot.reply_to(message, f"O último preço de negociação da ação {stock_code} é R$ {last_price:.2f}, com variação de {variation_today:.2f}% no dia.")
                sys.exit()  # Encerra a execução do bot após enviar o resultado
            except Exception as e:
                bot.reply_to(message,
                             f"Erro ao obter informações da ação {stock_code}. Verifique se o código está correto.")
                sys.exit()  # Encerra a execução do bot em caso de erro

    # Se nenhum código de ação do Ibovespa for encontrado na mensagem
    bot.reply_to(message,
                 "Nenhum código de ação do Ibovespa encontrado na mensagem. Por favor, insira um código de ação válido.")


# Iniciando o bot
bot.polling()
