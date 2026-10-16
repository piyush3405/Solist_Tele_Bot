import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()

# --- MENU LAYOUT FUNCTIONS ---

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📦 Products", callback_data='menu_products')],
        [InlineKeyboardButton("📞 Support", callback_data='menu_support')],
        [InlineKeyboardButton("ℹ️ About Us", callback_data='menu_about')]
    ]
    return InlineKeyboardMarkup(keyboard)

def products_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("💻 Software", callback_data='prod_software')],
        [InlineKeyboardButton("📱 Mobile Apps", callback_data='prod_mobile')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button_keyboard():
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='menu_main')]]
    return InlineKeyboardMarkup(keyboard)


# --- COMMAND HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the Main Menu when user types /start."""
    await update.message.reply_text(
        "Welcome! Please select an option from the menu below:",
        reply_markup=main_menu_keyboard()
    )


# --- CALLBACK QUERY HANDLER (Menu Navigation) ---

async def handle_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge button click
    data = query.data

    # Main Menu Options
    if data == 'menu_main':
        await query.edit_message_text(
            "Welcome! Please select an option from the menu below:",
            reply_markup=main_menu_keyboard()
        )
    elif data == 'menu_products':
        await query.edit_message_text(
            "Select a product category:",
            reply_markup=products_menu_keyboard()
        )
    elif data == 'menu_support':
        await query.edit_message_text(
            "For assistance, email us at support@example.com or reach out on social media.",
            reply_markup=back_button_keyboard()
        )
    elif data == 'menu_about':
        await query.edit_message_text(
            "We are a leading tech team building automated Telegram solutions!",
            reply_markup=back_button_keyboard()
        )

    # Sub-Menu Product Options
    elif data == 'prod_software':
        await query.edit_message_text(
            "You selected: Software. We offer web, server, and automation software.",
            reply_markup=products_menu_keyboard()
        )
    elif data == 'prod_mobile':
        await query.edit_message_text(
            "You selected: Mobile Apps. We build iOS and Android apps.",
            reply_markup=products_menu_keyboard()
        )


# Register handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_menu_click))


# --- FLASK ROUTES ---

@app.route('/ping', methods=['GET'])
def ping():
    return "OK", 200

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(eval(json_str), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)