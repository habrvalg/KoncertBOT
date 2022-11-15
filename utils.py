from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styledpil import StyledPilImage
from telebot import types
import qrcode


def create_keyboard(lines):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for line in lines:
        if len(line) > 1:
            keyboard.add(types.KeyboardButton(line[0]), types.KeyboardButton(line[1]))
        else:
            keyboard.add(types.KeyboardButton(line[0]))
    return keyboard


def get_qr_code(base, user_info: str, event_info: str):
    new_path = f'qrs/{user_info}_{event_info}.jpg'
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, border=4, box_size=25)
    qr.add_data(f'{user_info}_{event_info}')
    img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer(radius_ratio=1))
    img.save(new_path)
    base.add_ticket(user_info, event_info, new_path)

    with open(new_path, 'rb') as file:
        return file.read()
