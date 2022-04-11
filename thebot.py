from telegram import CallbackQuery, Update, Voice
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import configparser
import os
import logging
import redis
import telegram
import telegram.ext
import pymysql
from pymysql import connect
import datetime

global film


def main():

    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
  

    sharingDOC_handler = MessageHandler(Filters.text & (~Filters.command), sharingDOC)
    dispatcher.add_handler(sharingDOC_handler)
    sharingVID_handler = MessageHandler(telegram.ext.Filters.video & (~Filters.command), sharingVID)
    dispatcher.add_handler(sharingVID_handler)
    sharingVoice_handler = MessageHandler(telegram.ext.Filters.voice & (~Filters.command), sharingVoice)
    dispatcher.add_handler(sharingVoice_handler)
    sharingPic_handler = MessageHandler(telegram.ext.Filters.photo & (~Filters.command), sharingPic)
    dispatcher.add_handler(sharingPic_handler)


    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("comment", comment))  #choose the film to operate(write or review)
    dispatcher.add_handler(CommandHandler("write", write))   #write comments
    dispatcher.add_handler(CommandHandler("review", review))  #review comments
    

    # To start the bot:
    updater.start_polling()
    print('Started')
    updater.idle()
    print('Stopping...')





# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def sharingDOC(update, context):
    config = configparser.ConfigParser()
    config.read('config.ini')
    reply_message = update.message.text
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=config['TELEGRAM']['Publish_Channel_ID'],
                             text=reply_message)
    update.message.reply_text('Thank you for sharing')

def sharingVID(update, context):
    config = configparser.ConfigParser()
    config.read('config.ini')
    message = update.message
    context.bot.send_video(chat_id=config['TELEGRAM']['Publish_Channel_ID'],
                             video=message.video, caption=message.caption)
    update.message.reply_text('Thank you for sharing')

def sharingVoice(update, context):
    config = configparser.ConfigParser()
    config.read('config.ini')
    message = update.message
    context.bot.send_voice(chat_id=config['TELEGRAM']['Publish_Channel_ID'],
                             voice=message.voice, caption=message.caption)
    update.message.reply_text('Thank you for sharing')

def sharingPic(update, context):
    config = configparser.ConfigParser()
    config.read('config.ini')
    message = update.message
    context.bot.send_photo(chat_id=config['TELEGRAM']['Publish_Channel_ID'],
                             photo=message.photo[0], caption=message.caption)
    update.message.reply_text('Thank you for sharing')

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('E-mail Mike via wysy19982015@outlook.com')

def start_command(update: Update, context: CallbackContext) -> None:
    """Start you will get a link for pub channel"""
    update.message.reply_text('Please add Channel https://t.me/Nur0Channel for more function')



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
    for temp in data:
        print(temp)
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
