import string
from random import choices

from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.fsm.context import FSMContext

from utils.routers import admin_router
import keyboards as keys
from loader import base
from states import Admin


@admin_router.message(F.text == '⚙ Админ панель')
async def open_admin_panel(msg: Message):
    await msg.answer('Выберете действие:', reply_markup=keys.admin_menu)


# ====================
# Операции со ссылками
# ====================


@admin_router.message(F.text == 'Ссылки на источники')
async def links_action_menu(msg: Message):
    url_list = await base.get_links()
    url_list = '\n\n'.join([u['url_name'] + '\n' + u['url_content'] for u in url_list])
    await msg.answer(f'Ссылки на источники:\n\n{url_list}', reply_markup=keys.link_action)


@admin_router.callback_query(F.data.startswith('link'))
async def link_action(callback: CallbackQuery, state: FSMContext):
    """Ловим действие со ссылками - удалить или добавить"""
    if callback.data == 'link_add':
        await state.set_state(Admin.add_link_name)
        await callback.message.answer('Введите название ссылки:')
    else:
        url_list = await base.get_links()
        await callback.message.answer('Выберете ссылку для удаления:', reply_markup=await keys.remove_url(url_list))


@admin_router.message(Admin.add_link_name, F.text != 'Отмена')
async def catch_link_name(msg: Message, state: FSMContext):
    """Ловим название ссылки"""
    await state.set_data({'link_name': msg.text})
    await state.set_state(Admin.add_link_url)
    await msg.answer('Теперь скиньте саму ссылку:')


@admin_router.message(Admin.add_link_url, F.text != 'Отмена')
async def catch_link_url(msg: Message, state: FSMContext):
    """Ловим саму ссылку и сохраняем"""
    url_id = ''.join(choices(string.digits + string.ascii_letters, k=8))

    await base.insert_new_url(
        link_id=url_id,
        url_name=(await state.get_data())['link_name'],
        url_content=msg.text
    )
    await state.clear()
    await msg.answer('Ссылка создана', reply_markup=keys.admin_menu)
    await links_action_menu(msg)


@admin_router.callback_query(F.data.startswith('remove_url_'))
async def remove_url_start(callback: CallbackQuery, state: FSMContext):
    """Начинаем удаление ссылки"""
    link_id = callback.data.removeprefix('remove_url_')
    await state.set_data({'link_id': link_id})
    await state.set_state(Admin.remove_link)
    await callback.message.answer('Вы уверены?', reply_markup=keys.confirm)


@admin_router.callback_query(Admin.remove_link, F.data.in_(['yes', 'no']))
async def remove_url(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления ссылки"""
    if callback.data == 'yes':
        await base.remove_link(link_id=(await state.get_data())['link_id'])
        await state.clear()

    else:
        await state.clear()

    await links_action_menu(callback.message)


# ====================
# Операции с рецептами
# ====================


@admin_router.message(F.text == 'Свои рецепты')
async def recipe_action_menu(msg: Message, state: FSMContext):
    """Меню категорий с рецептами"""
    await msg.answer('Выберете категорию:', reply_markup=keys.category_choice)


async def recipe_list_show_func(msg: Message, category):
    """Вывод всех рецептов в категории"""
    recipe_dict = {
        'salads': 'Салаты',
        'meat': 'Мясные блюда',
        'desserts': 'Десерты',
    }

    recipe_list = await base.get_recipe_by_category(category)
    recipe_list = '\n'.join([r['recipe_name'] for r in recipe_list])
    await msg.answer(f'Список рецептов <b>"{recipe_dict[category]}"</b>:\n\n<b><i>{recipe_list}</i></b>',
                     reply_markup=await keys.recipe_action(category))


@admin_router.callback_query(F.data.in_(['salads', 'meat', 'desserts']))
async def category_choice(callback: CallbackQuery, state: FSMContext):
    """Открываем выбранную категорию с кнопками действий"""

    await recipe_list_show_func(callback.message, callback.data)


@admin_router.callback_query(F.data.startswith('recipe_'))
async def recipe_action(callback: CallbackQuery, state: FSMContext):
    """Ловим выбор действия с рецептами"""
    action_info = callback.data.split('_')
    if action_info[2] == 'add':
        await state.set_state(Admin.new_recipe_name)
        await state.set_data({'category': action_info[1]})
        await callback.message.answer('Введите название рецепта:', reply_markup=keys.cancel)
    elif action_info[2] == 'view':
        recipe_list = await base.get_recipe_by_category(action_info[1])
        await callback.message.edit_text('Выберете рецепт для просмотра:',
                                         reply_markup=await keys.show_recipe_list(recipe_list))
    else:
        recipe_list = await base.get_recipe_by_category(action_info[1])
        await callback.message.edit_text('Выберете рецепт для удаления:',
                                         reply_markup=await keys.remove_recipe_list(recipe_list, action_info[1]))


@admin_router.callback_query(F.data.startswith('show_'))
async def show_recipe(callback: CallbackQuery):
    """Открываем конкретный рецепт"""
    recipe = await base.get_recipe_by_id(callback.data.removeprefix('show_'))

    recipe_button = await keys.recipe_url(recipe['recipe_url']) if recipe['recipe_url'] != 'empty' else None

    await callback.message.answer(f'*_Рецепт "{recipe["recipe_name"]}_*"\n\n{recipe["recipe_content"]}',
                                  reply_markup=recipe_button, parse_mode='MarkdownV2')


@admin_router.callback_query(F.data.startswith('delete_'))
async def remove_recipe(callback: CallbackQuery):
    """Удаляем конкретный рецепт"""
    recipe_data = callback.data.split('_')
    await base.remove_recipe(recipe_data[1])
    await callback.message.answer('Рецепт удален')
    await recipe_list_show_func(callback.message, recipe_data[2])


@admin_router.message(Admin.new_recipe_name, F.text != 'Отмена')
async def catch_recipe_name(msg: Message, state: FSMContext):
    """Ловим название рецепта"""
    await state.update_data({'recipe_name': msg.text})
    await state.set_state(Admin.new_recipe_content)
    await msg.answer('Теперь сам рецепт:', reply_markup=keys.cancel)


@admin_router.message(Admin.new_recipe_content, F.text != 'Отмена')
async def catch_recipe_content(msg: Message, state: FSMContext):
    """Ловим сам рецепт и предлагаем скинуть ссылку на видео"""
    await state.update_data({'recipe_content': msg.md_text})  # Сохраняем в разметке MARKDOWN
    await state.set_state(Admin.new_recipe_link)
    await msg.answer('Теперь ссылку на видео или нажмите "Пропустить":', reply_markup=keys.skip)


@admin_router.message(Admin.new_recipe_link, F.text != 'Отмена')
async def cath_recipe_link(msg: Message, state: FSMContext):
    """Ловим ссылку если таковая есть и сохраняем рецепт"""

    recipe_data = await state.get_data()
    await base.add_new_recipe(
        recipe_id=''.join(choices(string.digits + string.ascii_letters, k=8)),
        recipe_name=recipe_data['recipe_name'],
        recipe_content=recipe_data['recipe_content'],
        recipe_url=msg.text if msg.text != 'Пропустить' else 'empty',
        category=recipe_data['category']
    )
    await state.clear()
    await msg.answer('Рецепт сохранен', reply_markup=keys.admin_menu)

    await recipe_list_show_func(msg, recipe_data['category'])
