import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

# Initialize application globally
telegram_app = Application.builder().token(TOKEN).build()

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📦 Products", callback_data='menu_products')],
        [InlineKeyboardButton("📞 Support", callback_data='menu_support')],
        [InlineKeyboardButton("ℹ️ About Us", callback_data='menu_about')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Please select an option from the menu below:",
        reply_markup=main_menu_keyboard()
    )

async def handle_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'menu_products':
        await query.edit_message_text("Here is our product catalogue...")
    elif data == 'menu_support':
        await query.edit_message_text("Contact support at support@example.com")
    elif data == 'menu_about':
        await query.edit_message_text("We build automated bots!")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_menu_click))

# Flag to check if application is initialized
is_initialized = False

async def initialize_bot():
    global is_initialized
    if not is_initialized:
        await telegram_app.initialize()
        is_initialized = True

@app.route('/ping', methods=['GET'])
def ping():
    return "OK", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_data = request.get_json(force=True)
    if json_data:
        async def process():
            await initialize_bot()
            update = Update.de_json(json_data, telegram_app.bot)
            async with telegram_app:
                await telegram_app.process_update(update)
        
        # Run the async process loop inside Flask sync route
        asyncio.run(process())
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
