from itertools import count
import pdfplumber
import re
import json
import os
from collections import defaultdict
from datetime import datetime


class Product:
    def __init__(self, name, quantity, price, measure_of_quantity):
        self.name = name           # Название товара
        self.quantity = quantity   # Количество
        self.price = price         # Цена
        self.total = quantity * price  # Общая стоимость
        self.measure_of_quantity = measure_of_quantity # мера количества

    def to_dict(self):
        """Преобразует объект Product в словарь"""
        return {
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
            "total": self.total,
            "measure_of_quantity": self.measure_of_quantity
        }

class Checkinfo:
    def __init__(self, date, time, payment_address, place_settlement):
        self.date = date
        self.time = time 
        self.payment_address = payment_address
        self.place_settlement = place_settlement

    def to_dict(self):
        """Преобразует объект Checkinfo в словарь"""
        return {
            "date": self.date,
            "time": self.time,
            "payment_address": self.payment_address,
            "place_settlement": self.place_settlement
        }

    

def create_product(text_line, prefix, len_prefix, info_about_check):
    pattern = r'(\d+[,.]?\d*)\s*[X]\s*(\d+[,.]?\d*)'
    match = re.search(pattern, text_line)

    pattern2 = r'\s*=\s*(\d+[.,]\d+)(?![\w.,])' 
    match2 = re.search(pattern2, text_line)

    
    if match:
        quantity = match.group(1)
        price = match.group(2)
    else:
        print("ОШИБКА ПРИ СЧИТЫВАНИИ КОЛИЧЕСТВА И ЦЕНЫ ЗА ЕДИНИЦУ КОЛИЧЕСТВА ТОВАРА!")
        return 
    if match2:
        resultt = match2.group(1)
    else:
        print("ОШИБКА ПРИ СЧИТЫВАНИИ ИТОГОВОЙ СУММЫ ТОВАРА!")
        return 

    index_nds = text_line.find("в т.ч. СУММА НДС")
    name = text_line[:index_nds].replace(f"{quantity} X {price}", "")
    measure_of_quantity = text_line[text_line.find(prefix)+len_prefix+1:]

    if check(resultt, quantity, price):  # изменения
        quantity = float(match.group(1).replace(",", "."))
        price = float(match.group(2).replace(",", "."))
        product_item = Product(name, quantity, price, measure_of_quantity) 
        info_about_check.append(product_item)
        

def check(resultt, quantity, price):
    try:
        resultt1 = float(resultt.replace(",", "."))
    except ValueError:
        print(resultt, end = "\n")
        print("Итоговая сумма продукта в pdf-чеке считана некорректно!")
        return False

    try:
        quantity1 = float(quantity.replace(",", "."))
    except ValueError:
        print("Мера количества товара продукта в pdf-чеке считана некорректно!")
        return False

    try:
        price1 = float(price.replace(",", "."))
    except ValueError:
        print("Стоимость товара за единицу меры количества в pdf-чеке считана некорректно!")
        return False


    if (round(quantity1 * price1, 2) == resultt1):  
        return True
    else: 
        print("Данные о итоговой сумме/мере количества/стоимости за единицу меры количества товара в pdf-чеке считана некорректно!")
        print(f"Ожидалось: {quantity1 * price1:.2f}, получено: {resultt1}")
        return False

def date_time_string_TEST(stringo):
    pattern = r'^\d{2}\.\d{2}\.\d{2} \d{2}:\d{2} $'
    return bool(re.match(pattern, stringo))
        

def parse_pdf(pdf_path):
    initial_data = "" # исходные данные
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                initial_data += text + " "
    return initial_data

def products_information(initial_data):
    info_about_check = [] # список всех данных о чеке
    prefix = "Мера кол-ва предмета расчета"
    product_categories = []
    len_prefix = len(prefix)
    
    
    initial_data_now = initial_data.replace("\n", " ") # убрали переходы на новые строки для удобства

    if (initial_data_now.find("check.ofd.ru")):
        pruning_index = initial_data_now.find("check.ofd.ru") # индекс обрезки. Тот, после которого идут полезные данные
    if initial_data_now.find("check.ofd.ru") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ check.ofd.ru! Проверьте PDF-файл")
        return 

    if initial_data_now.find("ДАТА ВЫДАЧИ "):
        index_date_issue = initial_data_now.find("ДАТА ВЫДАЧИ ") + 12 #строка дата выдачи. индекс в исходных данных
    if initial_data_now.find("ДАТА ВЫДАЧИ ") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ ДАТА ВЫДАЧИ! Проверьте PDF-файл")
        return 

    if initial_data_now.find("АДРЕС РАСЧЁТОВ "):
        index_payment_address = initial_data_now.find("АДРЕС РАСЧЁТОВ ") #строка адрес расчетов. индекс в исходных данных
    if initial_data_now.find("АДРЕС РАСЧЁТОВ ") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ АДРЕС РАСЧЁТОВ! Проверьте PDF-файл")
        return 

    if initial_data_now.find("МЕСТО РАСЧЁТОВ "):
        index_place_settlement = initial_data_now.find("МЕСТО РАСЧЁТОВ ") #строка адрес расчетов. индекс в исходных данных
    if initial_data_now.find("МЕСТО РАСЧЁТОВ ") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ МЕСТО РАСЧЁТОВ! Проверьте PDF-файл")
        return 

    if initial_data_now.find(" КАССИР"):
        index_cashier = initial_data_now.find(" КАССИР") # строка кассир. индекс в исходных данных
    if initial_data_now.find(" КАССИР") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ КАССИР! Проверьте PDF-файл")
        return 

    dateTime = initial_data_now[index_date_issue:index_payment_address]

    if date_time_string_TEST(dateTime):
        Date_and_Time = initial_data_now[index_date_issue:index_payment_address] # дата и время выдачи чека
    if date_time_string_TEST(dateTime) == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ ДАТЫ И ВРЕМЕНИ! Проверьте PDF-файл")
        return 

    date,time = Date_and_Time.split()
    payment_address = initial_data_now[index_payment_address + 15:index_place_settlement - 1] # адрес расчетов
    place_settlement = initial_data_now[index_place_settlement + 15:index_cashier] # место расчетов

    date_time_payment_address_place_settlement = Checkinfo(date, time, payment_address, place_settlement) 
    info_about_check.append(date_time_payment_address_place_settlement)

    initial_data_now = initial_data_now[pruning_index+13:]

    if initial_data_now.find("ПРИЗНАК СПОСОБА РАСЧЕТА") == -1:
        print(1)
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ ПРИЗНАК СПОСОБА РАСЧЕТА! Проверьте PDF-файл")
        return 

    if initial_data_now.find("ПРИЗНАК СПОСОБА РАСЧЕТА"):
        initial_data_now = initial_data_now.replace("ПРИЗНАК СПОСОБА РАСЧЕТА", " ")
    

    if initial_data_now.find("ПРИЗНАК ПРЕДМЕТА") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ ПРИЗНАК ПРЕДМЕТА! Проверьте PDF-файл")
        return 

    if initial_data_now.find("ПРИЗНАК ПРЕДМЕТА"):
        initial_data_now = initial_data_now.replace("ПРИЗНАК ПРЕДМЕТА", " ")
   

    if initial_data_now.find("РАСЧЕТА") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ РАСЧЕТА! Проверьте PDF-файл")
        return 

    if initial_data_now.find("РАСЧЕТА"):
        initial_data_now = initial_data_now.replace("РАСЧЕТА", " ")
    
    if initial_data_now.find("Результат проверки сведений ") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ Результат проверки сведений о товаре! Проверьте PDF-файл")
        return 

    if initial_data_now.find("Результат проверки сведений "):
        initial_data_now = initial_data_now.replace("Результат проверки сведений ", " ")
    
    if initial_data_now.find("Идентификатор ФОИВ") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ Идентификатор ФОИВ! Проверьте PDF-файл")
        return 

    if initial_data_now.find("Идентификатор ФОИВ"):
        initial_data_now = initial_data_now.replace("Идентификатор ФОИВ", " ")
    
    if initial_data_now.find("Дата/Номер док. основания") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ Дата/Номер док. основания! Проверьте PDF-файл")
        return 

    if initial_data_now.find("Дата/Номер док. основания"):
        initial_data_now = initial_data_now.replace("Дата/Номер док. основания", " ")
    
    if initial_data_now.find("Отраслевой реквизит") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ Отраслевой реквизит! Проверьте PDF-файл")
        return 

    if initial_data_now.find("Отраслевой реквизит"):
        initial_data_now = initial_data_now.replace("Отраслевой реквизит", " ")
    
    if initial_data_now.find("ПОЛНЫЙ РАСЧЕТ") == -1:
        print("ОШИБКА В СЧИТЫВАНИИ СТРОКИ ПОЛНЫЙ РАСЧЕТ! Проверьте PDF-файл")
        return
    if initial_data_now.find("ПОЛНЫЙ РАСЧЕТ"):
        initial_data_now = initial_data_now.replace("ПОЛНЫЙ РАСЧЕТ", " ")
    

    count_prefix = initial_data_now.count(prefix)
    initial_data_NOW = initial_data_now
    #делим
    for i in range(count_prefix):
        indeX = initial_data_NOW.find(prefix)
        separator_product = initial_data_NOW.find(" ", indeX + len_prefix + 1)
        product_categories.append(initial_data_NOW[:separator_product])
        initial_data_NOW = initial_data_NOW[separator_product+1:]

    for linE in product_categories:
        create_product(linE, prefix, len_prefix, info_about_check)


    return info_about_check



def in_dict(info_about_check): 
    # products_dicts = [product.to_dict() for product in info_about_check]
    # return products_dicts

    if not info_about_check:
        return {}

    check_info = info_about_check[0].to_dict() if hasattr(info_about_check[0], 'to_dict') else {}

    products_list = []

    for item in info_about_check[1:]:
        if hasattr(item, 'to_dict'):
            products_list.append(item.to_dict())
    
    result = {
        "check_info": check_info,
        "products": products_list,
        "total_sum": sum(item.total for item in info_about_check[1:])
    }
    
    return result


def summa(pdf_path):
    initial_data = parse_pdf(pdf_path)
    result_pruning = initial_data[initial_data.find("ИТОГ") + 5:]
    summa_numb = result_pruning[:result_pruning.find("\n")]
    summ = float(summa_numb)
    return summ


def IN_JSON(all_prod):
    json_data = in_dict(all_prod)
    with open('check_data.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

def total_amounts_receipts_month(pdf_path_month):
    pdf_files = [f for f in os.listdir(pdf_path_month) if f.lower().endswith('.pdf')]

    monthly_totals = defaultdict(float)
    i = 0

    while i < len(pdf_files):
        pdf_path = os.path.join(pdf_path_month, pdf_files[i])
        try:
            initial_data =  parse_pdf(pdf_path)
            check_data = products_information(initial_data)   #ИЗМЕНЕНИЯ

            raw_date = check_data[0].date
            check_sum = summa(pdf_path)
            dt = datetime.strptime(raw_date, "%d.%m.%y")
            month_key = dt.strftime("%m-%Y")
            monthly_totals[month_key] += check_sum

        except Exception as error:
            print(f"Ошибка при обработке {pdf_files[i]}: {error}")

        i += 1

    print("Сумма по месяцам: ")
    for month in sorted(monthly_totals):
        print(f"{month}: {monthly_totals[month]:.2f} руб.")

def TEST(file1):
    with open(file1, 'r', encoding='utf-8') as file:
        init_dat = file.read()
    return init_dat

def main():
    # pdf_path = "C:\\Users\\ivano\\Desktop\\check\\check1.pdf" #Пример: pdf_path = "E:\\Check\\check2.pdf"

    # # pdf_path_month = "C:\\Users\\ivano\\Desktop\\check" #Пример: pdf_path_month = "E:\\Check"

    # initial_data = parse_pdf(pdf_path)
    # print(initial_data)
    # all_prod = products_information(initial_data)
    

    # IN_JSON(all_prod)

    #total_amounts_receipts_month(pdf_path_month)

    
    initial_data1 = TEST("TEST3.txt")
    
    all_prod = products_information(initial_data1)

    # функция summa хранит в себе сумму чека дробным значением
    # print(f"   Дата выдачи чека: {all_prod[0].date}")
    # print(f"   Время выдачи чека: {all_prod[0].time}")
    # print(f"   Адрес расчетов: {all_prod[0].payment_address}")
    # print(f"   Место расчетов: {all_prod[0].place_settlement}")
    # print("\nСписок покупок:\n")
    # for i, product in enumerate(all_prod[1:], 1):
    #     print(f"{i}. {product.name}")
    #     print(f"   Количество: {product.quantity}")
    #     print(f"   Цена: {product.price} руб")
    #     print(f"   Общая стоимость: {product.total:.2f} руб")


if __name__ == "__main__":
    main()
