from aiogram.dispatcher.flags import get_flag
from aiogram.utils.chat_action import ChatActionSender
from aiogram import BaseMiddleware
from aiogram.types import Message
from config_reader import config
from custom_queue import CallCooldown
import logging
logger = logging.getLogger(__name__)

class ChatActionMiddleware(BaseMiddleware):
  async def __call__(self, handler, event, data):
    long_operation_type = get_flag(data, "long_operation")

    if not long_operation_type:
      return await handler(event, data)

    async with ChatActionSender(action=long_operation_type, chat_id=event.chat.id):
      return await handler(event, data)

class AccessMiddleware(BaseMiddleware):
  async def __call__(self, handler, event, data):
    uid = event.from_user.id
    cid = event.chat.id
    logger.info(f'message in chat {cid} ({event.chat.title or "private"}) from {uid} (@{event.from_user.username or event.from_user.first_name})')
    if config.ignore_mode == 'whitelist' or config.ignore_mode == 'both':
      if cid not in config.whitelist:
        return
    if config.ignore_mode == 'blacklist' or config.ignore_mode == 'both':
      if uid in config.blacklist or cid in config.blacklist:
        return
    if get_flag(data, "admins_only"):
      if uid not in config.adminlist:
        return
    return await handler(event, data)

class CooldownMiddleware(BaseMiddleware):
  async def __call__(self, handler, event, data):
    cooldown_seconds = get_flag(data, "cooldown")
    if cooldown_seconds:
      function_name = data['handler'].callback.__name__
      if CallCooldown.check_call(event.from_user.id, function_name, cooldown_seconds):
        return await handler(event, data)
      else:
        return
    else:
      return await handler(event, data)