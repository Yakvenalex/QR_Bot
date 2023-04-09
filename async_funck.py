import os.path
import os
import aiofiles
import aiofiles.os
from smb.SMBConnection import SMBConnection
from io import BytesIO
from create_bot import bot
from PIL import Image, ImageDraw, ImageFont


def generate_qr_code_image(qr_code_path, text):
    # Load QR code image
    qr_code = Image.open(qr_code_path)

    # Create new image with white background
    new_image = Image.new('RGB', (1000, 1000), color='white')

    # Resize QR code to fit in new image
    new_width = 450
    new_height = 450
    qr_code_resized = qr_code.resize((new_width, new_height))

    # Paste QR code in top center of new image
    x_offset = int((new_image.width - qr_code_resized.width) / 2)
    y_offset = -30  # shift up by 10 pixels
    new_image.paste(qr_code_resized, (x_offset, y_offset))

    # Add text below QR code
    draw = ImageDraw.Draw(new_image)
    font_size = 40  # decrease by 20 pixels
    font = ImageFont.truetype('arialbd.ttf', size=font_size)  # load bold font
    text_lines = text.split('\n')
    y_offset += qr_code_resized.height + 10
    for line in text_lines:
        line_bbox = draw.textbbox((0, 0), line, font=font)
        x_offset = int((new_image.width - line_bbox[2]) / 2)
        draw.text((x_offset, y_offset), line, font=font, fill='black')
        y_offset += line_bbox[3] - line_bbox[1] + int(font_size / 2)

    # Save new image as PNG
    new_image.save("qr_codes/" + qr_code_path.split("/")[-1].split(".")[0] + ".png", format='PNG')


async def save_to_server_async(username, password, server_name, server_ip, file_path):
    filename = os.path.basename(file_path)
    conn = SMBConnection(username, password, "", server_name)
    conn.connect(server_ip)
    async with aiofiles.open(file_path, mode='rb') as file:
        contents = await file.read()
        f = BytesIO(contents)
        conn.storeFile('QR', filename, f)
    conn.close()
    print(f'{filename} успешно сохранено на сервере в папке QR')


async def save_qr_in_QR(putch):
    username = "Print"
    password = "P~e7|4V|*Q"
    server_name = "Server"
    server_ip = "192.168.1.199"
    await save_to_server_async(username, password, server_name, server_ip, putch)


async def send_qr_code(user_id, data_send):
    with open(data_send[1], 'rb') as qr:
        await bot.send_photo(user_id, qr, caption=data_send[0])
    generate_qr_code_image(data_send[1], data_send[0])
    await save_qr_in_QR(data_send[1])


def check_color(*args):
    return len(args) == len(set(args))


def check_wire(*args):
    return all(val == args[0] for val in args)
