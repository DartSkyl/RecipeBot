from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types.chat_member_left import ChatMemberLeft
from aiogram.exceptions import TelegramBadRequest

from utils.routers import users_router
import keyboards as keys
from config import MAIN_CHANNEL, ADMINS


@users_router.message(Command('start'))
async def strat_func(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('Привет! Я бот с рецептами. Выбери действие:',
                     # Если админ, то добавим кнопку для открытия админ-панели
                     reply_markup=await keys.main_menu(msg.from_user.id in ADMINS))


@users_router.message(F.text == '🍲 Случайный рецепт')
async def random_recipe(msg: Message):
    await msg.answer('Посмотреть готовый рецепт или по имеющимся продуктам?', reply_markup=keys.recipe_choice)


@users_router.message(F.text == '📖 Категории')
async def category_menu(msg: Message):
    await msg.answer('Выбери категорию:', reply_markup=keys.categories)


@users_router.message(F.text == '⬅ Назад')
async def back(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('Возвращаю в главное меню:',
                     # Если админ, то добавим кнопку для открытия админ-панели
                     reply_markup=await keys.main_menu(msg.from_user.id in ADMINS))
