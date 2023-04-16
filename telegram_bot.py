import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import  ContextTypes, CommandHandler , MessageHandler  , ApplicationBuilder, filters
from conf import users
from subprocess import call
from gpt_message_handler import handle_response
import sqlalchemy as db
import io

print('Starting up bot...')

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
BOTNAME = os.getenv('BOTNAME')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Create a decorator that takes users as an argument and if the user is in the list, it will run the function
def user_allowed(users):
    def decorator(func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.message.from_user
            logging.info(f'User {user.username} is trying to access the bot. id: {user.id}, message: {update.message.text}')
            if user.username in users:
                await func(update, context)
            else:
                await update.message.reply_text('You are not allowed to use this command')
        return wrapper
    return decorator

# Lets us use the /start command
@user_allowed(users)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! I\'m a bot. What\'s up?')


# Lets us use the /help command
@user_allowed(users)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Try typing anything and I will do my best to respond!')


# Lets us use the /custom command
@user_allowed(users)
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command, you can add whatever text you want here.')

# Lets us use the /restart
@user_allowed(users)
async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # delete the db.sqlite3 file
    engine = db.create_engine("sqlite:///db.sqlite3")
    connection = engine.connect()
    metadata = db.MetaData()

    try: 
        conversations = db.Table('conversations', metadata, autoload=True, autoload_with=engine)
    except:
        conversations = db.Table('conversations', 
                                metadata, 
                                db.Column('id', db.Integer, primary_key=True), 
                                db.Column('user_id', db.Integer), 
                                db.Column('user_name', db.String), 
                                db.Column('user_message', db.String), 
                                db.Column('message_id', db.Integer),
                                db.Column('bot_response', db.String), 
                                db.Column('created_at', db.DateTime, default=datetime.now))

        metadata.create_all(engine)
    # delete all rows
    query = db.delete(conversations)
    ResultProxy = connection.execute(query)
    print('Deleted all rows from conversations table')
    await update.message.reply_text('Restarted the bot.')


@user_allowed(users)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('Message received')
    # Get basic info of the incoming message
    message_type = update.message.chat.type
    text = str(update.message.text).lower()
    user = update.message.from_user
    message_id = update.message.message_id
    response = ''

    # Print a log for debugging
    print(f'User ({update.message.chat.id}) says: "{text}" in: {message_type}')

    if text.startswith(BOTNAME):
        response = handle_response(text, user, message_id)

    # Reply normal if the message is in private
    await update.message.reply_text(response)


# Log errors
@user_allowed(users)
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Run the program
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Commands
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('custom', custom_command))
    application.add_handler(CommandHandler('restart', restart_command))

    # Messages
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    # Log all errors
    application.add_error_handler(error)
    application.run_polling()

    