import json
import datetime
import random
from typing import NamedTuple
import aiohttp, asyncio
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup


class WeatherTuple(NamedTuple):
    day: str
    number_day: str
    month: str
    weather: str
    temperature: str
    magnit: dict


def append_row_in_file(file_json, name_row, price):
    with open(file_json, 'r+') as file_read:
        data = json.load(file_read)
        today = str(datetime.date.today())

        for elem in data:
            key = [*elem]
            if today in key:
                rates = [*elem[today]]
                if name_row in rates:
                    name_row = name_row + f"/копия{random.randint(1, 90)}"
                    elem[today].update({name_row: price})
                else:
                    elem[today].update({name_row: price})

            else:
                elem.update({today: {name_row: price}})

        with open(file_json, 'w', encoding='UTF8') as file:
            json.dump(data, file)


def delete_row_in_file(file_json, call):
    with open(file_json, 'r+') as file_read:
        data = json.load(file_read)
        today = str(datetime.date.today())

        for elem in data:
            key = [*elem]

            if today in key:

                elem[today].pop(call)

                try:
                    with open(file_json, 'w') as file:
                        json.dump(data, file)
                except KeyError as ex:
                    print(ex)


"""  :return list_refund """


def get_list_refund(file_json):
    with open(file_json) as file:
        data = json.load(file)
        today = str(datetime.date.today())
        for elem in data:
            key = [*elem]
            if today in key:

                result_list = []
                for item in elem[today]:
                    result_list.append(item)

    return result_list


def get_info_report(file_json):
    with open(file_json, 'r') as file:
        data = json.load(file)

        mess = ""
        days = [*data[0]]
        result = 0
        for day in days:
            mess += ('	\U00002714 ' + day + '\n')
            summa = 0
            for rate, price in data[0][day].items():
                mess += f"     * {rate}  {price} \n"
                summa += int(price)
            mess += f"  итог дня {summa}\n"
            result += summa
        mess += f"\U00002757 потраченные средства за период {result}"

    return mess


async def pars_weather():
    ua = UserAgent()
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
        'Accept:': '*/*'
    }
    async with aiohttp.ClientSession() as session:
        response = await session.get('https://world-weather.ru/pogoda/russia/engels/', headers=headers)
        soup = BeautifulSoup(await response.text(), 'lxml')
        block = soup.find('ul', id='vertical_tabs').find('li', class_='current')
        day = block.find('div', class_='day-week').text.strip()
        number_day = block.find('div', class_='numbers-month').text.strip()
        month = block.find('div', class_='month').text.strip()
        weather = block.find('span', class_='icon-weather').get('title')
        temperature = block.find('div', class_='day-temperature').text.strip()

        async with aiohttp.ClientSession() as session_two:
            response = await session_two.get('https://my-calend.ru/magnitnye-buri/engel-s', headers=headers)
            soup = BeautifulSoup(await response.text(), 'lxml')
            block_burya_today = soup.find('table', class_='magnitnye-buri-items')
            hours = block_burya_today.findAll('tr')

            hours_list = []
            index_list = []
            for i in hours[0]:
                if i.text.isdigit():
                    hours_list.append(i.text)
            for ind in hours[1]:
                if ind.text.isdigit():
                    index_list.append(ind.text)

            magnit_b = dict(zip(hours_list, index_list))

            result = WeatherTuple(
                day=day,
                number_day=number_day,
                month=month,
                weather=weather,
                temperature=temperature,
                magnit=magnit_b
            )

            return result


