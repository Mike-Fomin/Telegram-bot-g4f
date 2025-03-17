from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


######################### Choice menu keyboard #################################

choice_button1 = InlineKeyboardButton(
    text='Текст 📄',
    callback_data='get_text_button'
)
choice_button2 = InlineKeyboardButton(
    text='Изображение 🏞',
    callback_data='get_image_button'
)
choice_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[[choice_button1, choice_button2]]
)

######################### Text response keyboard ###############################

send_button = InlineKeyboardButton(
    text='Подтвердить ☑',
    callback_data='send_button'
)
send_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[[send_button]]
)

######################### Save response keyboard ###############################

save_button = InlineKeyboardButton(
    text='Сохранить 💾',
    callback_data='save_button'
)
save_response_kb = InlineKeyboardMarkup(
    inline_keyboard=[[save_button]]
)

######################### Text end part keyboard ###############################

send_text_to_chat_button = InlineKeyboardButton(
    text='Отправить в чат ✈',
    callback_data='send_to_chat_button'
)
get_image_button = InlineKeyboardButton(
    text='Сгенерировать изображение 🏞',
    callback_data='get_image_button'
)
get_text_button = InlineKeyboardButton(
    text='Сгенерировать текст 📄',
    callback_data='get_text_button'
)
cancel_button = InlineKeyboardButton(
    text='Отмена 🚫',
    callback_data='cancel_button'
)
end_part_kb_text = InlineKeyboardMarkup(
    inline_keyboard=[
        [send_text_to_chat_button, get_image_button],
        [cancel_button]
    ]
)
end_part_kb_image = InlineKeyboardMarkup(
    inline_keyboard=[
        [send_text_to_chat_button, get_text_button],
        [cancel_button]
    ]
)
end_part_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [send_text_to_chat_button],
        [cancel_button]
    ]
)
