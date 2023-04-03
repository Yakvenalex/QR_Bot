from qr_scaner import read_qr_code_async
import os
from aiogram import types, Dispatcher
from create_bot import bot

async def handle_photos_and_documents(message: types.Message):
    # проверяем, является ли отправленный файл изображением
    if message.content_type == types.ContentType.PHOTO:
        file_id = message.photo[-1].file_id
    elif message.content_type == types.ContentType.DOCUMENT and message.document.mime_type.startswith('image/'):
        file_id = message.document.file_id
    else:
        return

    # сохраняем фотографию на диск
    file_path = await bot.get_file(file_id)
    file_name = file_path.file_path.split('/')[-1]
    await bot.download_file(file_path.file_path, os.path.join(os.getcwd(), 'photos', file_name))

    # получаем текст из QR кода
    text = await read_qr_code_async(file_name)

    # отправляем текст пользователю
    await message.reply(text)


def register_handlers_qr_cod_scaner(dp: Dispatcher):
    dp.register_message_handler(handle_photos_and_documents, content_types=[types.ContentType.PHOTO, types.ContentType.DOCUMENT])