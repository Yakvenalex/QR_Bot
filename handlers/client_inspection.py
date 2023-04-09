from aiogram import types, Dispatcher
from create_bot import bot, InspectionStates
from aiogram.dispatcher import FSMContext
from keyboards import keyboard_next_photo
from qr_scaner import read_qr_code_async
import os


async def start_inspection(message: types.Message):
    await message.answer('Пожалуйста, отправьте фото qr-кода')
    await InspectionStates.waiting_for_photo.set()


async def receive_photo(message: types.Message, state: FSMContext):
    if not (message.photo or (message.document and 'image' in message.document.mime_type.lower())):
        await message.answer('Пожалуйста, отправьте фотографию или документ с изображением qr-кода')
        return

    async with state.proxy() as data:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        file_path = await bot.get_file(file_id)
        file_name = os.path.basename(file_path.file_path)
        file_local_path = os.path.join(os.getcwd(), 'photos', file_name)
        await bot.download_file(file_path.file_path, file_local_path)
        text = await read_qr_code_async(file_local_path)
        data['photos'] = data.get('photos', []) + [{'file_id': file_id, 'text': text}]

    await message.answer('Спасибо, фото qr-кода получено!', reply_markup=keyboard_next_photo)
    await InspectionStates.waiting_for_next_photo.set()


async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if callback_query.data == 'more_photo':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'Пожалуйста, отправьте ещё фотографию')
        await InspectionStates.waiting_for_photo.set()

    elif callback_query.data == 'calculate':
        for photo in data.get('photos', []):
            await bot.send_message(callback_query.from_user.id, photo['text'])

        await state.finish()


def register_handlers_client_inspect(dp: Dispatcher):
    dp.register_message_handler(start_inspection, commands=['inspection'])
    dp.register_message_handler(receive_photo, content_types=[types.ContentType.PHOTO, types.ContentType.DOCUMENT],
                                state=InspectionStates.waiting_for_photo)
    dp.register_callback_query_handler(process_callback, state=InspectionStates.waiting_for_next_photo)
