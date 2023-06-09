from qr_scaner import read_qr_code_async
import os
from aiogram import types, Dispatcher
from create_bot import bot, AcceptState
from aiogram.dispatcher import FSMContext
from sqlite import Database
import requests

def generate_output_string(data_tuple):
    product = data_tuple[1] + ': ' + data_tuple[3]
    amount = 'Количество: ' + data_tuple[4] + ' кг'
    supplier = 'Поставщик: ' + data_tuple[8]
    manufacturer = 'Изготовитель: ' + data_tuple[7]
    date = 'Дата: ' + data_tuple[9]
    id = 'ID: ' + data_tuple[0]
    operator = 'Оператор: ' + data_tuple[11]

    output = product + '\n' + amount + '\n' + supplier + '\n' + manufacturer + '\n' + date + '\n' + id + '\n' + operator
    return output


def find_qr_code_in_bd(qr_id):
    db = Database()
    for i in db.select_all_products():
        if str(qr_id) == str(i[0][-4:]):
            data = generate_output_string(i)
            return data
    return 'qr_код не найден'


# async def handle_photos_and_documents(message: types.Message):
#     # check if the sent file is an image
#     if message.content_type == types.ContentType.PHOTO:
#         file_id = message.photo[-1].file_id
#     elif message.content_type == types.ContentType.DOCUMENT and message.document.mime_type.startswith('image/'):
#         file_id = message.document.file_id
#     else:
#         return
#
#     # save the photo to disk
#     file_path = await bot.get_file(file_id)
#
#     file_name = os.path.basename(file_path.file_path)
#     await bot.download_file(file_path.file_path, os.path.join(os.getcwd(), 'photos', file_name))
#
#     # get text from QR code
#     text = await read_qr_code_async(file_name)
#
#     if not text:
#         # If the QR code could not be read, display a message and request the ID manually
#         await message.reply("Could not scan QR code. Please enter ID manually: ")
#         await AcceptState.find_qr.set()
#     else:
#         # send text to user
#         await message.reply(text)
#

async def handle_photos_and_documents(message: types.Message):
    # check if the sent file is an image
    if message.content_type == types.ContentType.PHOTO:
        file_id = message.photo[-1].file_id
    elif message.content_type == types.ContentType.DOCUMENT and message.document.mime_type.startswith('image/'):
        file_id = message.document.file_id
    else:
        return
    file = await bot.get_file(file_id)
    file_path = file.file_path
    photo_path = f"photos\photo_{file_id[1:5]}.png"  # генерируем уникальное имя файла для сохранения
    await bot.download_file(file_path, photo_path)
    text = await read_qr_code_async(photo_path)
    if not text:
        # If the QR code could not be read, display a message and request the ID manually
        await message.reply("Could not scan QR code. Please enter ID manually: ")
        await AcceptState.find_qr.set()
    else:
        # send text to user
        await message.reply(text)


async def find_qr(message: types.Message, state: FSMContext):
    qr_id = message.text
    await bot.send_message(message.from_user.id, find_qr_code_in_bd(qr_id))
    await state.finish()


def register_handlers_qr_cod_scaner(dp: Dispatcher):
    dp.register_message_handler(handle_photos_and_documents,
                                content_types=[types.ContentType.PHOTO, types.ContentType.DOCUMENT])
    dp.register_message_handler(find_qr, state=AcceptState.find_qr)
