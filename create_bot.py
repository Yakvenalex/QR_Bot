from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

class AcceptState(StatesGroup):
    date_now = State()
    id = State()
    type_product = State()

    supplier_plasticat = State()
    supplier_wire = State()

    manufacturer_plasticat = State()
    manufacturer_wire = State()
    wire = State()
    wire_pv = State()
    enter_value = State()
    waiting_for_plasticat = State()
    waiting_for_wire = State()
    waiting_for_drawing = State()
    check = State()
    plasticat = State()
    volume_plasticat = State()
    color_pv = State()
    waiting_for_color_pv = State()
    volume_wire = State()
    metr_wire = State()
    drawing = State()
    photo_pv = State()
    metr_pv = State()
    waiting_for_metr_pv = State()
    first_yes_pv = State()
    result_create = State()
    result_create_metr = State()
    second_yes_pv = State()
    print_1 = State()
    defect_metr = State()
    defect_reason = State()
    print_2 = State()
    defect_yes_no = State()
    count_pieces_vvg = State()
    section_vvg = State()
    metr_vvg = State()
    photo_vvg = State()
    type_vvg = State()
    photo_vvg_1 = State()
    photo_vvg_2 = State()
    photo_vvg_3 = State()
    photo_vvg_4 = State()
    photo_vvg_5 = State()
    yes_vvg_round = State()





storage = MemoryStorage()
TOKEN = '6144897027:AAEsE9Rzfz2a5KyezQu-n42YKNQm_qMf3wM'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
