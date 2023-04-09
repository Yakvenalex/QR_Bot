from aiogram import types, Dispatcher
from create_bot import bot, AcceptState, dp
from aiogram.dispatcher import FSMContext
from keyboards import keyboard_create_defect, keyboard_type_vvg, keyboard_count_round, keyboard_yes_no, \
    keyboard_sec_round_vvg, keyboard_type_wire
from qr_scaner import read_qr_code_async
import os
from async_funck import stop_script, step_back


@dp.message_handler(commands=['make_vvg'])
async def make_vvg_start(message: types.Message):
    await message.answer('Выберите из списка по форме:', reply_markup=keyboard_type_vvg)
    await AcceptState.type_vvg.set()


async def handle_photos_and_documents_id(file_id: str, message: types.Message, state: FSMContext):
    file = await bot.get_file(file_id)
    file_path = file.file_path
    photo_path = f"photos\photo_{file_id}.png"  # генерируем уникальное имя файла для сохранени
    await bot.download_file(file_path, photo_path)
    text = await read_qr_code_async(photo_path)
    text = text.split('\n')
    if text[0] == 'Изготовить: Скрутка':
        return text
    else:
        await bot.send_message(message.from_user.id, 'ошибка - завершаю скрипт')
        await state.finish()


@dp.callback_query_handler(state=AcceptState.type_vvg)
async def process_type_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Круглый':
        await state.update_data(wire=callback_query.data)
        await bot.send_message(callback_query.from_user.id, 'Выберите кол-во жил для круглого:',
                               reply_markup=keyboard_count_round)
        await AcceptState.count_round_vvg.set()
    else:
        await bot.send_message(callback_query.from_user.id, 'блок в разработке. Оставнавливаю сценарий')
        await state.finish()


@dp.callback_query_handler(state=AcceptState.count_round_vvg)
async def process_section_round(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Назад':
        await stop_script(callback_query.id, callback_query.from_user.id, AcceptState.type_vvg.set(), keyboard_type_vvg)
    else:
        await state.update_data(count_round=callback_query.data)
        await bot.send_message(callback_query.from_user.id, 'Выберите сечение:', reply_markup=keyboard_sec_round_vvg)
        await AcceptState.section_vein_round.set()


@dp.callback_query_handler(state=AcceptState.section_vein_round)
async def process_round_vein(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Заново':
        await stop_script(callback_query.id, callback_query.from_user.id, AcceptState.type_vvg.set(), keyboard_type_vvg)
    elif callback_query.data == 'Назад':
        await step_back(callback_query.from_user.id, 'Выберите кол-во жил для круглого:',
                        AcceptState.count_round_vvg.set(), keyboard_count_round)
    elif callback_query.data == 'enter':
        await bot.send_message(callback_query.from_user.id, 'Введите сечение:')
        await AcceptState.section_vein_round_hand.set()
    else:
        await state.update_data(vein_round=callback_query.data)
        await bot.send_message(callback_query.from_user.id, 'Выбирите сечение, которое будет участвовать в проверке:',
                               reply_markup=keyboard_type_wire)
        await AcceptState.section_vein_round_check.set()


@dp.message_handler(state=AcceptState.section_vein_round_hand)
async def hand_section_vein_round(message: types.Message, state: FSMContext):
    await state.update_data(vein_round=message.text)
    await bot.send_message(message.from_user.id, 'Выбирите сечение, которое будет участвовать в проверке:',
                           reply_markup=keyboard_type_wire)
    await AcceptState.section_vein_round_check.set()


@dp.callback_query_handler(state=AcceptState.section_vein_round_check)
async def process_round_section_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Заново':
        await stop_script(callback_query.id, callback_query.from_user.id, AcceptState.type_vvg.set(), keyboard_type_vvg)
    elif callback_query.data == 'Назад':
        await step_back(callback_query.from_user.id, 'Выберите сечение:', AcceptState.section_vein_round.set(),
                        keyboard_sec_round_vvg)
    elif callback_query.data == 'Другой тип проволоки':
        await bot.send_message(callback_query.from_user.id, 'Введите сечение, которое будет участвовать в проверке:')
        await AcceptState.section_vein_round_check_hand.set()
    else:
        await state.update_data(section_vein_round_check=callback_query.data)
        await bot.send_message(callback_query.from_user.id, "Укажите метраж:")
        await AcceptState.metr_vvg_round.set()


@dp.message_handler(state=AcceptState.section_vein_round_check_hand)
async def hand_section_vein_round(message: types.Message, state: FSMContext):
    await state.update_data(section_vein_round_check=message.text)
    await bot.send_message(message.from_user.id, "Укажите метраж:")
    await AcceptState.metr_vvg_round.set()


@dp.message_handler(state=AcceptState.metr_vvg_round)
async def process_metr_vvg(message: types.Message, state: FSMContext):
    await state.update_data(metr=message.text)
    await bot.send_message(message.from_user.id, f'Отправьте мне фото QR-кода заготовки.')
    await AcceptState.photo_vvg_round.set()


@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.DOCUMENT],
                    state=AcceptState.photo_vvg_round)
async def process_photo_vvg(message: types.Message, state: FSMContext):
    if message.content_type == types.ContentType.PHOTO:
        file_id = message.photo[-1].file_id
    elif message.content_type == types.ContentType.DOCUMENT and message.document.mime_type.startswith('image/'):
        file_id = message.document.file_id
    else:
        file_id = ''
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_vvg_round.set()

    data = await state.get_data()
    info = await handle_photos_and_documents_id(file_id, message, state)
    new_text = f'Изготовить ВВГ-Пнг(А)-LS {data["count_round"]}х{data["vein_round"]} - ' \
               f'{data["section_vein_round_check"]} - заготовка ID {info[-3].replace("ID: ")} верно?'
    await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)
    await AcceptState.yes_vvg_round.set()


@dp.callback_query_handler(state=AcceptState.yes_vvg_round)
async def firs_yes_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'ДА':
        await bot.answer_callback_query(callback_query.id, text=f"ДА!")
        await bot.send_message(callback_query.from_user.id, 'Укажите результат работы',
                               reply_markup=keyboard_create_defect)
        await AcceptState.result_create.set()
        await state.finish()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await AcceptState.restart_round_vvg.set()
