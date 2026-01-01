import unittest
import json
import tempfile
import os
from unittest.mock import patch, mock_open
from datetime import datetime
from Check_Pdf import Product, Checkinfo, check, date_time_string_TEST, create_product, in_dict, summa, parse_pdf, products_information, IN_JSON, total_amounts_receipts_month
import sys
from unittest.mock import patch, MagicMock, mock_open
from auth import AdaptiveMobileLoginApp, USERS_FILE


class TestProductClass(unittest.TestCase):
    def test_product_creation(self):
        product = Product("Яблоки", 2.5, 100.0, "кг")
        self.assertEqual(product.name, "Яблоки")
        self.assertEqual(product.quantity, 2.5)
        self.assertEqual(product.price, 100.0)
        self.assertEqual(product.total, 250.0)
        self.assertEqual(product.measure_of_quantity, "кг")
    
    def test_product_to_dict(self):
        product = Product("Молоко", 1, 80.0, "л")
        expected_dict = {
            "name": "Молоко",
            "quantity": 1,
            "price": 80.0,
            "total": 80.0,
            "measure_of_quantity": "л"
        }
        self.assertDictEqual(product.to_dict(), expected_dict)
    
    def test_product_with_zero_quantity(self):
        product = Product("Хлеб", 0, 50.0, "шт")
        self.assertEqual(product.total, 0)


class TestCheckinfoClass(unittest.TestCase):

    def test_checkinfo_creation(self):
        checkinfo = Checkinfo("25.12.25", "14:30", "ул. Киренского, 17", "Магазин 'Командор'")
        self.assertEqual(checkinfo.date, "25.12.25")
        self.assertEqual(checkinfo.time, "14:30")
        self.assertEqual(checkinfo.payment_address, "ул. Киренского, 17")
        self.assertEqual(checkinfo.place_settlement, "Магазин 'Командор'")
    
    def test_checkinfo_to_dict(self):
        """Преобразование Checkinfo в словарь"""
        checkinfo = Checkinfo("01.01.26", "10:00", "ул. Киренского, 17", "Магазин 'Командор'")
        expected_dict = {
            "date": "01.01.26",
            "time": "10:00",
            "payment_address": "ул. Киренского, 17",
            "place_settlement": "Магазин 'Командор'"
        }
        self.assertDictEqual(checkinfo.to_dict(), expected_dict)


class TestCheckFunction(unittest.TestCase):
    def test_check_correct_calculation(self):
        self.assertTrue(check("25.00", "2.5", "10.0"))
    
    def test_check_correct_with_commas(self):
        self.assertTrue(check("25,00", "2,5", "10,0"))

    def test_check_invalid_calculation(self):
        self.assertFalse(check("25..00", "2.5", "10.0"))
    
    def test_check_invalid_with_commas(self):
        self.assertFalse(check("25,,00", "2,5", "10,0"))

    def test_check_corrent_total(self):
        self.assertTrue(check("25.00", "2.5", "10.0"))

    def test_check_invalid_total(self):
        self.assertFalse(check("abc", "2.5", "10.0"))

    def test_check_corrent_quantity(self):
        self.assertTrue(check("25.00", "2.5", "10.0"))
    
    def test_check_invalid_quantity(self):
        self.assertFalse(check("25.00", "abc", "10.0"))
    
    def test_check_corrent_price(self):
        self.assertTrue(check("25.00", "2.5", "10.0"))

    def test_check_invalid_price(self):
        self.assertFalse(check("25.00", "2.5", "abc"))


class TestDateTimeStringTest(unittest.TestCase):
    def test_correct_datetime_string(self):
        self.assertTrue(date_time_string_TEST("25.12.25 14:30 "))
    
    def test_invalid_datetime_no_space(self):
        self.assertFalse(date_time_string_TEST("25.12.25 14:30"))
    
    def test_invalid_datetime_wrong_format(self):
        self.assertFalse(date_time_string_TEST("25-12-25 14:30 "))
    
    def test_invalid_datetime_too_many_spaces(self):
        self.assertFalse(date_time_string_TEST("25.12.25  14:30 "))


class TestCreateProductFunction(unittest.TestCase):
    def setUp(self):
        self.prefix = "Мера кол-ва предмета расчета"
        self.len_prefix = len(self.prefix)
        self.info_about_check = []
    
    def test_create_product_with_commas(self):
        text_line = "Бананы 0,172 X 159,99 = 27,52 в т.ч. СУММА НДС Мера кол-ва предмета расчета кг"
        create_product(text_line, self.prefix, self.len_prefix, self.info_about_check)
        
        self.assertEqual(len(self.info_about_check), 1)
        product = self.info_about_check[0]

        self.assertEqual(product.quantity, 0.172)
        self.assertEqual(product.price, 159.99)
        self.assertEqual(product.total, 27.52)
    
    def test_create_product_no_nds(self):
        text_line = "Хлеб 1 X 35.99 = 35.99 Мера кол-ва предмета расчета шт"
        create_product(text_line, self.prefix, self.len_prefix, self.info_about_check)
        
        self.assertEqual(len(self.info_about_check), 1)
    
    def test_create_product_incorrect_calculation(self):
        text_line = "Яблоки 2.5 X 10.0 = 30.00 в т.ч. СУММА НДС Мера кол-ва предмета расчета кг"
        create_product(text_line, self.prefix, self.len_prefix, self.info_about_check)
        
        self.assertEqual(len(self.info_about_check), 0)
    
    def test_create_product_missing_total(self):
        text_line = "Яблоки 2.5 X 10.0 в т.ч. СУММА НДС Мера кол-ва предмета расчета кг"
        create_product(text_line, self.prefix, self.len_prefix, self.info_about_check)
        
        self.assertEqual(len(self.info_about_check), 0)


class TestInDictFunction(unittest.TestCase):
    def test_in_dict_full_data(self):
        checkinfo = Checkinfo("25.12.25", "14:30", "ул. Борисова, 17", "Магазин Командор")
        product1 = Product("Яблоки", 2.5, 100.0, "кг")
        product2 = Product("Молоко", 1, 80.0, "л")
        
        result = in_dict([checkinfo, product1, product2])
        
        self.assertEqual(len(result["products"]), 2)
        self.assertEqual(result["total_sum"], 330.0)
        self.assertEqual(result["check_info"]["date"], "25.12.25")
        self.assertEqual(result["products"][0]["name"], "Яблоки")
        self.assertEqual(result["products"][1]["name"], "Молоко")


class TestProductsInformationIntegration(unittest.TestCase):
    
    def test_products_information_correct_data(self):
        test_data = """
        check.ofd.ru ДАТА ВЫДАЧИ 25.12.25 14:30 АДРЕС РАСЧЁТОВ ул. Киренского, 17 МЕСТО РАСЧЁТОВ Магазин Командор КАССИР
        ПРИЗНАК СПОСОБА РАСЧЕТА ПРИЗНАК ПРЕДМЕТА РАСЧЕТА
        Яблоки 2.5 X 100.00 = 250.00 в т.ч. СУММА НДС Мера кол-ва предмета расчета кг
        Творог 1 X 80,00 = 80.00 в т.ч. СУММА НДС Мера кол-ва предмета расчета шт
        Результат проверки сведений Идентификатор ФОИВ Дата/Номер док. основания Отраслевой реквизит ПОЛНЫЙ РАСЧЕТ
        """
        
        result = products_information(test_data)
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

        self.assertIsInstance(result[0], Checkinfo)
        self.assertEqual(result[0].date, "25.12.25")
        

        if len(result) > 1:
            self.assertIsInstance(result[1], Product)
    
    def test_products_information_missing_checkofd(self):
        test_data = "ДАТА ВЫДАЧИ 25.12.25 14:30"
        
        result = products_information(test_data)

        self.assertIsNone(result)
    
    def test_products_information_missing_date(self):
        test_data = "check.ofd.ru АДРЕС РАСЧЁТОВ ул. "
        
        result = products_information(test_data)
        self.assertIsNone(result)


class TestJsonFunctions(unittest.TestCase):
    def test_IN_JSON(self):
        checkinfo = Checkinfo("25.12.25", "14:30", "ул. Киренского, 17", "Магазин Командор")
        product = Product("Яблоки", 2.5, 100.0, "кг")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.json")

            with patch('builtins.open', mock_open()) as mock_file:
                IN_JSON([checkinfo, product])
                
                mock_file.assert_called_with('check_data.json', 'w', encoding='utf-8')


sys.modules['register'] = MagicMock()


class TestAdaptiveMobileLoginApp(unittest.TestCase):

    def setUp(self):
        self.patcher_tk = patch('tkinter.Tk')
        self.mock_tk = self.patcher_tk.start()
        self.mock_tk.return_value.winfo_screenwidth.return_value = 1920
        self.mock_tk.return_value.winfo_screenheight.return_value = 1080
        with patch('tkinter.Label'), patch('tkinter.Button'), \
                patch('tkinter.Frame'), patch('tkinter.Entry'):
            self.app = AdaptiveMobileLoginApp()
            self.app.login_entry = MagicMock()
            self.app.password_entry = MagicMock()
            self.app.eye_btn = MagicMock()

    def tearDown(self):
        self.patcher_tk.stop()

    def test_scaling_factors(self):
        """Тест: Проверка расчета коэффициентов масштабирования"""
        self.assertGreater(self.app.overall_scale, 0)
        base_size = 100
        scaled = self.app.get_scaled_size(base_size)
        expected = int(base_size * self.app.overall_scale)
        self.assertEqual(scaled, expected)

    def test_auth_logic_success(self):
        """Тест: Успешная авторизация (проверка чтения файла)"""
        fake_file_content = "admin:12345\nuser:password"

        with patch("builtins.open", mock_open(read_data=fake_file_content)):
            with patch("os.path.exists", return_value=True):
                # Вызываем только логику проверки
                result = self.app.authenticate_user("admin", "12345")
                self.assertTrue(result, "Авторизация должна пройти для admin:12345")

    def test_auth_logic_failure(self):
        """Тест: Неудачная авторизация (неверный пароль)"""
        fake_file_content = "admin:12345"

        with patch("builtins.open", mock_open(read_data=fake_file_content)):
            with patch("os.path.exists", return_value=True):
                result = self.app.authenticate_user("admin", "wrong_pass")
                self.assertFalse(result, "Авторизация не должна пройти с неверным паролем")

    def test_auth_no_file(self):
        """Тест: Если файла пользователей нет"""
        with patch("os.path.exists", return_value=False):
            result = self.app.authenticate_user("admin", "12345")
            self.assertFalse(result, "Если файла нет, авторизация должна быть False")

    @patch('tkinter.messagebox.showwarning')
    def test_login_empty_fields(self, mock_mb):
        """Тест: Попытка входа с пустыми полями"""
        self.app.login_entry.get.return_value = ""
        self.app.password_entry.get.return_value = ""

        self.app.login()

        mock_mb.assert_called_once()
        args, _ = mock_mb.call_args
        self.assertIn("Заполните все поля", args[1])
    

