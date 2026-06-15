import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode

TOKEN = os.environ.get("BOT_TOKEN")
app = Application.builder().token(TOKEN).build()

# Клавиатура выбора языка
def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇰🇿 Қазақша", callback_data="lang_kz"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ])

# Клавиатура выбора роли
def role_keyboard(lang):
    texts = {"kz": "🚖 Жолаушы", "ru": "🚖 Пассажир", "en": "🚖 Passenger"}
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(texts[lang], callback_data="role_passenger")],
        [InlineKeyboardButton("🚙 Жүргізуші / Водитель / Driver", callback_data="role_driver")]
    ])

async def start(update, context):
    await update.message.reply_text(
        "Қош келдіңіз! / Добро пожаловать! / Welcome!\n\nТіл таңдаңыз / Выберите язык",
        reply_markup=lang_keyboard()
    )

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data["lang"] = lang
        await query.edit_message_text(
            "Кімсіз? / Кто вы? / Who are you?",
            reply_markup=role_keyboard(lang)
        )
    elif data == "role_passenger":
        # Ссылка на мини-приложение (замените позже на ваш vercel URL)
        webapp_url = "https://taxi-bot.vercel.app/static/index.html"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚕 Заказать такси", web_app=WebAppInfo(url=webapp_url))]
        ])
        await query.edit_message_text(
            "Нажмите кнопку, чтобы заказать такси",
            reply_markup=keyboard
        )
    elif data == "role_driver":
        await query.edit_message_text(
            "🚖 Режим водителя\n\nКогда будете готовы выезжать, нажмите:\n/online",
            reply_markup=None
        )

async def online(update, context):
    await update.message.reply_text("✅ Вы на линии! Скоро поступят заказы.")

# Регистрируем команды
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("online", online))
app.add_handler(CallbackQueryHandler(button_handler))

async def webhook(request):
    if request.method == "POST":
        body = await request.body()
        update = Update.de_json(json.loads(body), app.bot)
        await app.process_update(update)
        return {"statusCode": 200, "body": "OK"}
    return {"statusCode": 405}