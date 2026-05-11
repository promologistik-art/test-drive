aiogram==3.3.0
python-dotenv==1.0.0import asyncio
import logging
import os
import re

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from dotenv import load_dotenv

load_dotenv()

# --- Конфигурация ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена. Убедитесь, что она есть в файле .env")

# --- Инициализация ---
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# --- Состояния ---
class UserFlow(StatesGroup):
    waiting_for_phone = State()

# --- Клавиатуры ---
def get_block1_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Идем дальше🔥", callback_data="to_block2")]
        ]
    )

def get_block2_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Идем дальше🔥", callback_data="to_block3")]
        ]
    )

def get_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Поделиться номером 📞", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

# --- Обработчики команд ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    block1_text = (
        "Привет! Это первый блок, созданный мной в конструкторе воронок Sale Bot. "
        "Дальше будет еще интересней! Нажимай на кнопку ниже!"
    )
    await message.answer(block1_text, reply_markup=get_block1_keyboard())

# --- Callback handlers ---
@dp.callback_query(F.data == "to_block2")
async def process_block2(callback: types.CallbackQuery):
    block2_text = (
        "Приветствую вас, дорогие друзья! 🌟\n\n"
        "Мы подошли ко второму блоку, и я с радостью расскажу немного о себе. "
        "Меня зовут Евгений, я решил(а) пройти тест-драйв профессии "
        "“технический специалист” от Влада Пурвиньша и сделать шаг навстречу новым возможностям!\n\n"
        "Сейчас я создаю своего первого чат-бота, и это невероятно увлекательно! 🤖\n\n"
        "Давайте вместе исследовать этот путь и открывать новые горизонты! "
        "Спасибо, что вы со мной! 🌈"
    )
    await callback.message.answer(block2_text, reply_markup=get_block2_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "to_block3")
async def process_block3(callback: types.CallbackQuery, state: FSMContext):
    block3_text = (
        "Мы подошли к очень интересному блоку, где у нас есть возможность "
        "запросить у вас важную информацию. В этот раз мы будем запрашивать ваш номер телефона. 📞\n\n"
        "Обратите внимание: если номер будет введен неверно, вы не сможете продолжить!\n\n"
        "Попробуйте! Введите свой номер ниже или нажмите на кнопку, чтобы продолжить. 🚀"
    )
    await callback.message.answer(block3_text, reply_markup=get_phone_keyboard())
    await state.set_state(UserFlow.waiting_for_phone)
    await callback.answer()

# --- Обработка номера телефона ---
@dp.message(UserFlow.waiting_for_phone, F.contact)
async def process_contact(message: Message, state: FSMContext):
    # Получаем номер из контакта
    phone = message.contact.phone_number
    await proceed_to_block5(message, state, phone)

@dp.message(UserFlow.waiting_for_phone, F.text)
async def process_text_phone(message: Message, state: FSMContext):
    # Проверяем текст на корректность номера
    phone = message.text.strip()
    # Простая регулярка для проверки (российские и международные форматы)
    pattern = r'^(\+?\d{1,3})?[\s\-\(\)]*?\d{3}[\s\-\(\)]*?\d{3}[\s\-\(\)]*?\d{2}[\s\-\(\)]*?\d{2}$'
    if re.match(pattern, phone):
        await proceed_to_block5(message, state, phone)
    else:
        # Блок 4: Ошибка
        error_text = (
            "❌ Ошибка\n\n"
            "Нужно ввести корректный номер телефона!"
        )
        # Показываем ошибку и оставляем клавиатуру
        await message.answer(error_text, reply_markup=get_phone_keyboard())

async def proceed_to_block5(message: Message, state: FSMContext, phone: str):
    await state.clear()
    
    # Убираем клавиатуру
    await message.answer(f"Спасибо! Ваш номер {phone} принят.", reply_markup=ReplyKeyboardRemove())
    
    block5_text = (
        "Мы подошли к четвертому блоку моего первого чат-бота! "
        "Если вы здесь, значит, вы успешно оставили свой номер телефона. 🎉\n\n"
        "Знаете ли вы, что мы можем переходить от сообщения к сообщению "
        "не только по нажатию на кнопки?\n\n"
        "Мы можем установить таймер, и вам придет сообщение через определенное время! ⏳\n\n"
        "Как, например, сейчас: через 1 минуту вы получите мое финальное сообщение, "
        "в котором будет небольшой бонус для вас! 🎁\n\n"
        "Спасибо, что вы со мной на этом увлекательном пути! 🚀"
    )
    await message.answer(block5_text)
    
    # Запускаем таймер на 1 минуту
    await asyncio.sleep(60)
    
    # Блок 6: Финальное сообщение с файлом
    block6_text = (
        "Вот мы и подошли к финалу! 🎉 В приложении вы найдете файл, "
        "который поможет вам найти своего первого клиента на фрилансе.\n\n"
        "Знаете ли вы, что бот, который вы только что собрали, "
        "на рынке стоит от 3 до 5 тысяч рублей? 💰\n\n"
        "И это только начало! Если вы успешно освоите эту профессию, "
        "ваши первые 100 тысяч в месяц не за горами! 🚀\n\n"
        "Желаю вам удачи и больших успехов на вашем фриланс-пути! 🌟"
    )
    
    # Отправляем сообщение с ссылкой на Google Drive
    await message.answer(
        f"{block6_text}\n\n"
        "https://drive.google.com/file/d/1Ig92rtNwv4tcvFRaRLwMTcGnZFpkdi0J/view"
    )

# --- Запуск ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())