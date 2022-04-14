from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext,CallbackQueryHandler


import configparser
import logging
import redis
import pymysql
import datetime

global redis1
global film


def main():
    # Load your token and create an Updater for your Bot

    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']),
                         port=(config['REDIS']['REDISPORT']))

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)


    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("comment", comment))  #choose the film to operate(write or review)
    dispatcher.add_handler(CommandHandler("write", write))   #write comments
    dispatcher.add_handler(CommandHandler("review", review))  #review comments

    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)



# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]  # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

# insert comment information to the database
def insert(w_username,w_id,w_comments,w_film):
    # Open database connection
    db = pymysql.connect(host="mariadb4bot.mariadb.database.azure.com", port=3306, user="dbuser@mariadb4bot",
                         password="Wy@190450", database="ccbot98")
    # Use the cursor() method to create a cursor object cursor
    cursor = db.cursor()
    # Execute SQL query using execute() method
    cursor.execute("SELECT VERSION()")

    query="insert into comments(user_name,user_id,comment,film) " \
          "values(%s,%s,%s,%s)"
    values=(w_username,w_id,w_comments,w_film)
    cursor.execute(query,values)

    # close database
    cursor.close()
    db.commit()
    db.close()

# Output all comments for the specified movie name
def read(filmname):
    # Open database connection
    db = pymysql.connect(host="mariadb4bot.mariadb.database.azure.com", port=3306, user="dbuser@mariadb4bot",
                         password="Wy@190450", database="ccbot98")
    # Use the cursor() method to create a cursor object cursor
    cursor = db.cursor()
    # Execute SQL query using execute() method
    cursor.execute('SELECT VERSION()')

    cursor.execute('SELECT * FROM comments \
           WHERE film= "%s" order by date asc' % (filmname))
    data = cursor.fetchall()
    # close database
    cursor.close()
    db.commit()
    db.close()
    return data

# specify movie name
def comment(update: Update, context: CallbackContext) -> None:
    try:
        global film
        reply_message = update.message.text
        new_message = reply_message.replace('/comment ', '')
        if new_message == '/comment':  # If no movie name is entered, prompt the user
            update.message.reply_text(
                'You have not entered a film name, please enter the command in format :/comment <film>')
        else:
            film=new_message
            update.message.reply_text('Already entered the comment area of movie "'+ film +'", Please use /write or /review to write or read comments')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /comment <keyword>')

# User enters comment
def write(update,context):
    try:
        global film
        filmname=film
        reply_message = update.message.text
        new_message=reply_message.replace('/write ','')
        name=update.message.from_user.first_name
        id=update.message.from_user.id
        if new_message == '/write':  # If no comment is written, prompt the user
            update.message.reply_text('You have not entered a comment, please enter a comment in format :/write <comment>')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Comment successful!')
            insert(name,id,new_message,filmname)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /write <comment>')

# User query comments
def review(update,context):
    try:
        global film
        filmname=film
        data=read(filmname)
        if len(data)==0:  # If the database has no relevant movie reviews, prompt the user
            context.bot.send_message(chat_id=update.effective_chat.id, text='There is no comment, you can use /write to add your comment.')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='OK, here are all the reviews for movie '+filmname)
            for a, b, c, d, e in data:
                result=c.strftime("%Y-%m-%d %H:%M:%S")+' '+a+': '+d
                context.bot.send_message(chat_id=update.effective_chat.id, text=result)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /review')

if __name__ == '__main__':
    main()