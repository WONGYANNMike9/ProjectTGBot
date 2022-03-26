from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


import configparser
import os
import logging
import redis
import telegram
import telegram.ext

global redis1

def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    #updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)   
    dispatcher = updater.dispatcher


    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=(config['REDIS']['REDISPORT']))

    #global redis1
    #redis1 = redis.Redis(host=(os.environ['HOST']), password=(os.environ['PASSWORD']), port=(os.environ['REDISPORT']))
    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
  
    
    sharingDOC_handler = MessageHandler(Filters.text & (~Filters.command), sharingDOC)
    dispatcher.add_handler(sharingDOC_handler)
    #sharingVID_handler = MessageHandler(Filters.text & (~Filters.command), sharingVID)
    #dispatcher.add_handler(sharingVID_handler)



    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    #dispatcher.add_handler(CommandHandler("what", reply_instruction))
    #dispatcher.add_handler(CommandHandler("view", view_review))
    dispatcher.add_handler(CommandHandler("help", help_command))
   
    

    # To start the bot:
    updater.start_polling()
    updater.idle()





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


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('E-mail Mike via wysy19982015@outlook.com')




def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try: 
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg +  ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')



if __name__ == '__main__':
    main()
