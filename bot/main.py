import os
import sys
import logging
import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.filters import CommandStart

from dotenv import load_dotenv

# Добавляем путь, чтобы импорты работали
sys.path.append(os.path.dirname(__file__))

# ——— Загрузка переменных окружения ———
load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not API_TOKEN or not ADMIN_CHAT_ID:
    raise RuntimeError("Не заданы BOT_TOKEN или ADMIN_CHAT_ID в .env файле")

try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
except ValueError:
    raise RuntimeError("ADMIN_CHAT_ID должен быть числом")

# ——— Логирование ———
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# ——— Инициализация ———
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ——— FSM: заказ услуги ———
class OrderForm(StatesGroup):
    name = State()
    niche = State()
    task = State()


# ——— Клавиатура ———
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Услуги"), KeyboardButton(text="💼 Примеры работ")],
            [KeyboardButton(text="💬 Заказать")]
        ],
        resize_keyboard=True
    )


# ——— Пример функции get_sheet() ———
def get_sheet():
    """
    Здесь должна быть ваша функция подключения к Google Sheets.
    Для примера возвращается объект с методом append_row.
    """
    class DummySheet:
        def append_row(self, row):
            logger.info(f"Данные добавлены в таблицу: {row}")
    return DummySheet()
    # Замените на вашу реальную реализацию!


# ——— Хендлер /start ———
@dp.message(lambda msg: msg.text == "/start")
async def start(message: Message):
    await message.answer(
        "Привет! Бот запущен и готов к работе ✅",
        reply_markup=get_main_menu()
    )


# ——— FSM: Заказ ———
@dp.message(lambda msg: msg.text == "💬 Заказать")
async def start_order(message: Message, state: FSMContext):
    await state.set_state(OrderForm.name)
    await message.answer("Как тебя зовут?")


@dp.message(OrderForm.name)
async def process_name(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer("Пожалуйста, введите имя.")
        return
    await state.update_data(name=text)
    await state.set_state(OrderForm.niche)
    await message.answer("Из какой ты ниши?")


@dp.message(OrderForm.niche)
async def process_niche(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer("Пожалуйста, укажите нишу.")
        return
    await state.update_data(niche=text)
    await state.set_state(OrderForm.task)
    await message.answer("Опиши задачу, с которой тебе нужна помощь.")


@dp.message(OrderForm.task)
async def process_task(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name', '—')
    niche = data.get('niche', '—')
    task = message.text.strip()
    if not task:
        await message.answer("Пожалуйста, опишите задачу.")
        return

    user_id = message.from_user.id
    username = message.from_user.username or "—"
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        sheet = get_sheet()
        if sheet:
            sheet.append_row([date, name, niche, task, user_id, username])
            logger.info(f"✅ Заявка сохранена для @{username}")
        else:
            raise Exception("Не удалось инициализировать Google Sheet")
    except Exception as e:
        logger.error(f"❌ Ошибка записи в таблицу: {e}")
        await message.answer("⚠️ Не удалось сохранить заявку. Попробуй позже.")
        await bot.send_message(ADMIN_CHAT_ID, f"❌ Ошибка записи в Google Таблицу:\n{e}")
        await state.clear()
        return

    await bot.send_message(
        ADMIN_CHAT_ID,
        f"📩 Новая заявка!\n\n"
        f"👤 Имя: {name}\n"
        f"📌 Ниша: {niche}\n"
        f"📝 Задача: {task}\n"
        f"🆔 ID: {user_id}\n"
        f"👤 @{username}\n"
        f"📅 {date}"
    )

    await message.answer("Спасибо, заявка принята ✅\nЯ свяжусь с тобой в ближайшее время.")
    await state.clear()


# ——— Примеры работ ———
@dp.message(lambda msg: msg.text == "💼 Примеры работ")
async def show_portfolio(message: Message):
    await message.answer(
        "💼 Примеры работ:\n\n"
        "📄 [Смотреть портфолио](https://docs.google.com/document/d/1m0ydVEODPfvMTqCXtWvBSlp_jXZNX600xf3IgApGPVk)\n\n" 
        "📦 Карточка товара:\n"
        "«Это не просто куртка — это броня на зиму»\n\n"
        "👟 Описание кроссовок:\n"
        "«Амортизация, подошва и память стельки — комфорт на весь день»",
        parse_mode="Markdown"
    )


# ——— Услуги ———
@dp.message(lambda msg: msg.text == "📋 Услуги")
async def show_services(message: Message):
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


# ——— Точка входа для Vercel ———
async def main(event, context):
    update = Update.model_validate_json(event["body"], context={"bot": bot})
    await dp.propagate_event(bot=bot, update=update)
    return {"statusCode": 200, "body": "OK"}