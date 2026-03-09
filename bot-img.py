#!/usr/bin/env python3
"""
Telegram бот с генерацией изображений через Grok (xAI Aurora)
Команды:
  /start   — приветствие
  /help    — помощь
  /image <описание> — сгенерировать картинку
"""

import os
import logging
import asyncio
import base64
import httpx
from io import BytesIO

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ──────────────────────────────────────────────
# НАСТРОЙКИ — замени на свои ключи!
# ──────────────────────────────────────────────
TELEGRAM_TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"   # от @BotFather
XAI_API_KEY    = "ВАШ_XAI_API_KEY"          # от https://console.x.ai

# Модель генерации изображений xAI
IMAGE_MODEL = "aurora"   # aurora — флагманская модель Grok для изображений

# ──────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Привет! Я генерирую картинки с помощью Grok Aurora.\n\n"
        "Используй команду:\n"
        "  /image <описание> — создать изображение\n\n"
        "Например:\n"
        "  /image кот в скафандре на Марсе"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📖 Справка:\n\n"
        "/image <описание> — сгенерировать изображение по тексту\n"
        "/start — главное меню\n\n"
        "Описание может быть на русском или английском языке.\n"
        "Пример: /image закат над горами в стиле аниме"
    )


async def cmd_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Генерация изображения через xAI Aurora API."""
    # Получаем промпт из аргументов команды
    prompt = " ".join(context.args).strip() if context.args else ""

    if not prompt:
        await update.message.reply_text(
            "⚠️ Укажи описание после команды.\n"
            "Пример: /image котёнок в шляпе волшебника"
        )
        return

    # Сообщаем пользователю, что начали генерацию
    status_msg = await update.message.reply_text(
        f"🎨 Генерирую изображение по запросу:\n«{prompt}»\n\nПодожди несколько секунд..."
    )

    try:
        image_bytes = await generate_image_xai(prompt)

        # Отправляем фото в чат
        await update.message.reply_photo(
            photo=BytesIO(image_bytes),
            caption=f"✨ Готово!\nЗапрос: {prompt}",
        )
        # Удаляем статусное сообщение
        await status_msg.delete()

    except ValueError as e:
        logger.error("Ошибка генерации: %s", e)
        await status_msg.edit_text(f"❌ Ошибка: {e}")
    except Exception as e:
        logger.exception("Неожиданная ошибка: %s", e)
        await status_msg.edit_text(
            "❌ Что-то пошло не так. Попробуй ещё раз позже."
        )


async def generate_image_xai(prompt: str) -> bytes:
    """
    Вызывает xAI Images API и возвращает байты PNG/JPEG.
    Документация: https://docs.x.ai/docs/guides/image-generation
    """
    url = "https://api.x.ai/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",   # получаем base64
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        error_text = response.text[:300]
        raise ValueError(f"xAI API вернул {response.status_code}: {error_text}")

    data = response.json()

    try:
        b64_data = data["data"][0]["b64_json"]
        return base64.b64decode(b64_data)
    except (KeyError, IndexError) as e:
        raise ValueError(f"Неожиданный формат ответа xAI: {e}\n{data}") from e


def main() -> None:
    if TELEGRAM_TOKEN == "ВАШ_TELEGRAM_BOT_TOKEN":
        print("❗ Укажи TELEGRAM_TOKEN в коде или переменной окружения!")
        return
    if XAI_API_KEY == "ВАШ_XAI_API_KEY":
        print("❗ Укажи XAI_API_KEY в коде или переменной окружения!")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_help))
    app.add_handler(CommandHandler("image", cmd_image))

    logger.info("Бот запущен. Нажми Ctrl+C для остановки.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()