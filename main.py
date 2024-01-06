import datetime

import telebot
from simpful import *

bot = telebot.TeleBot("YOUR_TOKEN")

# об'єкт нечіткої логіки
FS = FuzzySystem()

# Створення термів
cur_year = datetime.date.today().year
manufacture_year_very_old = FuzzySet(function=Trapezoidal_MF(1932, 1942, (cur_year - 52), (cur_year - 32)),
                                     term="very_old")
manufacture_year_old = FuzzySet(
    function=Trapezoidal_MF((cur_year - 49), (cur_year - 39), (cur_year - 29), (cur_year - 19)), term="old")
manufacture_year_almost_new = FuzzySet(
    function=Trapezoidal_MF((cur_year - 28), (cur_year - 17), (cur_year - 9), (cur_year - 2)), term="almost_new")
manufacture_year_new = FuzzySet(function=Triangular_MF((cur_year - 4), cur_year, (cur_year + 4)), term="new")
FS.add_linguistic_variable("manufacture_year", LinguisticVariable([manufacture_year_very_old,
                                                                   manufacture_year_old,
                                                                   manufacture_year_almost_new,
                                                                   manufacture_year_new],
                                                                  universe_of_discourse=[1950, cur_year]), verbose=True)

car_mileage_normal = FuzzySet(function=Trapezoidal_MF(a=-73980, b=-11110, c=73330, d=117500), term="normal")
car_mileage_average = FuzzySet(function=Trapezoidal_MF(50000, 100000, 150000, 176300), term="average")
car_mileage_high = FuzzySet(function=Trapezoidal_MF(150000, 200000, 500000, 530000), term="high")
FS.add_linguistic_variable("car_mileage",
                           LinguisticVariable([car_mileage_normal, car_mileage_average, car_mileage_high],
                                              universe_of_discourse=[0, 300000]), verbose=True)

technical_condition_bad = FuzzySet(function=Gaussian_MF(mu=0, sigma=1.77), term="bad")
technical_condition_normal = FuzzySet(function=Gaussian_MF(5, 1.77), term="normal")
technical_condition_good = FuzzySet(function=Gaussian_MF(10, 1.77), term="good")
FS.add_linguistic_variable("technical_condition", LinguisticVariable(
    [technical_condition_bad, technical_condition_normal, technical_condition_good], universe_of_discourse=[0, 10]),
                           verbose=True)

price_cheap = FuzzySet(function=Trapezoidal_MF(-70930, 0, 8000, 30000), term="cheap")
price_average = FuzzySet(function=Trapezoidal_MF(20000, 40000, 70000, 100000), term="average")
price_average_expensive = FuzzySet(function=Trapezoidal_MF(60000, 100000, 130000, 160000), term="average_expensive")
price_expensive = FuzzySet(function=Trapezoidal_MF(100000, 160000, 300000, 400000), term="expensive")
FS.add_linguistic_variable("price",
                           LinguisticVariable([price_cheap, price_average, price_average_expensive, price_expensive],
                                              universe_of_discourse=[500, 200000]), verbose=True)

# Створення вихідного терму
recommendation_negative = FuzzySet(function=Trapezoidal_MF(-4.12, -0.458, 1.66279069767442, 4.12), term="negative")
recommendation_average = FuzzySet(function=Trapezoidal_MF(2.06, 4.56, 6.15374677002584, 8.46), term="average")
recommendation_positive = FuzzySet(function=Trapezoidal_MF(6.88, 8.9108527131783, 11, 15.1), term="positive")
FS.add_linguistic_variable("recommendation", LinguisticVariable(
    [recommendation_negative, recommendation_average, recommendation_positive], universe_of_discourse=[0, 10]),
                           verbose=True)

# Занесення правил
FS.add_rules_from_file(path='rules.txt')


@bot.message_handler(commands=['help', 'start'])
def info_msg(message):
    bot.send_message(message.chat.id, "Вітаю!👋\n"
                                      "Цей бот створений, щоб допомогти вам з покупкою авто. "
                                      "Просто почніть опитування командою /run.\n"
                                      "Дайте відповіді на запитання про автомобіль і отримаєте рекомендації щодо "
                                      "покупки машини 🤖🚗")


@bot.message_handler(commands=['run'])
def run_quiz(message):
    bot.send_message(message.from_user.id, "Починаємо опитування.\n"
                                           "Напишіть /exit щоб припинити опитування.\n\n"
                                           "Який рік виготовлення автомобіля?")
    bot.register_next_step_handler(message, get_manufacture_year)


def get_manufacture_year(message):
    if message.text.lower() == '/exit':
        bot.send_message(message.chat.id, "Опитування припинено")
        return
    global manufacture_year
    try:
        manufacture_year = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "‼️*Не коректне значення*‼️\n"
                                          "Повинна бути цифра", parse_mode='Markdown')
        bot.register_next_step_handler(message, get_manufacture_year)
        return
    if manufacture_year < 1950 or manufacture_year > cur_year:
        bot.send_message(message.chat.id, "️‼️*Не коректне значення*‼️\n"
                                          "Рік має бути між 1950 та " + str(cur_year), parse_mode='Markdown')
        bot.register_next_step_handler(message, get_manufacture_year)
        return
    bot.send_message(message.chat.id, "Який пробіг у автомобіля? (км)")
    bot.register_next_step_handler(message, get_car_mileage)


def get_car_mileage(message):
    if message.text.lower() == '/exit':
        bot.send_message(message.chat.id, "Опитування припинено")
        return
    global car_mileage
    try:
        car_mileage = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "‼️*Не коректне значення*‼️\n"
                                          "Повинна бути цифра", parse_mode='Markdown')
        bot.register_next_step_handler(message, get_car_mileage)
        return
    if car_mileage < 0 or car_mileage > 300000:
        bot.send_message(message.chat.id, "️‼️*Не коректне значення*‼️\n"
                                          "Пробіг має бути між 0 км та 300 тис. км", parse_mode='Markdown')
        bot.register_next_step_handler(message, get_car_mileage)
        return
    bot.send_message(message.chat.id, "Оцініть від 0 до 10 технічний стан автомобіля за зовнішнім оглядом (наявність "
                                      "подряпин, видимих ознак участі в ДТП, іржа, тощо.)\n"
                                      "`0 - багато недоліків\n"
                                      "10 - в ідеальному стані`", parse_mode='Markdown')
    bot.register_next_step_handler(message, get_technical_condition)


def get_technical_condition(message):
    if message.text.lower() == '/exit':
        bot.send_message(message.chat.id, "Опитування припинено")
        return
    global technical_condition
    try:
        technical_condition = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "‼️*Не коректне значення*‼️\n"
                                          "Повинна бути цифра", parse_mode='Markdown')
        bot.register_next_step_handler(message, get_technical_condition)
        return
    if technical_condition < 0 or technical_condition > 10:
        bot.send_message(message.chat.id, "️‼️*Не коректне значення*‼️\n"
                                          "Значення має бути між 0 та 10", parse_mode='Markdown')
        bot.register_next_step_handler(message, get_technical_condition)
        return
    bot.send_message(message.chat.id, "Яка ціна автомобіля в доларах? ($)")
    bot.register_next_step_handler(message, get_price)


def get_price(message):
    if message.text.lower() == '/exit':
        bot.send_message(message.chat.id, "Опитування припинено")
        return
    global price
    try:
        price = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "‼️*Не коректне значення*‼️\n"
                                          "Повинна бути цифра", parse_mode='Markdown')
        bot.register_next_step_handler(message, get_price)
        return
    if price < 500 or price > 200000:
        bot.send_message(message.chat.id, "️‼️*Не коректне значення*‼️\n"
                                          "Ціна має бути між 500 $ та 200тис. $", parse_mode='Markdown')
        bot.register_next_step_handler(message, get_price)
        return
    give_recommendation(message)


def give_recommendation(message):
    bot.send_message(message.chat.id, "_" + message.chat.first_name + ", ваші дані_\nРік виготовлення: `" + str(
        manufacture_year) + "`\nПробіг "
                            "автомобіля: `" +
                     str(car_mileage) + " км`\nТехнічний стан: `" + str(technical_condition) + "`\nЦіна: `" + str(price)
                     + " $`", parse_mode='Markdown')
    variables = ["manufacture_year", "car_mileage", "technical_condition", "price"]
    values = [manufacture_year, car_mileage, technical_condition, price]
    for variable, value in zip(variables, values):
        FS.set_variable(variable, value)
    mamdani = FS.Mamdani_inference()
    bot.send_message(message.chat.id, "*Порада*\n" + get_recommendation(mamdani.get("recommendation")), parse_mode='Markdown')
    bot.send_message(message.chat.id, "Дякуємо, що користуєтеся нашим ботом. Раді якщо змогли вам допомогти😁\nЩоб отримати нову пораду введіть /run")


def get_recommendation(coef):
    if 0 <= coef < 3.3:
        return "🔴 Автомобіль не вартий уваги, пошукайте щось краще."
    elif 3.3 <= coef < 6.6:
        return "🟡 Автомобіль у гарному стані, але має свої недоліки. Якщо вас все влаштовує то купуйте 😅"
    elif 6.6 <= coef <= 10:
        return "🟢 Гарний вибір. Авто в ідельному стані. Купуйте - не пошкодуєте 😎"


@bot.message_handler(commands=['exit'])
@bot.message_handler(func = lambda msg: msg.text is not None and '/' not in msg.text)
def query_handler(message):
    bot.send_message(message.chat.id, "Не розумію вашого прохання🤷‍♂️")
    info_msg(message)


bot.infinity_polling()
