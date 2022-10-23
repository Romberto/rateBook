import datetime
import json
import os
from keyboard.keyboard import markup, markup_info, markup_yes, rate_markup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from manager import get_list_refund, get_info_report, delete_row_in_file, append_row_in_file, pars_weather
from aiogram.utils import executor
from config import token
from aiogram import Bot, Dispatcher, types
import logging
from aiogram.utils.callback_data import CallbackData

logging.basicConfig(level=logging.INFO)

bot = Bot(token)

db = Dispatcher(bot, storage=MemoryStorage())


class RateForm(StatesGroup):
    name = State()
    price = State()


class PlusForm(StatesGroup):
    name = State()
    price = State()


COMMANDS = 'вот команды :\n/start - ' \
           'начать новый период \n или воспользуйтесь меню ниже'

callback_other = CallbackData('answer', 'action')
callback_refund_fab = CallbackData('refund', 'action')


@db.message_handler(text=['\U00002753 о боте'])
async def info_bot(message: types.Message):
    text_message = '*** информация о боте *** \n  Бот ведёт учёт расходов. Расчётный период начинается в момент ' \
                   'отправления сообщения "/start".\n  Кнопка "Просмотр расходов" показывает ' \
                   'предварительный отчёт.\n ' \
                   ' Для ' \
                   'добавления расходов в отчёт кнопка "Записать расходы" сначала отправляем найменование расходов, ' \
                   'потом сумму \n  Кнопка "удалить расход" ' \
                   'позволяет удалить статью расходов.\n  Если надо закрыть период и сформировать отчёт нажимаем на ' \
                   'кропку "ИТОГ". '

    await message.answer(text_message, reply_markup=markup_info)


@db.message_handler(text="menu")
async def menu(message):
    data_dict = {}
    data = [{str(datetime.date.today()): data_dict}]
    file_json = 'files/' + str(message.from_user.id) + '.json'
    if os.path.exists(file_json):
        await bot.send_message(message.chat.id, "Доступные команды", reply_markup=markup)
    else:
        mess = f"Привет {message.from_user.first_name} я бот который поможет автоматизировать отчёты по расходам"
        await bot.send_message(chat_id=message.chat.id, text=mess)
        with open(file_json, 'w') as file:
            json.dump(data, file)
        await bot.send_message(message.chat.id, 'расчетный период начинается с сегодняшнего дня \n'
                                                'вот команды :\n'
                                                '"ИТОГ"- формировать отчёт(закрыть период)\nкнопка "удалить расход"- '
                                                'возврат '
                                                '\n "Записать расходы" - добавить расходы',
                               reply_markup=markup)


@db.message_handler(commands=['start'])
async def start(message: types.Message):
    data_dict = {}
    data = [{str(datetime.date.today()): data_dict}]
    file_json = 'files/' + str(message.from_user.id) + '.json'
    if os.path.exists(file_json):
        mess = f"{message.from_user.first_name} если хотите начать новый период, сначала закройте прошлый " \
               f"расчётный период\n вот команды :\n" \
               f"'Записать расходы' - добавить расходы" \
               f" \nкнопка 'ИТОГ' - формировать отчёт(закрыть период)" \
               f"\nкнопка 'удалить расход'- возврат\nкнопка 'Просмотр расходов' " \
               f"- предварительный отчёт "
        await bot.send_message(chat_id=message.chat.id, text=mess, reply_markup=markup)
    else:

        mess = f"Привет {message.from_user.first_name} я бот который поможет автоматизировать отчёты по расходам"
        await bot.send_message(chat_id=message.chat.id, text=mess)
        with open(file_json, 'w') as file:
            json.dump(data, file)
        await bot.send_message(message.chat.id, 'расчетный период начинается с сегодняшнего дня \n'
                                                'вот команды :\n'
                                                '"ИТОГ"- формировать отчёт(закрыть период)\nкнопка "удалить расход"- '
                                                'возврат '
                                                '\n "Записать расходы" - добавить расходы',
                               reply_markup=markup)


""" /REPORT """


@db.message_handler(text='\U0001F6AB ИТОГ')
async def report(message: types.Message):
    file_json = 'files/' + str(message.from_user.id) + '.json'
    if os.path.exists(file_json):
        await bot.send_message(message.chat.id,
                               'Это дейстие приведёт к удалению файла на сервере и закрытию отчёнтого периода')
        markup_inline_report = types.InlineKeyboardMarkup(row_width=2)
        button_yes = types.InlineKeyboardButton('Да', callback_data=callback_other.new(action="yes"))
        button_no = types.InlineKeyboardButton('Нет', callback_data=callback_other.new(action="no"))
        markup_inline_report.add(button_no, button_yes)
        await bot.send_message(text="Вы уверены ?", chat_id=message.chat.id, reply_markup=markup_inline_report)
    else:
        await bot.send_message(message.chat.id, "Вы можете начать новый расчётный период \n" + COMMANDS)


""" /RATE """


@db.message_handler(text='\U00002712 записать расходы', state='*')
async def rate(message: types.Message):
    file_json = 'files/' + str(message.from_user.id) + '.json'
    if os.path.exists(file_json):

        await RateForm.name.set()
        await bot.send_message(message.chat.id, text='\U0001F4C3 Название расходов ', reply_markup=rate_markup)

    else:
        await bot.send_message(message.chat.id, "Вы можете начать новый расчётный период \n" + COMMANDS)


@db.message_handler(content_types=types.ContentType.TEXT, state=RateForm.name)
async def name_step(message: types.Message, state: FSMContext):
    if message.text == "отмена":
        await state.finish()
        await bot.send_message(message.chat.id, "Действие отменено", reply_markup=markup)
    else:
        await state.update_data(chosen_name_rate=message.text.strip())
        await RateForm.next()
        await bot.send_message(message.chat.id, " \U0001F4B3 Теперь укажите сумму:")


@db.message_handler(text="отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.chat.id, "Действие отменено", reply_markup=markup)


@db.message_handler(content_types=types.ContentType.TEXT, state=RateForm.price)
async def price_step(message: types.Message, state: FSMContext):
    file_json = 'files/' + str(message.from_user.id) + '.json'
    if message.text == 'отмена':
        await state.finish()
        await bot.send_message(message.chat.id, "Действие отменено", reply_markup=markup)
    elif not message.text.strip().isdigit():
        await bot.send_message(message.chat.id, "введите сумму цифрами")
        return
    else:
        name_rate = await state.get_data()
        await bot.send_message(message.chat.id, f'записываю {name_rate["chosen_name_rate"]} - сумма {message.text}',
                               reply_markup=markup)
        append_row_in_file(file_json, name_rate["chosen_name_rate"], message.text)
        await state.finish()


""" /REFUND  """


@db.message_handler(text='\U0000274c удалить расход')
async def refund(message: types.Message):
    file_json = 'files/' + str(message.from_user.id) + '.json'
    if os.path.exists(file_json):
        rate_list = get_list_refund(file_json)
        if len(rate_list) == 0:
            await bot.send_message(message.chat.id, "Сегодня расходов ещё не было")
        else:
            await bot.send_message(message.chat.id, "наименование расходов")
            markup_inline = types.InlineKeyboardMarkup()
            for button_str in rate_list:
                button = types.InlineKeyboardButton(button_str, callback_data="refund_" + button_str)
                markup_inline.add(button)
            await bot.send_message(message.chat.id, "Выберите из списка расходов тот, который удаляем",
                                   reply_markup=markup_inline)
    else:
        await bot.send_message(message.chat.id, "Вы можете начать новый расчётный период \n" + COMMANDS)


"""PLUS BALANS """


@db.message_handler(text='Приход на баланс')
async def plus_balans(message: types.Message):
    file_json = 'files/' + str(message.from_user.id) + '.json'
    if os.path.exists(file_json):
        await PlusForm.name.set()
        await message.answer('название прихода средств', reply_markup=rate_markup)
    else:
        await bot.send_message(message.chat.id, "Вы можете начать новый расчётный период \n" + COMMANDS)


@db.message_handler(content_types=types.ContentType.TEXT, state=PlusForm.name)
async def answer_from_plus(message: types.Message, state: FSMContext):
    if message.text == "отмена":
        await state.finish()
        await bot.send_message(message.chat.id, "Действие отменено", reply_markup=markup)
    else:
        await state.update_data(chosen_name_plus=message.text.strip())
        await PlusForm.next()
        await bot.send_message(message.chat.id, " \U0001F4B3 Теперь укажите сумму:", reply_markup=rate_markup)


@db.message_handler(content_types=types.ContentType.TEXT, state=PlusForm.price)
async def end_plus(message: types.Message, state: FSMContext):
    file_json = 'files/' + str(message.from_user.id) + '.json'
    if message.text == 'отмена':
        await state.finish()
        await bot.send_message(message.chat.id, "Действие отменено", reply_markup=markup)
    elif not message.text.strip().isdigit():
        await bot.send_message(message.chat.id, "введите сумму цифрами")
        return
    else:
        name_plus = await state.get_data()
        await bot.send_message(message.chat.id, f'записываю {name_plus["chosen_name_plus"]} - сумма -{message.text}',
                               reply_markup=markup)
        append_row_in_file(file_json, f'{name_plus["chosen_name_plus"]}', f'-{message.text}')
        await state.finish()


"""   /INFO-REPORT   """


@db.message_handler(text=['\U0001F4CB Просмотр расходов'])
async def info_report(message: types.Message):
    file_json = 'files/' + str(message.from_user.id) + '.json'
    if os.path.exists(file_json):
        mess = get_info_report(file_json)
        await bot.send_message(message.chat.id, mess)
    else:
        await bot.send_message(message.chat.id, "Вы можете начать новый расчётный период \n" + COMMANDS)


@db.callback_query_handler(callback_other.filter(action=['yes', 'no']))
async def callback_report(call: types.CallbackQuery, callback_data: dict):
    if call.message:
        action = callback_data["action"]
        if action == 'yes':
            file_json = 'files/' + str(call.from_user.id) + '.json'
            mess = get_info_report(file_json)
            await bot.send_message(call.message.chat.id, mess)
            os.remove(file_json)

            await bot.send_message(chat_id=call.message.chat.id,
                                   text="Вы можете начать новый расчётный период \n" + COMMANDS,
                                   reply_markup=markup_yes)
        elif action == 'no':
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        text=COMMANDS,
                                        message_id=call.message.message_id)


@db.callback_query_handler(Text(startswith="refund_"))
async def callback_refund(call: types.CallbackQuery):
    if call.message:
        action = call.data.split('_')[1]
        file_json = 'files/' + str(call.from_user.id) + '.json'
        delete_row_in_file(file_json=file_json, call=action)  # удаляем данные из json
        await bot.edit_message_text(chat_id=call.message.chat.id, text=f'Ок, позиция {action} удалена из отчета',
                                    message_id=call.message.message_id, )


@db.message_handler(content_types=types.ContentType.DOCUMENT)
async def file(message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "text.xlsx")


@db.message_handler(content_types=['text'])
async def default_answer(message):
    if message.text.capitalize() == 'Погода':
        result = await pars_weather()
        await message.answer(
            f'{result.number_day} {result.month} {result.day}\n {result.weather} {result.temperature}\n\n'
            f'Магнитные бури сегодня\n'
            f'часы 0  3  6  9  12  15  18  21\n'
            
            f'буря  {result.magnit["0"]}  {result.magnit["3"]}  {result.magnit["6"]}  {result.magnit["9"]}'
            f'   {result.magnit["12"]}    {result.magnit["15"]}    {result.magnit["18"]}    {result.magnit["21"]}')

    else:
        await bot.send_message(message.chat.id, "Извените я не понимаю," + COMMANDS)


if __name__ == "__main__":
    executor.start_polling(db)
