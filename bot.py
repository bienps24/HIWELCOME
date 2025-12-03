import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ChatMemberHandler, CallbackContext
from PIL import Image
from io import BytesIO
import requests

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the bot token from environment variable (from Railway)
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Railway environment variable

if not API_TOKEN:
    logger.error("API token not set in environment variables.")
    exit()

# Welcome message photo URL and description
photo_url = 'https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjA2gi9S_9kEpC9t-8Kow2ejr4BYNjl_9oHImh0XfJjVHLVFdaLXC4hasJBNMMOA0PNPtueA74L3QmR9juiot-AdrwmByNFt3fa1dVl0UcERv8i1f5g7QfmpOyL1y4wxxL4Xup7db5NsmB9Gsx2kaOx7GjpVd_CzrJ6CD7MdiZVps5zDVLn91WFuSANmEc/s1600/photo_2025-11-03_15-41-22.jpg'
description = "Hoyyy tara sali kaaaa {username}! @aikee17 etong @aikee17 ay may naka embeb na link na https://t.me/c/3364299216/10 , SA BABA IS BUTTONS 𝗦𝗵𝗮𝗿𝗲 • 𝟬/𝟮 - https://t.me/share/url?url=%20tara%20guys%20sali%20kayo%20𝙡𝙞𝙗𝙧𝙚%20𝙗𝙤𝙨𝙤%20at%20ᴀᴛᴀʙꜱ!%20https://t.me/joinchat/zZwEq6I2voY2MWVl"

# Send the welcome message
def send_welcome_message(update: Update, context: CallbackContext):
    # Get the new user's name
    user = update.message.new_chat_members[0]
    username = user.username if user.username else user.first_name
    
    # Build the welcome message
    welcome_text = description.format(username=username)

    # Use Pillow to open the image from URL
    response = requests.get(photo_url)
    img = Image.open(BytesIO(response.content))
    
    # Send the photo and message with inline buttons
    keyboard = [
        [InlineKeyboardButton("Share", url="https://t.me/share/url?url=%20tara%20guys%20sali%20kayo%20𝙡𝙞𝙗𝙧𝙚%20𝙗𝙤𝙨𝙤%20at%20ᴀᴛᴀʙꜱ!%20https://t.me/joinchat/zZwEq6I2voY2MWVl"),
         InlineKeyboardButton("Unlock Videos", callback_data='unlock_videos')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Convert Pillow image to binary data
    byte_io = BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)

    # Send the photo with message
    message = update.message.reply_photo(photo=byte_io, caption=welcome_text, reply_markup=reply_markup)

    # Store the message ID to delete it later
    context.chat_data['last_welcome_message'] = message.message_id

# Delete the old welcome message and send a new one if a new user joins
def handle_new_member(update: Update, context: CallbackContext):
    # Delete the old welcome message
    if 'last_welcome_message' in context.chat_data:
        context.bot.delete_message(chat_id=update.message.chat_id,
                                   message_id=context.chat_data['last_welcome_message'])
    
    # Send the new welcome message
    send_welcome_message(update, context)

# Handle button presses (like unlock videos)
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'unlock_videos':
        query.edit_message_text(text="Share 3 times to unlock videos!")

# Main function to start the bot
def main():
    # Make sure the API token is loaded from environment variable
    if API_TOKEN is None:
        print("Bot token not set in environment variables!")
        return

    # Create the Updater and pass in your bot's API token
    updater = Updater(API_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, send_welcome_message))

    dp.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.MY_CHAT_MEMBER))

    # Handler for button presses
    dp.add_handler(CallbackQueryHandler(button))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
