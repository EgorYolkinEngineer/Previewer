from utils.image_processing import make_preview
from handlers.init import *
import asyncio
import os
import io


async def start_cmd_handler(msg: Message,):

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

    await msg.answer_sticker(sticker='CAACAgIAAxkBAAN7ZFD2m2SgAxweWK9uflY2iieRfEQAAlEAAyRxYhrpRxtfxj-nIy8E')
    await msg.answer(text=answer, parse_mode='markdown')


async def make_preview_handler(msg: Message):
    answer_msg = await msg.answer(text='⌛')

    try:
        if msg.photo:
            # список для хранения корутин загрузки фотографий
            download_tasks = []

            # обходим список фотографий и создаем корутину для каждой
            for photo in msg.photo:
                download_tasks.append(
                    photo.download(destination_file='./source/service/%s-background.jpg' % msg.from_user.id))

            # запускаем загрузку всех фотографий параллельно
            await asyncio.gather(*download_tasks)

            text, description = msg.caption.split('\n\n', maxsplit=1)
            flags, img = make_preview(text, description, msg.from_user.id, True)
        else:
            text, description = msg.text.split('\n\n')
            flags, img = make_preview(text, description, msg.from_user.id)

        byte_img = io.BytesIO()
        img.save(byte_img, format='JPEG')
        byte_img.seek(0)

        if flags.get('f', False):
            img_path = './source/service/%s-background.jpg' % msg.from_user.id
            img.save(img_path)
            await msg.answer_document(document=open(img_path, 'rb'))
        else:
            await msg.answer_photo(photo=byte_img)
        img.close()
        byte_img.close()
        try:
            os.remove('./source/service/%s-background.jpg' % msg.from_user.id)
        except FileNotFoundError:
            ...
    except FileNotFoundError:
        ...
    except Exception as error:
        await msg.answer_sticker(sticker='CAACAgIAAxkBAAN5ZFD2fS4yNhKmu1QU5JOcaz5ktPwAAk8AAyRxYhpYzOfip1OVSC8E')
        await msg.answer(text='🙃 Ошибка обработки. Возможно, вы указали некорректные флаги.\n\n'
                              '⚠ %s' % error)
    await answer_msg.delete()


async def get_sticker_id_handler(msg: Message):
    await msg.answer_sticker(sticker=msg.sticker.file_id)
    print(msg.sticker.file_id)
