import asyncio
import cv2
import os
import pyzbar.pyzbar as pyzbar


async def read_qr_code_async(filename):
    dir_path = os.getcwd()
    file_name = filename

    def get_text(decoded_image):
        decoded_objects = pyzbar.decode(decoded_image)
        texts = [obj.data.decode('utf8') for obj in decoded_objects]
        try:
            return texts[0]
        except IndexError:
            return ""

    image = cv2.imread(os.path.join(dir_path, 'photos', file_name))
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_text, image)