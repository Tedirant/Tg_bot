import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ============================
# НАСТРОЙКИ — МЕНЯЙ ТУТ
# ============================
BOT_TOKEN = "8599455451:AAHu-b9eZwIjX089JyTZmaFW9cPE83RCla0"  # Вставь токен от @BotFather

# Оскорбительные фразы — добавляй свои!
PHRASES = [
    "— сказала шлюха",
    "— изрёк долбоеб",
    "— промямлил петух",
    "— прокричал дебил",
    "— пробормотало уебище",
    "— заявил хуесос",
    "— написал пидор",
    "— выдал клоун",
    "— сообщил олень попуск",
    "— высрал дегенерат",
    "— напечатал хуеглот",
]

# ============================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    user = message.from_user
    if not user or user.is_bot:
        return

    # Игнорируем тебя
    if user.username and 
    user.username.lower() == "turboos".lower() or
    user.username.lower() == "Ssssszx4".lower() or
    user.username.lower() == "tedirant".lower() or
    user.username.lower() == "dsgsfg1":
        return

    phrase = random.choice(PHRASES)
    await message.reply_text(phrase)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("Бот запущен! Нажми Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
