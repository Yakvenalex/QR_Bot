from aiogram import types, Dispatcher
from create_bot import bot, AcceptState
from aiogram.dispatcher import FSMContext
from keyboards import (keyboard_type_wire_pv_list, keyboard_type_wire_pv, keyboard_yes_no, keyboard_type_yes_no_list,
                       keyboard_color_pv, keyboard_color_pv_list, keyboard_metr_pv, keyboard_metr_pv_list,
                       keyboard_create_defect, keyboard_create_defect_list, keyboard_print, keyboard_print_list)
from get_qr import (get_operation_id, get_date_now, generate_qr_code, get_data_to_db_operation, write_to_db_operation,
                    create_data_to_write_in_qr, create_data_to_send, find_user_descript)
from qr_scaner import read_qr_code_async
import os


async def make_pv_start(message: types.Message):
    await message.answer('Выберите из списка проволоки по ролевантности:', reply_markup=keyboard_type_wire_pv)
    await AcceptState.wire_pv.set()


async def stop_make_pv(user_id):
    await bot.send_message(user_id, 'Выберите из списка проволоки по ролевантности:',
                           reply_markup=keyboard_type_wire_pv)
    await AcceptState.wire_pv.set()


async def send_qr_code(user_id, data_send):
    with open(data_send[1], 'rb') as qr:
        await bot.send_photo(user_id, qr, caption=data_send[0])


async def handle_photos_and_documents_id(file_id: str, metr: str, wire: str, color: str, message: types.Message,
                                         state: FSMContext):
    # сохраняем фотографию на диск
    file_path = await bot.get_file(file_id)
    file_name = file_path.file_path.split('/')[-1]
    await bot.download_file(file_path.file_path, os.path.join(os.getcwd(), 'photos', file_name))

    # получаем текст из QR кода
    text = await read_qr_code_async(file_name)
    text = text.split('\n')

    wire_new = text[0].replace("Проволка: ", "")
    ID_new = text[-2].replace("ID: ", "")
    metr_new = text[2].replace("Метраж: ", "").replace(" м", "")

    if wire_new == wire:
        if metr == 'Весь':
            r_str = f'Изготовить ПУВ {wire_new} {color} {metr_new}м- заготовка ID {ID_new} верно?'
            await bot.send_message(message.from_user.id, r_str, reply_markup=keyboard_yes_no)
            await AcceptState.first_yes_pv.set()
            return ID_new
        else:
            try:
                int_metr = int(metr)
                int_metr_new = int(metr_new)
                if int_metr <= int_metr_new:
                    r_str = f'Изготовить ПУВ {wire_new} {color} {int_metr}м- заготовка ID {ID_new} верно?'
                    await bot.send_message(message.from_user.id, r_str, reply_markup=keyboard_yes_no)
                    await AcceptState.first_yes_pv.set()
                    return ID_new
                else:
                    r_str = f'Ваше значение метров больше чем доступно по QR коду'
                    await bot.send_message(message.from_user.id, r_str)
                    await state.finish()
                    return 'нет'
            except:
                r_str = 'Ошибка: неверный формат метров!'
                await bot.send_message(message.from_user.id, r_str)
                await state.finish()
                return 'нет'
    else:
        r_str = 'Ошибка: неверный QR-код. Пожалуйста, отсканируйте другой код!'
        await bot.send_message(message.from_user.id, r_str)
        await state.finish()
        return 'нет'


async def process_wire_pv(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Другой тип проволоки':
        await bot.send_message(user_id, 'Введите тип проволоки:')
        await AcceptState.waiting_for_color_pv.set()
    else:
        wire = callback_query.data
        await state.update_data(wire=wire)
        await bot.send_message(user_id, 'Выберите цвет:', reply_markup=keyboard_color_pv)
        await AcceptState.color_pv.set()


async def process_wire_input_pv(message: types.Message, state: FSMContext):
    wire = message.text
    await state.update_data(wire=wire)
    await bot.send_message(message.from_user.id, 'Выберите цвет:', reply_markup=keyboard_color_pv)
    await AcceptState.color_pv.set()


async def process_color_pv(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await stop_make_pv(user_id)
    else:
        color = callback_query.data
        await state.update_data(color=color)
        await bot.send_message(user_id, 'Укажите метраж:', reply_markup=keyboard_metr_pv)
        await AcceptState.metr_pv.set()


async def process_metr_pv(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Указать':
        await bot.send_message(callback_query.from_user.id, 'Введите метраж:')
        await AcceptState.waiting_for_metr_pv.set()
    elif callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await stop_make_pv(user_id)
    elif callback_query.data == 'Назад':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на шаг назад")
        await bot.send_message(user_id, 'Выберите цвет:', reply_markup=keyboard_color_pv)
        await AcceptState.color_pv.set()
    else:
        metr = callback_query.data
        await state.update_data(metr=metr)
        await bot.send_message(user_id, 'Сфотографируйте QR-код и отправьте мне')
        await AcceptState.photo_pv.set()


async def process_metr_input_pv(message: types.Message, state: FSMContext):
    metr = message.text
    await state.update_data(metr=metr)
    await bot.send_message(message.from_user.id, 'Сфотографируйте QR-код и отправьте мне')
    await AcceptState.photo_pv.set()


async def process_photo_pv(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        # await state.update_data(photo=message.photo[-1].file_id if message.photo else message.document)
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        data = await state.get_data()
        ID_NEW = await handle_photos_and_documents_id(file_id, data['metr'], data['wire'], data['color'], message,
                                                      state)
        await state.update_data(id_new=ID_NEW)
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_pv.set()


async def firs_yes_pv(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'ДА':
        await bot.answer_callback_query(callback_query.id, text=f"ДА!")
        await bot.send_message(user_id, 'Укажите результат работы', reply_markup=keyboard_create_defect)
        await AcceptState.result_create.set()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await stop_make_pv(user_id)


async def create_pv(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Изготовлено':
        await bot.send_message(user_id, 'Укажите метраж:')
        await AcceptState.result_create_metr.set()
    elif callback_query.data == 'Брак':
        await bot.send_message(user_id, 'Укажите количество брака в метрах:')
        await AcceptState.defect_metr.set()
    elif callback_query.data == 'Авария':
        await bot.send_message(user_id, 'Функционал под аварию')


async def process_defect_metr(message: types.Message, state: FSMContext):
    metr = message.text
    await state.update_data(metr=metr)
    await bot.send_message(message.from_user.id, 'Укажите причину брака:')
    await AcceptState.defect_reason.set()


async def process_defect_reason(message: types.Message, state: FSMContext):
    defect_reason = message.text
    await state.update_data(defect_reason=defect_reason)
    data = await state.get_data()
    text = f'БРАК ПУВ {data["wire"]} {data["color"]} - заготовка ID {data["id_new"]} верно ?'
    await bot.send_message(message.from_user.id, text, reply_markup=keyboard_yes_no)
    await AcceptState.defect_yes_no.set()


async def defect_yes_no(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'ДА':
        await bot.answer_callback_query(callback_query.id, text=f"ДА!")
        data = await state.get_data()
        await state.update_data(id=get_operation_id(data["id_new"]))
        text = f'БРАК ПУВ {data["wire"]} {data["color"]} - {data["metr"]}м - ID {get_operation_id(data["id_new"])} {get_date_now()}'
        await bot.send_message(user_id, text, reply_markup=keyboard_print)
        await AcceptState.print_2.set()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await stop_make_pv(user_id)


async def print_defect(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await state.update_data(type_product='брак ПУВ')
    await state.update_data(user_id=str(user_id))
    await state.update_data(user_descript=find_user_descript(str(user_id)))
    await state.update_data(date_now=get_date_now())
    data = await state.get_data()
    data_db = get_data_to_db_operation(data)
    write_to_db_operation(data_db)
    data_dict = create_data_to_write_in_qr(data)
    data_send = generate_qr_code(data_dict)
    await send_qr_code(data['user_id'], data_send)
    await state.finish()


async def process_create_metr(message: types.Message, state: FSMContext):
    metr = message.text
    await state.update_data(metr=metr)
    data = await state.get_data()
    text = f'Изготовлено ПУВ {data["wire"]} {data["color"]} - {data["metr"]}м - ID {data["id_new"]}'
    await bot.send_message(message.from_user.id, text)
    await bot.send_message(message.from_user.id, 'Верно?', reply_markup=keyboard_yes_no)
    await AcceptState.second_yes_pv.set()


async def second_yes_pv(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'ДА':
        await bot.answer_callback_query(callback_query.id, text=f"ДА!")
        data = await state.get_data()
        await state.update_data(id=get_operation_id(data["id_new"]))
        text = f'Изготовлено ПУВ {data["wire"]} {data["color"]} - {data["metr"]}м - ID {get_operation_id(data["id_new"])} {get_date_now()}'
        await bot.send_message(user_id, text, reply_markup=keyboard_print)
        await AcceptState.print_1.set()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await stop_make_pv(user_id)


async def print_command_1(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await state.update_data(type_product='изготовить ПУВ')
    await state.update_data(user_id=str(user_id))
    await state.update_data(user_descript=find_user_descript(str(user_id)))
    await state.update_data(date_now=get_date_now())
    data = await state.get_data()
    data_db = get_data_to_db_operation(data)
    write_to_db_operation(data_db)
    data_dict = create_data_to_write_in_qr(data)
    data_send = generate_qr_code(data_dict)
    await send_qr_code(data['user_id'], data_send)
    await state.finish()


def register_handlers_client_make_pv(dp: Dispatcher):
    dp.register_message_handler(make_pv_start, commands=['make_pv'])
    dp.register_callback_query_handler(process_wire_pv,
                                       lambda callback_query: callback_query.data in keyboard_type_wire_pv_list,
                                       state=AcceptState.wire_pv)
    dp.register_message_handler(process_wire_input_pv, state=AcceptState.waiting_for_color_pv)
    dp.register_callback_query_handler(process_color_pv,
                                       lambda callback_query: callback_query.data in keyboard_color_pv_list,
                                       state=AcceptState.color_pv)
    dp.register_callback_query_handler(process_metr_pv,
                                       lambda callback_query: callback_query.data in keyboard_metr_pv_list,
                                       state=AcceptState.metr_pv)
    dp.register_message_handler(process_metr_input_pv, state=AcceptState.waiting_for_metr_pv)
    dp.register_message_handler(process_photo_pv, content_types=['photo', 'document'], state=AcceptState.photo_pv)
    dp.register_callback_query_handler(firs_yes_pv, lambda callback_query: callback_query.data in
                                                                           keyboard_type_yes_no_list,
                                       state=AcceptState.first_yes_pv)
    dp.register_callback_query_handler(create_pv, lambda callback_query: callback_query.data in
                                                                         keyboard_create_defect_list,
                                       state=AcceptState.result_create)
    dp.register_message_handler(process_create_metr, state=AcceptState.result_create_metr)
    dp.register_callback_query_handler(second_yes_pv, lambda callback_query: callback_query.data in
                                                                             keyboard_type_yes_no_list,
                                       state=AcceptState.second_yes_pv)
    dp.register_callback_query_handler(print_command_1, lambda callback_query: callback_query.data in
                                                                               keyboard_print_list,
                                       state=AcceptState.print_1)
    dp.register_message_handler(process_defect_metr, state=AcceptState.defect_metr)
    dp.register_message_handler(process_defect_reason, state=AcceptState.defect_reason)
    dp.register_callback_query_handler(defect_yes_no, lambda callback_query: callback_query.data in
                                                                             keyboard_type_yes_no_list,
                                       state=AcceptState.defect_yes_no)
    dp.register_callback_query_handler(print_defect, lambda callback_query: callback_query.data in
                                                                            keyboard_print_list,
                                       state=AcceptState.print_2)
