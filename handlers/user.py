from random import choice

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types.chat_member_left import ChatMemberLeft
from aiogram.exceptions import TelegramBadRequest

from utils.routers import users_router
import keyboards as keys
from config import MAIN_CHANNEL, ADMINS
from states import User
from loader import base
from utils.ai_core import ai_recipe


@users_router.message(Command('start'))
async def strat_func(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('Привет! Я бот с рецептами. Выбери действие:',
                     # Если админ, то добавим кнопку для открытия админ-панели
                     reply_markup=await keys.main_menu(msg.from_user.id in ADMINS))


@users_router.message(F.text == '🍲 Случайный рецепт')
async def random_recipe(msg: Message, state: FSMContext):
    await state.set_state(User.random)
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


@users_router.callback_query(User.random, F.data == 'ready_recipe')
async def get_random_ready_recipe(callback: CallbackQuery, state: FSMContext):
    """Достаем любой готовый рецепт"""
    await state.clear()
    await callback.answer()
    random_ready_recipe = choice(await base.get_all_recipe())
    msg_text = f'*_Рецепт "{random_ready_recipe["recipe_name"]}":_*\n\n{random_ready_recipe["recipe_content"]}'

    recipe_button = await keys.recipe_url(random_ready_recipe['recipe_url']) \
        if random_ready_recipe['recipe_url'] != 'empty' else None

    await callback.message.answer(msg_text, reply_markup=recipe_button, parse_mode='MarkdownV2')


@users_router.callback_query(User.random, F.data == 'input')
async def get_random_input_recipe(callback: CallbackQuery, state: FSMContext):
    """Просим ИИ дать нам любой рецепт"""
    await callback.answer()
    await callback.message.answer('Введите список имеющихся у вас продуктов:')


@users_router.message(User.random, F.text != 'Отмена')
async def get_random_input_recipe(msg: Message, state: FSMContext):
    await state.clear()
    ai_answer = await ai_recipe(f'Вот какие продукты у меня есть: {msg.text}. Что ты можешь посоветовать приготовить?')
    await msg.answer(ai_answer)
