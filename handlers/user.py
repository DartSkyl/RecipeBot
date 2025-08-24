from random import choice

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from langchain_core.messages import HumanMessage, AIMessage

from utils.routers import users_router
import keyboards as keys
from config import ADMINS
from states import User
from loader import base
from utils.ai_core import ai_recipe


@users_router.callback_query(F.data == 'start')
async def after_sub_check(callback: CallbackQuery, state: FSMContext):
    """После проверки подписки"""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('Привет! Я бот с рецептами. Выбери действие:',
                                  # Если админ, то добавим кнопку для открытия админ-панели
                                  reply_markup=await keys.main_menu(callback.from_user.id in ADMINS))


@users_router.message(Command('start'))
async def strat_func(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('Привет! Я бот с рецептами. Выбери действие:',
                     # Если админ, то добавим кнопку для открытия админ-панели
                     reply_markup=await keys.main_menu(msg.from_user.id in ADMINS))


@users_router.message(F.text == '🍲 Случайный рецепт')
async def random_recipe(msg: Message, state: FSMContext):
    await state.set_state(User.random)
    await msg.answer('Выберете действие:', reply_markup=keys.back)
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


@users_router.callback_query(F.data.startswith('get_'))
async def show_redy_recipe(callback: CallbackQuery):
    """Показываем один из готовых рецептов"""
    recipe = await base.get_recipe_by_id(callback.data.removeprefix('get_'))
    recipe_button = await keys.recipe_url(recipe['recipe_url']) if recipe['recipe_url'] != 'empty' else None

    await callback.message.answer(f'*_Рецепт "{recipe["recipe_name"]}_*"\n\n{recipe["recipe_content"]}',
                                  reply_markup=recipe_button, parse_mode='MarkdownV2')


@users_router.callback_query(User.random, F.data == 'ready_recipe')
async def get_random_ready_recipe(callback: CallbackQuery, state: FSMContext):
    """Достаем любой готовый рецепт"""
    await state.clear()
    await callback.answer()
    try:
        random_ready_recipe = choice(await base.get_all_recipe())
        msg_text = f'*_Рецепт "{random_ready_recipe["recipe_name"]}":_*\n\n{random_ready_recipe["recipe_content"]}'

        recipe_button = await keys.recipe_url(random_ready_recipe['recipe_url']) \
            if random_ready_recipe['recipe_url'] != 'empty' else None

        await callback.message.answer(msg_text, reply_markup=recipe_button, parse_mode='MarkdownV2')
    except IndexError:
        await callback.message.answer('Доступных рецептов нет')


@users_router.message(F.text.in_(['🥗 Салаты', '🍖 Мясные блюда', '🍰 Десерты']))
async def salad_category(msg: Message, state: FSMContext):
    """Категория салатов"""
    category_dict = {
        '🥗 Салаты': User.salads,
        '🍖 Мясные блюда': User.meat,
        '🍰 Десерты': User.desserts,
    }
    await state.set_state(category_dict[msg.text])
    await msg.answer('Выберете действие:', reply_markup=keys.back)
    await msg.answer('Посмотреть готовый рецепт или по имеющимся продуктам?', reply_markup=keys.recipe_choice)


@users_router.callback_query(User.salads, F.data == 'ready_recipe')
@users_router.callback_query(User.meat, F.data == 'ready_recipe')
@users_router.callback_query(User.desserts, F.data == 'ready_recipe')
async def get_ready_recipe_by_category(callback: CallbackQuery, state: FSMContext):
    """Выдаем список готовых рецептов по категориям"""
    category = ((await state.get_state()).split(':'))[1]
    category_recipe_list = await base.get_recipe_by_category(category)
    if len(category_recipe_list) > 0:
        await callback.message.edit_text('Список доступных рецептов:',
                                         reply_markup=await keys.recipe_list_keyboard(category_recipe_list))
    else:
        await callback.message.answer('Доступных рецептов нет')


@users_router.callback_query(User.salads, F.data == 'input')
@users_router.callback_query(User.meat, F.data == 'input')
@users_router.callback_query(User.desserts, F.data == 'input')
@users_router.callback_query(User.random, F.data == 'input')
async def get_ready_recipe_by_category(callback: CallbackQuery):
    """Запрашиваем список имеющихся продуктов"""
    await callback.message.delete()
    await callback.message.answer('Введите список имеющихся у вас продуктов:', reply_markup=keys.cancel)


@users_router.callback_query(User.salads, F.data == 'more')
@users_router.callback_query(User.meat, F.data == 'more')
@users_router.callback_query(User.desserts, F.data == 'more')
@users_router.callback_query(User.random, F.data == 'more')
async def get_more_recipe(callback: CallbackQuery, state: FSMContext):
    """Просим ИИ дать еще варианты по имеющимся продуктам"""
    await callback.answer()
    chat_history = (await state.get_data())['chat_history']
    text_for_prompt_dict = {
        'salads': 'Какой еще салат я могу из этого приготовить? Дай еще три варианта',
        'meat': 'Какое еще мясное блюдо я могу из этого приготовить? Дай еще три варианта',
        'desserts': 'Какой еще десерт я могу из этого приготовить? Дай еще три варианта',
        'random': 'Что еще я могу из этого приготовить? Дай еще три варианта'
    }
    category = ((await state.get_state()).split(':'))[1]
    msg_for_del = await callback.message.answer('🔍 Ищу подходящий рецепт...')
    ai_answer = await ai_recipe(text_for_prompt_dict[category], chat_history)
    await callback.message.answer('Вот что нашел:', reply_markup=keys.back)
    await msg_for_del.delete()
    await callback.message.answer(ai_answer, reply_markup=keys.more)


@users_router.message(User.salads, F.text != 'Отмена')
@users_router.message(User.meat, F.text != 'Отмена')
@users_router.message(User.desserts, F.text != 'Отмена')
@users_router.message(User.random, F.text != 'Отмена')
async def get_ready_recipe_by_category(msg: Message, state: FSMContext):
    """Ловим список имеющихся продуктов и запрашиваем рецепты у ИИ"""
    text_for_prompt_dict = {
        'salads': 'Какой салат я могу из этого приготовить?',
        'meat': 'Какое мясное блюдо я могу из этого приготовить?',
        'desserts': 'Какой десерт я могу из этого приготовить?',
        'random': 'Что ты можешь посоветовать приготовить?'
    }
    category = ((await state.get_state()).split(':'))[1]
    msg_for_del = await msg.answer('🔍 Ищу подходящий рецепт...')
    user_products_str = f'Вот какие продукты у меня есть: {msg.text}. {text_for_prompt_dict[category]}'
    ai_answer = await ai_recipe(user_products_str, [])
    await state.set_data({'chat_history': [HumanMessage(content=user_products_str), AIMessage(content=ai_answer)]})
    await msg_for_del.delete()
    await msg.answer('Вот что нашел:', reply_markup=keys.back)
    await msg.answer(ai_answer, reply_markup=keys.more)


@users_router.message(F.text == 'Отмена')
async def cancel_func(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('Действие отменено',
                     # Если админ, то добавим кнопку для открытия админ-панели
                     reply_markup=await keys.main_menu(msg.from_user.id in ADMINS))
