from aiogram.utils import executor
from create_bot import dp, bot
from handlers import client_plasticat, client_wire, client_main, qr_cod_scaner, admin, other_type, client_make_pv, \
    client_make_vvg


async def on_startup(_):
    print('Бот вышел в онлайн')

client_plasticat.register_handlers_client_plasticat(dp)
client_wire.register_handlers_client_wire(dp)
client_main.register_handlers_client_main(dp)
qr_cod_scaner.register_handlers_qr_cod_scaner(dp)
other_type.register_handlers_client_other(dp)
client_make_pv.register_handlers_client_make_pv(dp)
client_make_vvg.register_handlers_client_make_vvg(dp)
# admin.register_handlers_admin(dp)
# other.register_handlers_other(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
