from aiogram.types import Message
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile

from services.images_service import make_preview

from core.config import bot
from core import config

import asyncio, os

messages_router = Router(name="messages")


@messages_router.message(Command(commands=["start"],
                                 prefix="/"))
async def start_cmd_handler(msg: Message):

    answer = ('Привет, *%s*!👋\n\n'
              'Отправь мне текст для твоего заголовка.\n'
              'Ты можешь установить фоновое '
              'изображение, просто прикрепив его '
              'к тексту в одном сообщении.\n\n'
              '⚠ Формат сообщения (*два переноса строки между '
              'заголовком и описанием*):\n'
              '`Заголовок\n\n'
              'Описание`\n'
              '{ флаги }\n\n'
              '🚩 Флаги\n\n'
              '💬 Шрифты\n'
              '`/ts 150` - размер шрифта заголовка\n'
              '`/ds 100` - размер шрифта описания'
              '`/to 10` - смещение заголовка\n'
              '`/do 400` - смещение описания\n\n'
              '📖 Строки\n'
              '`/tlw 30` - максимальное кол-во букв в заголовке\n'
              '`/dlw 60` - максимальное кол-во букв в описании\n\n'
              '🔤 Шрифты\n'
              '`/tf 0` - шрифт заголовка (0  /1)\n'
              '`/df 1` - шрифт описания (0 / 1)\n\n'
              '🖼 Фон\n'
              '`/bg 5` - затемнение (1 - 9)\n'
              '`/bl 30` - блюр фона (1 - 100)\n'
              '`/nc 1` - не кадрировать\n'
              '`/sq 1` - сделать фон квадратным\n'
              '`/nbg 1` - не затемнять\n\n'
              '⚙ Сервисные флаги\n'
              '`/f 1` - отправить фото как файл\n\n'
              '⚠ *Флаги применяются так*:\n'
              '/flag { значение }') % msg.from_user.first_name

    await msg.answer_sticker(sticker=config.START_MESSAGE_STICKER_ID)
    await msg.answer(text=answer, parse_mode='markdown')
    
    
def get_text_data(msg: Message) -> tuple[str, str]:
    if msg.caption:
        textsplit = [i.strip().replace('\n', '') 
                     for i in msg.caption.split('\n\n', 
                                                maxsplit=1)]
    else:
        textsplit = [i.strip().replace('\n', '') 
                     for i in msg.text.split('\n\n', 
                                             maxsplit=1)]
    
    if len(textsplit) > 1:
        text, description = textsplit
    else:
        text, description = (textsplit[0], str())
        
    return (text, description)


async def get_image_data(msg: Message, 
                         text: str, 
                         description: str, 
                         img_path: str
                         ) -> tuple:
    if msg.photo:
        image_file = await bot.get_file(file_id=msg.photo[-1].file_id)
        
        await bot.download_file(image_file.file_path, 
                                destination=img_path)

        flags, img = make_preview(text, description, msg.from_user.id, True)
    else:
        flags, img = make_preview(text, description, msg.from_user.id)
        
    return flags, img


@messages_router.message()
async def make_preview_handler(msg: Message):
    answer_msg = await msg.answer(text='⌛')

    try:
        text, description = get_text_data(msg=msg)
        
        img_path = './source/service/%s-background.jpg' % msg.from_user.id
        
        flags, img = await get_image_data(msg=msg, 
                                    text=text, 
                                    description=description, 
                                    img_path=img_path)
        img.save(img_path)
        
        upload_photo = FSInputFile(img_path)

        if flags.get('f', False):
            await msg.answer_document(document=upload_photo)
        else:
            await msg.answer_photo(photo=upload_photo)

        img.close()
        
        try:
            os.remove('./source/service/%s-background.jpg' % msg.from_user.id)
        except FileNotFoundError:
            ...
    except Exception as error:
        await msg.answer_sticker(
            sticker='CAACAgIAAxkBAAN5ZFD2fS4yNhKmu1QU5JOcaz5ktPwAAk8AAyRxYhpYzOfip1OVSC8E')
        await msg.answer(text='🙃 Ошибка обработки. Возможно, вы указали некорректные флаги.\n\n'
                              '⚠ %s' % error)

@messages_router.message()
async def get_sticker_id_handler(msg: Message):
    answer = "Пиши /start 🦄"
