from aiogram import types

markup = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        types.KeyboardButton('\U00002712 записать расходы'),
        types.KeyboardButton('\U0000274c удалить расход')
    ],
    [
        types.KeyboardButton('\U0001F4CB Просмотр расходов'),
        types.KeyboardButton('\U0001F6AB ИТОГ'),
    ],
    [
        types.KeyboardButton('\U00002753 о боте'),
        types.KeyboardButton("Приход на баланс")
    ],
    [
        types.KeyboardButton('погода')
    ]
])

markup_info = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        types.KeyboardButton(text='menu'),
        types.KeyboardButton(text="/start")
    ]
])

markup_yes = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        types.KeyboardButton('/start'),
        types.KeyboardButton('\U00002753 о боте')
    ]
])

rate_markup = types.ReplyKeyboardMarkup(resize_keyboard=True ,keyboard=[
    [
        types.KeyboardButton(text='отмена'),

    ]
])

