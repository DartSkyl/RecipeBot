from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup, ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup


# ====================
# Общие клавиатуры
# ====================


async def main_menu(admin=False):
    keys = ReplyKeyboardBuilder()
    keys.add(KeyboardButton(text='🍲 Случайный рецепт'))
    keys.add(KeyboardButton(text='📖 Категории'))
    if admin:
        keys.add(KeyboardButton(text='⚙ Админ панель'))
    keys.adjust(1)
    return keys.as_markup(resize_keyboard=True)


categories = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🥗 Салаты')],
    [KeyboardButton(text='🍖 Мясные блюда')],
    [KeyboardButton(text='🍰 Десерты')],
    [KeyboardButton(text='⬅ Назад')]
], resize_keyboard=True)

recipe_choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Готовый рецепт', callback_data='ready_recipe')],
    [InlineKeyboardButton(text='Ввести имеющиеся продукты', callback_data='input')]
])


async def sub_keys(channel_url):
    keys = InlineKeyboardBuilder()
    keys.button(text='Подписаться', url=channel_url)
    keys.button(text='Проверить', callback_data='start')
    keys.adjust(1)
    return keys.as_markup()


# ====================
# Для админов
# ====================


admin_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Ссылки на источники')],
    [KeyboardButton(text='Свои рецепты')],
], resize_keyboard=True)

link_action = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить ссылку', callback_data='link_add')],
    [InlineKeyboardButton(text='🗑 Удалить ссылку', callback_data='link_remove')]
])

confirm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Да', callback_data='yes')],
    [InlineKeyboardButton(text='🚫 Нет', callback_data='no')]
])


async def recipe_list_keyboard(recipe_list: list):
    keys = InlineKeyboardBuilder()
    for r in recipe_list:
        keys.button(text=r['recipe_name'], callback_data=f'get_{r["recipe_id"]}')
    keys.adjust(1)
    return keys.as_markup()


async def remove_url(url_list: list):
    key = InlineKeyboardBuilder()
    for url in url_list:
        key.button(text=f'Удалить "{url["url_name"]}"', callback_data=f'remove_url_{url["link_id"]}')
    key.adjust(1)
    return key.as_markup()


category_choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🥗 Салаты', callback_data='salads')],
    [InlineKeyboardButton(text='🍖 Мясные блюда', callback_data='meat')],
    [InlineKeyboardButton(text='🍰 Десерты', callback_data='desserts')]
])


async def recipe_action(category):
    keys = InlineKeyboardBuilder()
    keys.button(text='➕ Добавить рецепт', callback_data=f'recipe_{category}_add')
    keys.button(text='🔎 Посмотреть рецепт', callback_data=f'recipe_{category}_view')
    keys.button(text='🗑 Удалить рецепт', callback_data=f'recipe_{category}_remove')
    keys.adjust(1)
    return keys.as_markup()


async def show_recipe_list(recipe_list):
    keys = InlineKeyboardBuilder()
    for r in recipe_list:
        keys.button(text=r['recipe_name'], callback_data=f'show_{r["recipe_id"]}')
    keys.adjust(1)
    return keys.as_markup()


async def remove_recipe_list(recipe_list, category):
    keys = InlineKeyboardBuilder()
    for r in recipe_list:
        keys.button(text=r['recipe_name'], callback_data=f'delete_{r["recipe_id"]}_{category}')
    keys.adjust(1)
    return keys.as_markup()


cancel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отмена')]
], resize_keyboard=True)


skip = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Пропустить')],
    [KeyboardButton(text='Отмена')],
], resize_keyboard=True)


async def recipe_url(url):
    url_key = InlineKeyboardBuilder()
    url_key.button(text='Смотреть видео', url=f'{url}')
    url_key.adjust(1)
    return url_key.as_markup()
