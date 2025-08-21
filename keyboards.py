from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup, ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup


# Общие клавиатуры


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


# Для админов

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


async def remove_url(url_list: list):
    key = InlineKeyboardBuilder()
    for url in url_list:
        key.button(text=f'Удалить "{url["url_name"]}"', callback_data=f'remove_url_{url["link_id"]}')
    key.adjust(1)
    return key.as_markup()
