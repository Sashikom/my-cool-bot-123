# bot/main.py
import datetime
import logging
import os
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
from sheets import get_sheet  # обновлённая версия sheets.py

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# ——— Логирование ———
logging.basicConfig(level=logging.INFO)

# ——— Инициализация бота ———
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ——— FSM: заказ услуги ———
class OrderForm(StatesGroup):
    name = State()
    niche = State()
    task = State()

# ——— Клавиатура ———
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("📋 Услуги"), KeyboardButton("💼 Примеры работ"))
menu.add(KeyboardButton("💬 Заказать"))

# ——— Старт ———
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет, Александр! Бот запущен и готов к работе ✅", reply_markup=menu)

# ——— FSM: Заказ ———
@dp.message_handler(lambda msg: msg.text == "💬 Заказать")
async def start_order(message: types.Message):
    await OrderForm.name.set()
    await message.answer("Как тебя зовут?")

@dp.message_handler(state=OrderForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await OrderForm.next()
    await message.answer("Из какой ты ниши?")

@dp.message_handler(state=OrderForm.niche)
async def process_niche(message: types.Message, state: FSMContext):
    await state.update_data(niche=message.text)
    await OrderForm.next()
    await message.answer("Опиши задачу, с которой тебе нужна помощь")

@dp.message_handler(state=OrderForm.task)
async def process_task(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data['name']
    niche = data['niche']
    task = message.text
    user_id = message.from_user.id
    username = message.from_user.username or "—"
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        get_sheet().append_row([date, name, niche, task, user_id, username])
        logging.info(f"✅ Заявка сохранена для @{username}")
    except Exception as e:
        logging.error(f"❌ Ошибка записи в таблицу: {e}")
        await message.answer("⚠️ Не удалось сохранить заявку. Попробуй позже.")
        await bot.send_message(ADMIN_CHAT_ID, f"❌ Ошибка записи в Google Таблицу:\n{e}")
        await state.finish()
        return

    await bot.send_message(
        ADMIN_CHAT_ID,
        f"📩 Новая заявка!\n\n👤 Имя: {name}\n📌 Ниша: {niche}\n📝 Задача: {task}\n"
        f"🆔 ID: {user_id}\n👤 @{username}\n📅 {date}"
    )

    await message.answer("Спасибо, заявка принята ✅\nЯ свяжусь с тобой в ближайшее время.")
    await state.finish()

# ——— Хендлер: Примеры работ ———
@dp.message_handler(lambda msg: msg.text == "💼 Примеры работ")
async def show_portfolio(message: types.Message):
    await message.answer(
        "💼 Примеры работ:\n\n"
        "📄 [Смотреть портфолио](https://docs.google.com/document/d/1m0ydVEODPfvMTqCXtWvBSlp_jXZNX600xf3IgApGPVk)\n\n"
        "📦 Карточка товара:\n"
        "«Это не просто куртка — это броня на зиму»\n\n"
        "👟 Описание кроссовок:\n"
        "«Амортизация, подошва и память стельки — комфорт на весь день»",
        parse_mode="Markdown"
    )

# ——— Хендлер: Услуги ———
@dp.message_handler(lambda msg: msg.text == "📋 Услуги")
async def show_services(message: types.Message):
    await message.answer(
        "📋 Услуги:\n\n"
        "✍ Помогаю словами решать задачи:\n"
        "• Тексты для Telegram, прогревы\n"
        "• Продающие карточки Ozon / WB\n"
        "• Скрипты под видео / лендинги\n"
        "• Редактура, упаковка, генерация промтов\n\n"
        "🕐 Сроки — от 1 дня\n"
        "💰 Стоимость — от 1 000 ₽\n\n"
        "Нажмите «💬 Заказать» — и обсудим вашу задачу.",
        parse_mode="Markdown"
    )

# ——— Запуск ———
if __name__ == "__main__":
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling()

    asyncio.run(main())
