import os
import asyncio
import subprocess
from PIL import Image
from io import BytesIO
from smb.SMBConnection import SMBConnection


async def print_photo(image_path, printer_name="LPG4"):
    try:
        # Запустить печать
        subprocess.run(["lp", "-d", printer_name, image_path], check=True)
        print(f"Photo {image_path} has been sent to printer {printer_name}.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


async def monitor_folder(share_name, username, password, server_name, server_ip):
    conn = SMBConnection(username, password, server_name, server_name, use_ntlm_v2=True)
    conn.connect(server_ip)

    print(f"Мониторю папку {share_name}")
    while True:
        files = conn.listPath(share_name, '/')
        for file in files:
            if os.path.splitext(file.filename)[1] == '.png':
                print(f"Появилось фото - {file.filename}")
                with BytesIO() as file_obj:
                    conn.retrieveFile(share_name, f'/{file.filename}', file_obj)
                    file_obj.seek(0)
                    img = Image.open(file_obj)
                    img.save(f'{file.filename}')
                await print_photo(file.filename)
                conn.deleteFiles(share_name, f'/{file.filename}')
                print(f"Фото {file.filename} удалено")
        await asyncio.sleep(3)


async def main():
    share_name = 'QR'
    username = "Print"
    password = "P~e7|4V|*Q"
    server_name = "Server"
    server_ip = "192.168.1.199"

    await monitor_folder(share_name, username, password, server_name, server_ip)


if __name__ == '__main__':
    asyncio.run(main())
