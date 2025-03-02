from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BufferedInputFile, InputMediaPhoto, URLInputFile
from providers.tts_provider import tts, remote_tts, tts_convert
from custom_queue import UserLimitedQueue, semaphore_wrapper
from config_reader import config
import asyncio

class TextToSpeechModule:
  def __init__(self, dp, bot, broker):
    self.queue = UserLimitedQueue(config.tts_queue_size_per_user)
    self.semaphore = asyncio.Semaphore(1)
    
    @dp.message(Command(commands=["tts", *config.tts_voices]), flags={"long_operation": "record_audio"})
    async def command_tts_handler(message: Message, command: CommandObject) -> None:
      with self.queue.for_user(message.from_user.id) as available:
        if available:
          if command.command == "tts" or not command.args or str(command.args).strip() == "" or ('-help' in str(command.args)):
            return await message.answer(f"usage: {' '.join(['/' + x for x in config.tts_voices])} text,\nUse the commands like /command@botname \n{config.tts_credits}")
          voice = command.command
          text = str(command.args)
          task_function = remote_tts if config.tts_mode != 'local' else tts
          task = await broker.task(semaphore_wrapper(self.semaphore, task_function)).kiq(voice, text)
          result = await task.wait_result(timeout=240)
          completed, data = result.return_value
          if not completed:
            return await message.answer(f"Error, <b>{data}</b>")
          else:
            audio = BufferedInputFile(tts_convert(data), 'tts.ogg')
            return await message.answer_voice(voice=audio)




















