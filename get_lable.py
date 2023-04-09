from PIL import Image, ImageDraw, ImageFont
import qrcode


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
    font_size = 40 # decrease by 20 pixels
    font = ImageFont.truetype('arialbd.ttf', size=font_size)  # load bold font
    text_lines = text.split('\n')
    y_offset += qr_code_resized.height + 10
    for line in text_lines:
        line_bbox = draw.textbbox((0, 0), line, font=font)
        x_offset = int((new_image.width - line_bbox[2]) / 2)
        draw.text((x_offset, y_offset), line, font=font, fill='black')
        y_offset += line_bbox[3] - line_bbox[1] + int(font_size/2)

    # Save new image as PNG
    new_image.save('output.png', format='PNG')


generate_qr_code_image('/home/alexey/PycharmAll/QR_Bot/qr_codes/qr_code_AA00000157_01.png',
             'Изготовлено: ПУВ\n'
             'Проволка: 2,67\n'
             'Цвет: красн.\n'
             'Метраж: 616 м\n'
             'Дата: 05.04.23 14:59\n'
             'ID: AA00000157/01\n'
             'Оператор: Яковенко Алексей\n'
             'ID1: AA00000157/01\n'
             'ID2: AA00000157/01\n'
             'ID3: AA00000157/01')