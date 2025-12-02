import pdfplumber
import re

class Product:
    def __init__(self, name, quantity, price, measure_of_quantity):
        self.name = name           # Название товара
        self.quantity = quantity   # Количество
        self.price = price         # Цена
        self.total = quantity * price  # Общая стоимость
        self.measure_of_quantity = measure_of_quantity # мера количества
        
class Checkinfo:
    def __init__(self, date, time, payment_address, place_settlement):
        self.date = date
        self.time = time 
        self.payment_address = payment_address
        self.place_settlement = place_settlement

def create_product(text_line, prefix, len_prefix, info_about_check):
    pattern = r'(\d+[,.]?\d*)\s*[X]\s*(\d+[,.]?\d*)'
    match = re.search(pattern, text_line)
    
    if match:
        quantity = match.group(1)
        price = match.group(2)


        index_nds = text_line.find("в т.ч. СУММА НДС")
        name = text_line[:index_nds].replace(f"{quantity} X {price}", "")
        measure_of_quantity = text_line[text_line.find(prefix)+len_prefix+1:]

        quantity = float(match.group(1).replace(",", "."))
        price = float(match.group(2).replace(",", "."))
        product_item = Product(name, quantity, price, measure_of_quantity) 
        info_about_check.append(product_item)
        check(text_line, quantity, price)

def check(text_line, quantity, price):
    pattern = r'\s*=\s*(\d+[.,]?\d*)'
    match = re.search(pattern, text_line)
    if match:
        resultt = match.group(1)
    resultt1 = float(resultt)
    if (round(quantity * price, 2) == resultt1):
        print("Данные из PDF-файла считаны успешно!")
        return True
        
    else:
        print("Ошибка в считывании PDF-файла!")
        return False

def parse_pdf(pdf_path):
    global summa
    initial_data = "" # исходные данные
    info_about_check = [] # список всех данных о чеке
    prefix = "Мера кол-ва предмета расчета"
    product_categories = []
    len_prefix = len(prefix)
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                initial_data += text + " "

    
    initial_data_now = initial_data.replace("\n", " ") # убрали переходы на новые строки для удобства
    pruning_index = initial_data_now.find("check.ofd.ru") # индекс обрезки. Тот, после которого идут полезные данные
    index_date_issue = initial_data_now.find("ДАТА ВЫДАЧИ ") + 12 #строка дата выдачи. индекс в исходных данных
    index_payment_address = initial_data_now.find("АДРЕС РАСЧЁТОВ ") #строка адрес расчетов. индекс в исходных данных
    index_place_settlement = initial_data_now.find("МЕСТО РАСЧЁТОВ ") #строка адрес расчетов. индекс в исходных данных
    index_cashier = initial_data_now.find(" КАССИР") # строка кассир. индекс в исходных данных
    Date_and_Time = initial_data_now[index_date_issue:index_payment_address] # дата и время выдачи чека

    date,time = Date_and_Time.split()
    payment_address = initial_data_now[index_payment_address + 15:index_place_settlement - 1] # адрес расчетов
    place_settlement = initial_data_now[index_place_settlement + 15:index_cashier] # место расчетов

    date_time_payment_address_place_settlement = Checkinfo(date, time, payment_address, place_settlement) 
    info_about_check.append(date_time_payment_address_place_settlement)

    initial_data_now = initial_data_now[pruning_index+13:]
    initial_data_now = initial_data_now.replace("ПРИЗНАК СПОСОБА РАСЧЕТА", " ")
    initial_data_now = initial_data_now.replace("ПРИЗНАК ПРЕДМЕТА", " ")
    initial_data_now = initial_data_now.replace("РАСЧЕТА", " ")
    initial_data_now = initial_data_now.replace("Результат проверки сведений о товаре", " ")
    initial_data_now = initial_data_now.replace("Идентификатор ФОИВ", " ")
    initial_data_now = initial_data_now.replace("Дата/Номер док. основания", " ")
    initial_data_now = initial_data_now.replace("Отраслевой реквизит", " ")
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

    summa_pruning = initial_data_NOW[5:];
    summa_numb = summa_pruning[:summa_pruning.find(" ")]
    summa = float(summa_numb)

    return info_about_check

    

def main():
    pdf_path = "C:\\Users\\ivano\\Desktop\\проект\\check3.pdf"
    all_prod = parse_pdf(pdf_path)

    # summa хранит в себе сумму чека дробным значением
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

    
    



   

    

    



