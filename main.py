import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()

# --- KEYBOARD LAYOUTS ---

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🏡 Plots (YEIDA / Gr. Noida)", callback_data='cat_plots')],
        [InlineKeyboardButton("🏢 Flats (Noida / Gr. Noida West)", callback_data='cat_flats')],
        [InlineKeyboardButton("🏰 Villas & Independent Homes", callback_data='cat_villas')],
        [InlineKeyboardButton("📞 Talk to Expert", callback_data='contact_expert')]
    ]
    return InlineKeyboardMarkup(keyboard)

def plots_sub_menu():
    keyboard = [
        [InlineKeyboardButton("📍 YEIDA Residential Plots", callback_data='plot_yeida_res')],
        [InlineKeyboardButton("🏭 YEIDA Industrial / Commercial", callback_data='plot_yeida_ind')],
        [InlineKeyboardButton("🌳 Greater Noida Authority Plots", callback_data='plot_grnoida')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def flats_sub_menu():
    keyboard = [
        [InlineKeyboardButton("🏢 2 BHK Apartments", callback_data='flat_2bhk')],
        [InlineKeyboardButton("🏢 3 BHK Apartments", callback_data='flat_3bhk')],
        [InlineKeyboardButton("🌟 Luxury 4+ BHK / Penthouse", callback_data='flat_luxury')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def villas_sub_menu():
    keyboard = [
        [InlineKeyboardButton("🏡 Gated Community Villas", callback_data='villa_gated')],
        [InlineKeyboardButton("🏰 Luxury Independent Villas", callback_data='villa_indep')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def budget_menu(property_type):
    keyboard = [
        [InlineKeyboardButton("💰 Under ₹50 Lakhs", callback_data=f'budget_low_{property_type}')],
        [InlineKeyboardButton("💰 ₹50 Lakhs - ₹1 Crore", callback_data=f'budget_mid_{property_type}')],
        [InlineKeyboardButton("💰 ₹1 Crore - ₹2 Crores", callback_data=f'budget_high_{property_type}')],
        [InlineKeyboardButton("💰 ₹2 Crores+", callback_data=f'budget_luxury_{property_type}')],
        [InlineKeyboardButton("🔙 Back", callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def final_action_keyboard():
    keyboard = [
        [InlineKeyboardButton("📋 Get Detailed PDF Brochure", callback_data='action_brochure')],
        [InlineKeyboardButton("📞 Request Callback from Agent", callback_data='action_callback')],
        [InlineKeyboardButton("🔄 Start Over", callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)


# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🌟 **Welcome to Noida & Greater Noida Real Estate Bot!** 🌟\n\n"
        "Find your dream property across Yamuna Expressway (YEIDA), Noida, and Greater Noida.\n\n"
        "Please select a property category below to get started:"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Main Navigation
    if data == 'menu_main':
        await query.edit_message_text(
            "🌟 **Main Menu:** Select a property category below:",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
    
    # Category Selection
    elif data == 'cat_plots':
        await query.edit_message_text(
            "📍 **Plots Selection:** Choose a specific location or authority type:",
            reply_markup=plots_sub_menu(),
            parse_mode="Markdown"
        )
    elif data == 'cat_flats':
        await query.edit_message_text(
            "🏢 **Flats Selection:** Choose your preferred apartment configuration:",
            reply_markup=flats_sub_menu(),
            parse_mode="Markdown"
        )
    elif data == 'cat_villas':
        await query.edit_message_text(
            "🏰 **Villas Selection:** Choose your style:",
            reply_markup=villas_sub_menu(),
            parse_mode="Markdown"
        )
    elif data == 'contact_expert':
        await query.edit_message_text(
            "📞 **Direct Expert Support**\n\nCall our Noida property desk at: **+91-12345678900** or email support@noidarealestate.com",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data='menu_main')]]),
            parse_mode="Markdown"
        )

    # Sub-category selections leading to budget filtering
    elif data.startswith('plot_') or data.startswith('flat_') or data.startswith('villa_'):
        await query.edit_message_text(
            "💵 **Select your estimated budget range:**",
            reply_markup=budget_menu(data),
            parse_mode="Markdown"
        )

    # Budget selection leading to final options
    elif data.startswith('budget_'):
        await query.edit_message_text(
            "✅ **Great choice!** We have multiple verified options matching your criteria in Noida & Greater Noida.\n\n"
            "What would you like to do next?",
            reply_markup=final_action_keyboard(),
            parse_mode="Markdown"
        )

    # Final actions
    elif data == 'action_brochure':
        await query.edit_message_text(
            "📥 Your brochure request has been registered! Our team will send the price sheets & PDF catalog to your chat shortly.\n\nType /start to explore more.",
            parse_mode="Markdown"
        )
    elif data == 'action_callback':
        await query.edit_message_text(
            "📞 Request received! One of our senior property consultants will call you within 15 minutes.\n\nType /start to restart.",
            parse_mode="Markdown"
        )

# Register Handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_callback))

# --- FLASK ROUTES ---

@app.route('/ping', methods=['GET'])
def ping():
    return "OK", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_data = request.get_json(force=True)
    if json_data:
        async def process():
            await telegram_app.initialize()
            update = Update.de_json(json_data, telegram_app.bot)
            async with telegram_app:
                await telegram_app.process_update(update)
        
        asyncio.run(process())
    return "OK", 200

@app.route('/', methods=['GET'])
def home():
    return "Noida Real Estate Bot is running successfully!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
