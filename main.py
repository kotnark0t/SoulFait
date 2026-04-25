import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота
BOT_TOKEN = "8672976273:AAF2_7CQvkRFjtHbDoHdwxdc5ZMafWWrvo8"

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# URL с игрой (замените на ваш реальный URL после загрузки на Bothost)
GAME_URL = "https://your-domain.onrender.com/game"  # Замените на ваш URL


@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎮 Запустить Soul Knight",
            web_app=WebAppInfo(url=GAME_URL)
        )],
        [InlineKeyboardButton(
            text="📖 Как играть",
            callback_data="how_to_play"
        )],
        [InlineKeyboardButton(
            text="🏆 Рейтинг игроков",
            callback_data="rating"
        )]
    ])

    await message.answer(
        "🌟 **Добро пожаловать в Soul Knight!** 🌟\n\n"
        "⚔️ Сражайся с монстрами\n"
        "💰 Собирай монеты и ресурсы\n"
        "🛡️ Покупай оружие и баффы\n"
        "📜 Выполняй квесты\n\n"
        "Нажми на кнопку ниже, чтобы начать приключение!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    """Обработчик callback кнопок"""
    if callback.data == "how_to_play":
        await callback.message.answer(
            "📖 **Как играть в Soul Knight:**\n\n"
            "1️⃣ **Битва** - Нажми на портал, чтобы отправиться в бой\n"
            "2️⃣ **Атака** - Нажимай на кнопки атаки для удара по врагам\n"
            "3️⃣ **Магазины** - Покупай оружие у Кузнеца\n"
            "4️⃣ **Баффы** - Улучшай характеристики у Алхимика\n"
            "5️⃣ **Ресурсы** - Продавай ресурсы Скупщику за монеты\n"
            "6️⃣ **Квесты** - Выполняй задания для получения наград\n\n"
            "💡 Совет: Чем выше твой уровень, тем сильнее враги и лучше награды!",
            parse_mode="Markdown"
        )
    elif callback.data == "rating":
        await callback.message.answer(
            "🏆 **Таблица лидеров** 🏆\n\n"
            "Скоро здесь появится рейтинг лучших воинов!\n"
            "Покажи всем, на что способен настоящий герой!",
            parse_mode="Markdown"
        )

    await callback.answer()


@dp.message()
async def handle_message(message: types.Message):
    """Обработчик обычных сообщений"""
    await message.answer(
        "⚔️ Используй кнопку ниже, чтобы открыть игру и начать битву!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🎮 Открыть игру",
                web_app=WebAppInfo(url=GAME_URL)
            )]
        ])
    )


async def main():
    """Запуск бота"""
    print("🤖 Бот Soul Knight запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())