from aiogram import types, Dispatcher
from create_bot import bot, AcceptState
from aiogram.dispatcher import FSMContext
from keyboards import (keyboard_type_wire_pv_list, keyboard_type_wire_pv, keyboard_yes_no, keyboard_type_yes_no_list,
                       keyboard_color_pv, keyboard_color_pv_list, keyboard_metr_pv, keyboard_metr_pv_list,
                       keyboard_create_defect, keyboard_create_defect_list, keyboard_print, keyboard_print_list,
                       keyboard_type_vvg, keyboard_type_vvg_list, keyboard_count_round, keyboard_count_round_list,
                       keyboard_sec_round_vvg_list, keyboard_sec_round_vvg)
from get_qr import (get_operation_id, get_date_now, generate_qr_code, get_data_to_db_operation, write_to_db_operation,
                    create_data_to_write_in_qr, create_data_to_send, find_user_descript)
from qr_scaner import read_qr_code_async
import os


def check_color(*args):
    return len(args) == len(set(args))


def check_wire(*args):
    return all(val == args[0] for val in args)


async def make_vvg_start(message: types.Message):
    await message.answer('Выберите из списка по форме:', reply_markup=keyboard_type_vvg)
    await AcceptState.type_vvg.set()


async def stop_make_vvg(user_id):
    await bot.send_message(user_id, 'Выберите из списка по форме:',
                           reply_markup=keyboard_type_vvg)
    await AcceptState.type_vvg.set()


async def send_qr_code(user_id, data_send):
    with open(data_send[1], 'rb') as qr:
        await bot.send_photo(user_id, qr, caption=data_send[0])


async def handle_photos_and_documents_id(file_id: str, message: types.Message, state: FSMContext):
    # сохраняем фотографию на диск
    file_path = await bot.get_file(file_id)
    file_name = file_path.file_path.split('/')[-1]
    await bot.download_file(file_path.file_path, os.path.join(os.getcwd(), 'photos', file_name))

    # получаем текст из QR кода
    text = await read_qr_code_async(file_name)
    text = text.split('\n')

    if text[0] == 'Изготовлено: ПУВ':
        return text
        # ID = text[-3].replace("ID: ", "")
        # wire = text[1].replace("Проволка: ", "")
        # color = text[2].replace("Цвет: ", "")
        # new_text = f'Изготовить ВВГнг(А)-LS {round_pieces}х{round_section} - {wire} - заготовка ID {ID} верно?'
        # await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)
        # return (ID, wire, color)

    else:
        await bot.send_message(message.from_user.id, 'ошибка - завершаю скрипт')
        await state.finish()


async def process_type_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Круглый':
        wire = callback_query.data
        await state.update_data(wire=wire)
        await bot.send_message(user_id, 'Выберите кол-во жил для круглого:', reply_markup=keyboard_count_round)
        await AcceptState.count_pieces_vvg.set()
    else:
        await bot.send_message(user_id, 'блок в разработке. Оставнавливаю сценарий')
        await state.finish()


async def process_round_count_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    round_count = callback_query.data
    await state.update_data(count_pieces=round_count)
    await bot.send_message(user_id, 'Выберите сечение для круголого:', reply_markup=keyboard_sec_round_vvg)
    await AcceptState.section_vvg.set()


async def process_round_section_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await stop_make_vvg(user_id)
    else:
        sec_round = callback_query.data
        await state.update_data(section_vvg=sec_round)
        await bot.send_message(user_id, 'Укажите метраж:')
        await AcceptState.metr_vvg.set()


async def process_metr_vvg(message: types.Message, state: FSMContext):
    metr = message.text
    await state.update_data(metr=metr)
    data = await state.get_data()
    count_pieces = data["count_pieces"]
    if count_pieces == '1':
        await bot.send_message(message.from_user.id, f'Отправьте мне фото QR-кода заготовки.')
        await AcceptState.photo_vvg.set()
    else:
        await bot.send_message(message.from_user.id,
                               f'Вам необходимо будет отправить мне подряд {data["count_pieces"]} фото QR-кодов.\n\nФото 1:')
        await AcceptState.photo_vvg_1.set()


async def process_photo_vvg(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        data = await state.get_data()
        info = await handle_photos_and_documents_id(file_id, message, state)
        new_text = f'Изготовить ВВГнг(А)-LS {data["count_pieces"]}х{data["section_vvg"]} - ' \
                   f'{info[1].replace("Проволка: ", "")} - ' \
                   f'{data["metr"]}м - заготовка ID {info[-3].replace("ID: ", "")} верно?'

        await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_vvg.set()


async def process_photo_vvg_1(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        info = await handle_photos_and_documents_id(file_id, message, state)

        ID = info[-3].replace("ID: ", "")
        wire = info[1].replace("Проволка: ", "")
        color = info[2].replace("Цвет: ", "")
        await state.update_data(piece_1=ID)
        await bot.send_message(message.from_user.id, 'Фото 2:')
        await AcceptState.photo_vvg_2.set()
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_vvg_1.set()


async def process_photo_vvg_2(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        info = await handle_photos_and_documents_id(file_id, message, state)
        ID = info[-3].replace("ID: ", "")
        wire = info[1].replace("Проволка: ", "")
        color = info[2].replace("Цвет: ", "")
        await state.update_data(piece_2=ID)
        data = await state.get_data()

        if int(data['count_pieces']) == 2:
            new_text = f'Изготовить ВВГнг(А)-LS {data["count_pieces"]}х{data["section_vvg"]} - ' \
                       f'{info[1].replace("Проволка: ", "")} - ' \
                       f'{data["metr"]}м - ID заготовок:  {data["piece_1"]}; {data["piece_2"]} верно?'
            await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)

            await AcceptState.yes_vvg_round()
        else:
            await bot.send_message(message.from_user.id, 'Фото 3:')
            await AcceptState.photo_vvg_3.set()
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_vvg_2.set()


async def process_photo_vvg_3(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        info = await handle_photos_and_documents_id(file_id, message, state)

        ID = info[-3].replace("ID: ", "")
        wire = info[1].replace("Проволка: ", "")
        color = info[2].replace("Цвет: ", "")
        await state.update_data(piece_3=ID)
        data = await state.get_data()

        if int(data['count_pieces']) == 3:
            new_text = f'Изготовить ВВГнг(А)-LS {data["count_pieces"]}х{data["section_vvg"]} - ' \
                       f'{info[1].replace("Проволка: ", "")} - ' \
                       f'{data["metr"]}м - ID заготовок:  {data["piece_1"]}; {data["piece_2"]}; {data["piece_3"]}' \
                       f' верно?'
            await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)

            await AcceptState.yes_vvg_round()
        else:
            await bot.send_message(message.from_user.id, 'Фото 4:')
            await AcceptState.photo_vvg_4.set()
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_vvg_3.set()


async def process_photo_vvg_4(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        info = await handle_photos_and_documents_id(file_id, message, state)

        ID = info[-3].replace("ID: ", "")
        wire = info[1].replace("Проволка: ", "")
        color = info[2].replace("Цвет: ", "")
        await state.update_data(piece_4=ID)
        data = await state.get_data()

        if int(data['count_pieces']) == 4:
            new_text = f'Изготовить ВВГнг(А)-LS {data["count_pieces"]}х{data["section_vvg"]} - ' \
                       f'{info[1].replace("Проволка: ", "")} - ' \
                       f'{data["metr"]}м - ID заготовок:  {data["piece_1"]}; {data["piece_2"]}; {data["piece_3"]};' \
                       f' {data["piece_4"]} верно?'
            await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)

            await AcceptState.yes_vvg_round()
        else:
            await bot.send_message(message.from_user.id, 'Фото 5:')
            await AcceptState.photo_vvg_5.set()
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_vvg_4.set()


async def process_photo_vvg_5(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        info = await handle_photos_and_documents_id(file_id, message, state)

        ID = info[-3].replace("ID: ", "")
        wire = info[1].replace("Проволка: ", "")
        color = info[2].replace("Цвет: ", "")
        await state.update_data(piece_5=ID)
        data = await state.get_data()

        if int(data['count_pieces']) == 5:
            new_text = f'Изготовить ВВГнг(А)-LS {data["count_pieces"]}х{data["section_vvg"]} - ' \
                       f'{info[1].replace("Проволка: ", "")} - ' \
                       f'{data["metr"]}м - ID заготовок:  {data["piece_1"]}; {data["piece_2"]}; {data["piece_3"]}; ' \
                       f'{data["piece_4"]}, ; {data["piece_5"]} верно?'
            await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)
            await AcceptState.yes_vvg_round.set()
        else:
            await state.finish()
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_vvg_5.set()


async def firs_yes_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'ДА':
        await bot.answer_callback_query(callback_query.id, text=f"ДА!")
        await bot.send_message(user_id, 'Укажите результат работы', reply_markup=keyboard_create_defect)
        await AcceptState.result_create.set()
        await state.finish()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await stop_make_vvg(user_id)


def register_handlers_client_make_vvg(dp: Dispatcher):
    dp.register_message_handler(make_vvg_start, commands=['make_vvg'])
    dp.register_callback_query_handler(process_type_vvg,
                                       lambda callback_query: callback_query.data in keyboard_type_vvg_list,
                                       state=AcceptState.type_vvg)
    dp.register_callback_query_handler(process_round_count_vvg,
                                       lambda callback_query: callback_query.data in keyboard_count_round_list,
                                       state=AcceptState.count_pieces_vvg)
    dp.register_callback_query_handler(process_round_section_vvg,
                                       lambda callback_query: callback_query.data in keyboard_sec_round_vvg_list,
                                       state=AcceptState.section_vvg)
    dp.register_message_handler(process_metr_vvg, state=AcceptState.metr_vvg)
    dp.register_message_handler(process_photo_vvg, content_types=['photo', 'document'], state=AcceptState.photo_vvg)
    dp.register_message_handler(process_photo_vvg_1, content_types=['photo', 'document'], state=AcceptState.photo_vvg_1)
    dp.register_message_handler(process_photo_vvg_2, content_types=['photo', 'document'], state=AcceptState.photo_vvg_2)
    dp.register_message_handler(process_photo_vvg_3, content_types=['photo', 'document'], state=AcceptState.photo_vvg_3)
    dp.register_message_handler(process_photo_vvg_4, content_types=['photo', 'document'], state=AcceptState.photo_vvg_4)
    dp.register_message_handler(process_photo_vvg_5, content_types=['photo', 'document'], state=AcceptState.photo_vvg_5)
