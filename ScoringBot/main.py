from typing import Final
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import mysql.connector
from tabulate import tabulate
from prettytable import PrettyTable

TOKEN: Final = '7148715635:AAHQ-x2P3iB6AVjf5DhIykFG8tEluLvPZok'
BOT_USERNAME: Final = '@Scoring_For_TAs_Bot'

table = PrettyTable()
queue = []
previous_command: str = 'None'
previous_query: str = 'None'
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.message.from_user.full_name}!\nWelcom to Scoring Bot"
                                    f"\nIf u don't know how to use this bot use /help command or ask your "
                                    f"questions from below ID:\n@Mohammad_Jafari81")
    global previous_command
    previous_command = 'start'
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Helping part')
    global previous_command
    previous_command = 'help'
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command!')
    global previous_command
    previous_command = 'custom'

async def table_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text('Connecting to server...')
    queue.append(msg)
    db = connect_database()

    # Check Connection

    if db.is_connected():

        msg = await update.message.reply_text("connected succesfully✅")
        queue.append(msg)
        global previous_command
        if previous_command != 'show':
            table.clear()
            mycursor = db.cursor()
            query: str = "select userid, username from user"
            global previous_query
            previous_query = query
            mycursor.execute(query)
            info = mycursor.fetchall()
            a = []
            i = info[0]
            len1 = len(i)
            for i in range(0, len1):
                a.append(i)
            print(a)
            table.field_names = a
            for i in info:
                print(list(i))
                table.add_row(list(i))


        # Deleting 2 Prewious messages

        await context.bot.delete_message(chat_id=queue[0].chat_id, message_id=queue[0].message_id)
        await context.bot.delete_message(chat_id=queue[1].chat_id, message_id=queue[1].message_id)

        queue.clear()
        # Print table
        response = '```\n{}```'.format(table.get_string())
        await update.message.reply_text(response, parse_mode='Markdown')
        print(tabulate(info, tablefmt="presto", showindex=True))
        previous_command = 'show'
    else:
        msg = await update.message.reply_text("Error while connecting to MySQL❌")
        queue.append(msg)



# Connect
def connect_database():
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="phase_2"
        )
        return db

    #finally:
        #if db.is_connected():
           # mycursor.close()
           # db.close()
           # print("MySQL connection is closed")
# Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()
    numbers: str = processed.split(" ")
    if 'hello' in processed:
        return 'کتابچی دوست دارم ❤️💕'
    if 'how are u' in processed:
        return "I'am Good!"
    if len(numbers) == 2 and numbers[0].isdigit() and numbers[1].isdigit():
        return f"your number is {int(numbers[0]) + int(numbers[1])}"
    return 'I do not understand what you wrote... :('

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User ({update.message.chat.id}) in {message_type}: '{text}'")

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('show', table_command))
    # Messages
    app.add_handler(MessageHandler(filters.TEXT,handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print("Polling ...")
    app.run_polling(poll_interval=1)




