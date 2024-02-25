from telegram import Update, Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import mysql.connector
from tabulate import tabulate
from prettytable import PrettyTable
from bot_info import BOT_TOKEN, BOT_USERNAME, ADMINS_userID, ADMINS_USERNAME
from Userl import User

online_users = []
table = PrettyTable()
queue = []
previous_command: str = 'None'
previous_query: str = 'None'
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role:str
    if str(update.message.from_user.id) in ADMINS_userID:
        role = 'ADMIN'
    else:
        role = 'NORMAL'

    user = User(update.message.from_user.full_name, update.message.from_user.id,update.message.from_user.username, role)
    online_users.append(user)

    await update.message.reply_text(f"Hello {user.fullname}!\nWelcom to Scoring Bot"
                                    f"\nIf u don't know how to use this bot use /help command or ask your "
                                    f"questions from below ID:\n{ADMINS_USERNAME[0]}", reply_markup=user.get_keyboard())
    # Sending Requests to Admins
    if str(user.userid) not in ADMINS_userID:
        for adminsUserID in ADMINS_userID:

            msg = (f"#request\n"
                   f"User {update.message.from_user.full_name} "
                   f"with ID <{update.message.from_user.id}>  ")
            if user.username != None:
                msg = msg + f"and username @{user.username} requested to be added as TA"
            else:
                msg = msg + f"and username {user.username} requested to be added as TA"
            await context.bot.send_message(chat_id=adminsUserID, text=msg)

    global previous_command
    previous_command = 'start'

def exist_in_online_Users(userid):
    for user in online_users:
        if userid == user.userid:
            return True
    return False
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    iu:int = -1
    for i in range (0, len(online_users)):
        if online_users[i].userid == update.message.from_user.id:
            iu = i
    await update.message.reply_text('Helping part', reply_markup=online_users[iu].get_keyboard())
    global previous_command
    previous_command = 'help'
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command!')
    global previous_command
    previous_command = 'custom'

async def table_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        global previous_command

        if previous_command != 'show':

            msg = await update.message.reply_text('Connecting to server...')
            queue.append(msg)
            db = connect_database("phase_2")

            # Check Connection


            table.clear()
            mycursor = db.cursor()
            query: str = "select userid, groupid, role from groupmembership"
            global previous_query
            previous_query = query
            mycursor.execute(query)
            info = mycursor.fetchall()
            msg = await update.message.reply_text("connected succesfully✅")
            queue.append(msg)
            column_names = [i[0] for i in mycursor.description]
            table.field_names = column_names
            for i in info:
                print(list(i))
                table.add_row(list(i))

            # Deleting 2 Prewious messages

            await context.bot.delete_message(chat_id=queue[1].chat_id, message_id=queue[1].message_id)
            await context.bot.delete_message(chat_id=queue[0].chat_id, message_id=queue[0].message_id)

            queue.clear()
            # Print table
        response = '```\n{}```'.format(table.get_string())
        await update.message.reply_text(response, parse_mode='Markdown')
        previous_command = 'show'



    except Exception as e:
        msg = await update.message.reply_text(f"Error while connecting to MySQL❌\n"
                                              f"Error: {e}")
        queue.append(msg)





# Connect
def connect_database(DB: str):

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database= DB
    )
    return db


# Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()
    print(filters.TEXT)
    numbers: str = processed.split(" ")
    if processed == 'e':
        return 'excel'
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
    if response == 'excel':
        chat_id = update.message.chat_id
        document = open('user.xlsx','rb')
        msg = await update.message.reply_text('Sending file...')
        queue.append(msg)
        await context.bot.send_document(chat_id,document)
        await context.bot.delete_message(chat_id=queue[0].chat_id, message_id=queue[0].message_id)
        queue.pop()
    else:
        print('Bot:', response)
        await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(BOT_TOKEN).build()

    start_handler= CommandHandler('start', start_command)
    help_handler= CommandHandler('help', help_command)
    custom_handler= CommandHandler('custom', custom_command)
    show_handler= CommandHandler('show', table_command)

    # Commands
    app.add_handler(start_handler)
    app.add_handler(help_handler)
    app.add_handler(custom_handler)
    app.add_handler(show_handler)

    # Messages
    app.add_handler(MessageHandler(filters.TEXT,handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print("Polling ...")
    app.run_polling(poll_interval=1)




