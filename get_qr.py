import qrcode
from datetime import datetime
from sqlite import Database

db = Database()


def increment_max_number(numbers_list=[]):
    if not numbers_list:
        return "AA00000001"

    max_number = max(numbers_list)
    prefix, suffix = max_number[:2], max_number[2:]
    incremented_suffix = str(int(suffix) + 1).zfill(len(suffix))
    return "{}{}".format(prefix, incremented_suffix)


def get_date_now():
    now = datetime.now()
    formatted_date = now.strftime("%d.%m.%y %H:%M")
    return formatted_date


def generate_qr_code(data_dict):
    data_string = ""
    for key, value in data_dict.items():
        data_string += f"{key}: {value}\n"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data_string.encode('utf-8'), optimize=0)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    patch = f"qr_codes/qr_code_{data_dict['ID'].replace('/', '_')}.png"
    qr_image.save(patch)
    return (data_string, patch)


def get_data_to_db(data):
    data_db = {}
    data_db['id'] = data.get('id', '')
    data_db['type_product'] = data.get('type_product', '')
    data_db['supplier'] = data.get('supplier', '')
    data_db['manufacturer'] = data.get('manufacturer', '')
    data_db['date_now'] = data.get('date_now', '')
    data_db['wire'] = data.get('wire', '')
    data_db['plasticat'] = data.get('plasticat', '')
    data_db['volume'] = data.get('volume', '')
    data_db['metr'] = data.get('metr', '')
    data_db['drawing'] = data.get('drawing', '')
    return data_db


def get_data_to_db_operation(data):
    data_db = {}
    data_db['id'] = data.get('id', '')
    data_db['type_product'] = data.get('type_product', '')
    data_db['color'] = data.get('color', '')
    data_db['user_id'] = data.get('user_id', '')
    data_db['user_descript'] = data.get('user_descript', '')
    data_db['date_now'] = data.get('date_now', '')
    data_db['wire'] = data.get('wire', '')
    data_db['metr'] = data.get('metr', '')
    data_db['defect_reason'] = data.get('defect_reason', '')
    return data_db



def write_to_db_operation(data_to_db):
    id = data_to_db['id']
    type_product = data_to_db['type_product']
    date_now = data_to_db['date_now']
    wire = data_to_db['wire']
    metr = data_to_db['metr']
    color = data_to_db['color']
    user_id = data_to_db['user_id']
    user_descript = data_to_db['user_descript']
    defect_reason = data_to_db['defect_reason']
    db.add_operation_puv(id, type_product, wire, color, date_now, user_id, user_descript, metr, defect_reason)




def create_data_to_write_in_qr(data):
    data_dict = {}
    if data['type_product'] == 'Проволока':
        data_dict = {
            "Проволка": data['wire'],
            "Количество": data['volume'] + " кг",
            "Метраж": data['metr'] + " м",
            "Поставщик": data['supplier'],
            "Волочение": data['drawing'],
            "Изготовитель": data['manufacturer'],
            "Дата": data['date_now'],
            "ID": data['id']
        }
        return data_dict
    elif data['type_product'] == 'Пластикат':
        data_dict = {
            "Пластикат": data['plasticat'],
            "Количество": data['volume'] + " кг",
            "Поставщик": data['supplier'],
            "Изготовитель": data['manufacturer'],
            "Дата": data['date_now'],
            "ID": data['id']
        }

    elif data['type_product'] == 'Другое':
        data_dict = {
            "Другое": data['enter_value'],
            "Количество": data['volume'] + " кг",
            "Поставщик": data['supplier'],
            "Изготовитель": data['manufacturer'],
            "Дата": data['date_now'],
            "ID": data['id']
        }

    elif data['type_product'] == 'изготовить ПУВ':
        data_dict = {
            "Изготовлено": "ПУВ",
            "Проволка": data['wire'],
            "Цвет": data['color'],
            "Метраж": data['metr'] + " м",
            "Дата": data['date_now'],
            "ID": data['id'],
            "Оператор": data['user_descript']
        }
    elif data['type_product'] == 'брак ПУВ':
        data_dict = {
            "Брак": "ПУВ",
            "Проволка": data['wire'],
            "Цвет": data['color'],
            "Метраж": data['metr'] + " м",
            "Дата": data['date_now'],
            "ID": data['id'],
            "Оператор": data['user_descript']
        }
    return data_dict


def write_to_db(data_to_db):
    id = data_to_db['id']
    type_product = data_to_db['type_product']
    supplier = data_to_db['supplier']
    manufacturer = data_to_db['manufacturer']
    date_now = data_to_db['date_now']
    wire = data_to_db['wire']
    plasticat = data_to_db['plasticat']
    volume = data_to_db['volume']
    metr = data_to_db['metr']
    drawing = data_to_db['drawing']
    if type_product != 'изготовить ПУВ':
        db.add_automate(id=id, type_product=type_product, wire=wire, plasticat=plasticat, volume=volume, metr=metr,
                        supplier=supplier, drawing=drawing, manufacturer=manufacturer, date_now=date_now)


def create_data_to_send(data):
    data_dict = {}
    if data['type_product'] == 'Проволока':
        data_dict = {
            "Проволка": data['wire'],
            "Количество": data['volume'] + " кг",
            "Метраж": data['metr'] + " м",
            "Поставщик": data['supplier'],
            "Волочение": data['drawing'],
            "Изготовитель": data['manufacturer'],
        }

    elif data['type_product'] == 'Пластикат':
        data_dict = {
            "Пластикат": data['plasticat'],
            "Количество": data['volume'] + " кг",
            "Поставщик": data['supplier'],
            "Изготовитель": data['manufacturer'],
        }

    elif data['type_product'] == 'Другое':
        data_dict = {
            "Другое": data['enter_value'],
            "Количество": data['volume'] + " кг",
            "Поставщик": data['supplier'],
            "Изготовитель": data['manufacturer'],
        }
    elif data['type_product'] == 'изготовить ПУВ':
        data_dict = {
            "Изготовлено": "ПУВ",
            "Проволка": data['wire'],
            "Цвет": data['color'],
            "Метраж": data['metr'] + " м",
            "Поставщик": data['supplier'],
            "Изготовитель": data['manufacturer'],
        }

    return data_dict


def get_id():
    list_id = []
    for i in db.select_all_products():
        list_id.append(i[0])
    id = increment_max_number(list_id)
    return id


def generate_new_qr_code(code, operations):
    # проверяем, были ли уже операции с этим кодом
    if not any(operation.startswith(code + '/') for operation in operations):
        # если нет, добавляем первую операцию
        return code + '/01'
    else:
        # если были, находим последнюю операцию и увеличиваем номер на 1
        last_operation = max([int(operation.split('/')[-1]) for operation in operations if operation.startswith(code + '/')])
        new_number = str(last_operation + 1).zfill(2)
        return code + '/' + new_number


def get_operation_id(old_code):
    list_id = []
    for i in db.select_all_operation():
        list_id.append(i[0])
    id = generate_new_qr_code(old_code, list_id)
    return id



def find_user_descript(user_id):
    if str(user_id) == '5127841744':
        user_descript = 'Яковенко Алексей'
    elif str(user_id) == '438083101':
        user_descript = 'Карэн'
    else:
        user_descript = 'Иванов Иван'
    return user_descript