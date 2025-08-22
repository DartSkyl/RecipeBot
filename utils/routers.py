from aiogram import Router
from aiogram.types import Message
from aiogram.filters import BaseFilter
from aiogram.types.chat_member_left import ChatMemberLeft

from config import ADMINS, MAIN_CHANNEL, MAIN_CHANNEL_URL
from loader import bot
from keyboards import sub_keys


class IsAdminFilter(BaseFilter):
    """Фильтр, проверяющий является ли отправитель сообщения админом"""
    def __init__(self, admins_list):

        # Список ID администраторов загружается прямо
        # из основной группы во время запуска бота
        self.admins_list = admins_list

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admins_list


admin_router = Router()

# Выше описанный фильтр добавляем прямо в роутер
admin_router.message.filter(IsAdminFilter(admins_list=ADMINS))


class UserSubscription(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        is_member = await bot.get_chat_member(MAIN_CHANNEL, message.from_user.id)
        if not isinstance(is_member, ChatMemberLeft):
            return True
        else:
            await bot.send_message(message.from_user.id, f'Сначала нужно подписаться на канал:\n{MAIN_CHANNEL_URL}',
                                   reply_markup=await sub_keys(MAIN_CHANNEL_URL))
            return False


users_router = Router()

users_router.message.filter(UserSubscription())
users_router.callback_query.filter(UserSubscription())
