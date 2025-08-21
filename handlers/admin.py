import string
from random import choices

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types.chat_member_left import ChatMemberLeft
from aiogram.exceptions import TelegramBadRequest

from utils.routers import admin_router
import keyboards as keys
from loader import base
from states import Admin


@admin_router.message(F.text == '⚙ Админ панель')
async def open_admin_panel(msg: Message):
    await msg.answer('Выберете действие:', reply_markup=keys.admin_menu)


@admin_router.message(F.text == 'Ссылки на источники')
async def links_action_menu(msg: Message):
    url_list = await base.get_links()
    url_list = '\n'.join([u['url_content'] for u in url_list])
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
    if callback.data == 'yes':
        await base.remove_link(link_id=(await state.get_data())['link_id'])
        await state.clear()

    else:
        await state.clear()

    await links_action_menu(callback.message)

