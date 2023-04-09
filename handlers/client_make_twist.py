from aiogram import types, Dispatcher
from create_bot import bot, AcceptState
from aiogram.dispatcher import FSMContext
from keyboards import (keyboard_type_wire_pv, keyboard_yes_no, keyboard_color_pv, keyboard_metr_pv,
                       keyboard_create_defect, keyboard_print, keyboard_count_twist, keyboard_count_round,
                       keyboard_sec_round_vvg, keyboard_type_wire)
from get_qr import (get_operation_id, get_date_now, generate_qr_code, get_data_to_db_operation, write_to_db_operation,
                    create_data_to_write_in_qr, find_user_descript, get_id_twinse)
from qr_scaner import read_qr_code_async
import os.path
import os
from async_funck import send_qr_code, check_color, check_wire
from sqlite import Database

db = Database()

async def stop_make_twist(user_id):
    await bot.send_message(user_id, 'Выберите количество жил:', reply_markup=keyboard_count_twist)
    await AcceptState.wire_pv.set()


async def handle_photos_and_documents_id(file_id: str, message: types.Message, state: FSMContext):
    # сохраняем фотографию на диск
    file_path = await bot.get_file(file_id)
    file_name = file_path.file_path.split('/')[-1]
    await bot.download_file(file_path.file_path, os.path.join(os.getcwd(), 'photos', file_name))

    text = await read_qr_code_async(file_name)
    text = text.split('\n')

    if text[0] == 'Изготовлено: ПУВ':
        return text
    else:
        await bot.send_message(message.from_user.id, 'ошибка - завершаю скрипт')
        await state.finish()


async def make_twist_start(message: types.Message):
    await message.answer('Выберите количество жил:', reply_markup=keyboard_count_twist)
    await AcceptState.section_twist_pv.set()


async def process_section_twiste(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await stop_make_twist(user_id)
    else:
        sec_twiste = callback_query.data
        await state.update_data(sec_twiste=sec_twiste)
        await bot.send_message(user_id, 'Выберите сечение:', reply_markup=keyboard_sec_round_vvg)
        await AcceptState.section_vein_twiste.set()


async def process_twist_vein(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await state.update_data(twist_vein=callback_query.data)
    await bot.send_message(user_id, 'Выбирите сечение, которое будет участвовать в проверке:',
                           reply_markup=keyboard_type_wire)
    await AcceptState.section_vein_twiste_check.set()


async def process_twist_vein_check(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await state.update_data(twist_vein_check=callback_query.data)
    await bot.send_message(user_id, 'Укажите метраж:')
    await AcceptState.section_metr_twiste_pv.set()


async def process_metr_twiste(message: types.Message, state: FSMContext):
    metr = message.text
    await state.update_data(metr=metr)
    data = await state.get_data()
    count_pieces = data["sec_twiste"]
    if count_pieces == '1':
        await bot.send_message(message.from_user.id, f'Отправьте мне фото QR-кода заготовки.')
        await AcceptState.photo_twiste.set()
    else:
        await bot.send_message(message.from_user.id,
                               f'Вам необходимо будет отправить мне подряд {count_pieces} фото QR-кодов.\n\nФото 1:')
        await AcceptState.photo_twiste_1.set()


async def process_photo_twiste_1(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        info = await handle_photos_and_documents_id(file_id, message, state)
        ID = info[-3].replace("ID: ", "")
        color = info[2].replace('Цвет: ', '')
        wire = info[1].replace('Проволка: ', '')
        await state.update_data(piece_1=ID)
        await state.update_data(old_color_1=color)
        await state.update_data(old_wire_1=wire)
        data = await state.get_data()

        if check_wire(data["old_wire_1"], data["twist_vein_check"]):
            await bot.send_message(message.from_user.id, 'Фото 2:')
            await AcceptState.photo_twiste_2.set()
        else:
            await bot.send_message(message.from_user.id, 'Вы отправили код с некоректным QR-кодом (значение проволка и '
                                                         'вена должны отличаться')
            await AcceptState.photo_twiste_1.set()
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_twiste_1.set()


async def process_photo_twiste_2(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        info = await handle_photos_and_documents_id(file_id, message, state)
        ID = info[-3].replace("ID: ", "")
        color = info[2].replace('Цвет: ', '')
        wire = info[1].replace('Проволка: ', '')
        await state.update_data(piece_2=ID)
        await state.update_data(old_color_2=color)
        await state.update_data(old_wire_2=wire)
        data = await state.get_data()

        if check_wire(data["old_wire_1"], data["old_wire_2"], data["twist_vein_check"]) and check_color(
                data["old_color_1"],
                data["old_color_2"]):
            if int(data['sec_twiste']) == 2:
                new_text = f'Изготовить скрутку {data["sec_twiste"]}х{data["twist_vein"]} - ' \
                           f'{info[1].replace("Проволка: ", "")} - ' \
                           f'{data["metr"]}м - ID заготовок:  {data["piece_1"]}; {data["piece_2"]} верно?'
                await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)

                await AcceptState.yes_twiste.set()
            else:
                await bot.send_message(message.from_user.id, 'Фото 3:')
                await AcceptState.photo_twiste_3.set()
        else:
            await bot.send_message(message.from_user.id, 'Вы отправили код с некоректным QR-кодом (значение проволка и '
                                                         'вена должны отличаться) или вы отправили кода с одинаковыми '
                                                         'цветами (цвета должны отличаться)')
            await AcceptState.photo_twiste_2.set()
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_twiste_2.set()


async def process_photo_twiste_3(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        info = await handle_photos_and_documents_id(file_id, message, state)
        ID = info[-3].replace("ID: ", "")
        color = info[2].replace('Цвет: ', '')
        wire = info[1].replace('Проволка: ', '')
        await state.update_data(piece_3=ID)
        await state.update_data(old_color_3=color)
        await state.update_data(old_wire_3=wire)
        data = await state.get_data()

        if check_wire(data["old_wire_1"], data["old_wire_2"], data["old_wire_3"],
                      data["twist_vein_check"]) and check_color(
            data["old_color_1"], data["old_color_2"], data["old_color_3"]):

            if int(data['sec_twiste']) == 3:
                new_text = f'Изготовить скрутку {data["sec_twiste"]}х{data["twist_vein"]} - ' \
                           f'{info[1].replace("Проволка: ", "")} - ' \
                           f'{data["metr"]}м - ID заготовок:  {data["piece_1"]}; {data["piece_2"]} верно?'
                await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)

                await AcceptState.yes_twiste.set()
            else:
                await bot.send_message(message.from_user.id, 'Фото 4:')
                await AcceptState.photo_twiste_4.set()
        else:
            await bot.send_message(message.from_user.id, 'Вы отправили код с некоректным QR-кодом (значение проволка и '
                                                         'вена должны отличаться) или вы отправили кода с одинаковыми '
                                                         'цветами (цвета должны отличаться)')
            await AcceptState.photo_twiste_3.set()
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_twiste_3.set()


async def process_photo_twiste_4(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        info = await handle_photos_and_documents_id(file_id, message, state)
        ID = info[-3].replace("ID: ", "")
        color = info[2].replace('Цвет: ', '')
        wire = info[1].replace('Проволка: ', '')
        await state.update_data(piece_4=ID)
        await state.update_data(old_color_4=color)
        await state.update_data(old_wire_4=wire)
        data = await state.get_data()

        if check_wire(data["old_wire_1"], data["old_wire_2"], data["old_wire_3"], data["old_wire_4"],
                      data["twist_vein_check"]) and check_color(data["old_color_1"], data["old_color_2"],
                                                                data["old_color_3"], data["old_color_4"]):
            if int(data['sec_twiste']) == 4:
                new_text = f'Изготовить скрутку {data["sec_twiste"]}х{data["twist_vein"]} - ' \
                           f'{info[1].replace("Проволка: ", "")} - ' \
                           f'{data["metr"]}м - ID заготовок:  {data["piece_1"]}; {data["piece_2"]} верно?'
                await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)

                await AcceptState.yes_twiste.set()
            else:
                await bot.send_message(message.from_user.id, 'Фото 5:')
                await AcceptState.photo_twiste_5.set()
        else:
            await bot.send_message(message.from_user.id, 'Вы отправили код с некоректным QR-кодом (значение проволка и '
                                                         'вена должны отличаться) или вы отправили кода с одинаковыми '
                                                         'цветами (цвета должны отличаться)')
            await AcceptState.photo_twiste_4.set()
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_twiste_4.set()


async def process_photo_twiste_5(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        info = await handle_photos_and_documents_id(file_id, message, state)
        ID = info[-3].replace("ID: ", "")
        color = info[2].replace('Цвет: ', '')
        wire = info[1].replace('Проволка: ', '')
        await state.update_data(piece_5=ID)
        await state.update_data(old_color_5=color)
        await state.update_data(old_wire_5=wire)
        data = await state.get_data()

        if check_wire(data["old_wire_1"], data["old_wire_2"], data["old_wire_3"], data["old_wire_4"],
                      data["old_wire_5"], data["twist_vein_check"]) and check_color(data["old_color_1"],
                                                                                    data["old_color_2"],
                                                                                    data["old_color_3"],
                                                                                    data["old_color_4"],
                                                                                    data["old_color_5"]):
            if int(data['sec_twiste']) == 5:
                new_text = f'Изготовить скрутку {data["sec_twiste"]}х{data["twist_vein"]} - ' \
                           f'{info[1].replace("Проволка: ", "")} - ' \
                           f'{data["metr"]}м - ID заготовок:  {data["piece_1"]}; {data["piece_2"]} верно?'
                await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)
                await AcceptState.yes_twiste.set()
            else:
                await state.finish()
        else:
            await bot.send_message(message.from_user.id, 'Вы отправили код с некоректным QR-кодом (значение проволка и '
                                                         'вена должны отличаться) или вы отправили кода с одинаковыми '
                                                         'цветами (цвета должны отличаться)')
            await AcceptState.photo_twiste_5.set()
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_twiste_5.set()


async def firs_yes_twiste(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'ДА':
        await bot.answer_callback_query(callback_query.id, text=f"ДА!")
        await bot.send_message(user_id, 'Укажите результат работы', reply_markup=keyboard_create_defect)
        await AcceptState.result_metr_twist.set()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await stop_make_twist(user_id)


async def create_twiste(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Изготовлено':
        await bot.send_message(user_id, 'Укажите метраж:')
        await AcceptState.result_create_metr_twist.set()
    elif callback_query.data == 'Брак':
        await bot.send_message(user_id, 'Укажите количество брака в метрах:')
        await AcceptState.defect_metr_twist.set()
    elif callback_query.data == 'Авария':
        await bot.send_message(user_id, 'Функционал под аварию')
        await state.finish()


async def process_create_metr_twist(message: types.Message, state: FSMContext):
    metr = message.text
    await state.update_data(metr=metr)
    data = await state.get_data()

    if int(data['sec_twiste']) == 2:
        text = f'Скрутка {data["sec_twiste"]}х{data["twist_vein"]} - ' \
               f'{data["old_wire_1"]} - ID:  {data["piece_1"]}; {data["piece_2"]} - {data["metr"]}м'
    elif int(data['sec_twiste']) == 3:
        text = f'Скрутка {data["sec_twiste"]}х{data["twist_vein"]} - ' \
               f'{data["old_wire_1"]} - ID:  {data["piece_1"]}; {data["piece_2"]}; {data["piece_3"]} - {data["metr"]}м'
    elif int(data['sec_twiste']) == 4:
        text = f'Скрутка {data["sec_twiste"]}х{data["twist_vein"]} - ' \
               f'{data["old_wire_1"]} - ID:  {data["piece_1"]}; {data["piece_2"]}; {data["piece_3"]}; {data["piece_4"]} ' \
               f'- {data["metr"]}м'
    elif int(data['sec_twiste']) == 5:
        text = f'Скрутка {data["sec_twiste"]}х{data["twist_vein"]} - ' \
               f'{data["old_wire_1"]} - ID:  {data["piece_1"]}; {data["piece_2"]}; {data["piece_3"]}; ' \
               f'{data["piece_4"]}; {data["piece_5"]} - {data["metr"]}м'
    else:
        text = ''

    await bot.send_message(message.from_user.id, text)
    await bot.send_message(message.from_user.id, 'Верно?', reply_markup=keyboard_yes_no)
    await AcceptState.second_yes_twist.set()


async def second_yes_twist(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'ДА':
        await bot.answer_callback_query(callback_query.id, text=f"ДА!")
        data = await state.get_data()

        if int(data['sec_twiste']) == 2:
            text = f'Скрутка {data["sec_twiste"]}х{data["twist_vein"]} - ' \
                   f'{data["old_wire_1"]} - ID:  {data["piece_1"]}; {data["piece_2"]} - {data["metr"]}м'
        elif int(data['sec_twiste']) == 3:
            text = f'Скрутка {data["sec_twiste"]}х{data["twist_vein"]} - ' \
                   f'{data["old_wire_1"]} - ID:  {data["piece_1"]}; {data["piece_2"]}; {data["piece_3"]} - {data["metr"]}м'
        elif int(data['sec_twiste']) == 4:
            text = f'Скрутка {data["sec_twiste"]}х{data["twist_vein"]} - ' \
                   f'{data["old_wire_1"]} - ID:  {data["piece_1"]}; {data["piece_2"]}; {data["piece_3"]}; {data["piece_4"]} ' \
                   f'- {data["metr"]}м'
        elif int(data['sec_twiste']) == 5:
            text = f'Скрутка {data["sec_twiste"]}х{data["twist_vein"]} - ' \
                   f'{data["old_wire_1"]} - ID:  {data["piece_1"]}; {data["piece_2"]}; {data["piece_3"]}; ' \
                   f'{data["piece_4"]}; {data["piece_5"]} - {data["metr"]}м'
        else:
            text = ''

        await bot.send_message(user_id, text, reply_markup=keyboard_print)
        await AcceptState.print_create_twist.set()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await stop_make_twist(user_id)


async def print_command_1(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await state.update_data(type_product='изготовить Скрутка')
    await state.update_data(user_id=str(user_id))
    await state.update_data(user_descript=find_user_descript(str(user_id)))
    await state.update_data(date_now=get_date_now())
    await state.update_data(id=get_id_twinse())
    data = await state.get_data()
    name_twin = f'{data["sec_twiste"]}x{data["twist_vein"]}'
    await state.update_data(name_twin=name_twin)
    data = await state.get_data()

    db.add_operation_twinse(ID=data['id'], Name_twinse=name_twin, Wire=data["twist_vein_check"],
                            Metr=data["metr"], Date=get_date_now(), Operator_id=data["user_id"],
                            Operator_name=data["user_descript"], Section=data["sec_twiste"], Piece_1=data["piece_1"],
                            Piece_2=data["piece_2"], Piece_3=data.get("piece_3", ""), Piece_4=data.get("piece_4", ""),
                            Piece_5=data.get("piece_5", ""))

    data_dict = create_data_to_write_in_qr(data)
    data_send = generate_qr_code(data_dict)
    await send_qr_code(data['user_id'], data_send)
    await state.finish()


def register_handlers_client_make_twist(dp: Dispatcher):
    dp.register_message_handler(make_twist_start, commands=['twist_workpiece'])
    dp.register_callback_query_handler(process_section_twiste, state=AcceptState.section_twist_pv)
    dp.register_callback_query_handler(process_twist_vein, state=AcceptState.section_vein_twiste)
    dp.register_callback_query_handler(process_twist_vein_check, state=AcceptState.section_vein_twiste_check)
    dp.register_message_handler(process_metr_twiste, state=AcceptState.section_metr_twiste_pv)
    dp.register_message_handler(process_photo_twiste_1, content_types=['photo', 'document'],
                                state=AcceptState.photo_twiste_1)
    dp.register_message_handler(process_photo_twiste_2, content_types=['photo', 'document'],
                                state=AcceptState.photo_twiste_2)
    dp.register_message_handler(process_photo_twiste_3, content_types=['photo', 'document'],
                                state=AcceptState.photo_twiste_3)
    dp.register_message_handler(process_photo_twiste_4, content_types=['photo', 'document'],
                                state=AcceptState.photo_twiste_4)
    dp.register_message_handler(process_photo_twiste_5, content_types=['photo', 'document'],
                                state=AcceptState.photo_twiste_5)
    dp.register_callback_query_handler(firs_yes_twiste, state=AcceptState.yes_twiste)
    dp.register_callback_query_handler(create_twiste, state=AcceptState.result_metr_twist)
    dp.register_message_handler(process_create_metr_twist, state=AcceptState.result_create_metr_twist)
    dp.register_callback_query_handler(second_yes_twist, state=AcceptState.second_yes_twist)
    dp.register_callback_query_handler(print_command_1, state=AcceptState.print_create_twist)
