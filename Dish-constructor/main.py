from auth import AdaptiveMobileLoginApp
import unittest
import os
import sys
import test_runner
sys.path.insert(0, '.')


if __name__ == "__main__":
    try:
        unittest.main(module='test_runner', exit=False, verbosity=2)
    except ImportError as e:
        print(f"Ошибка: Не найден файл с тестами: {e}")

    app = AdaptiveMobileLoginApp()
    app.run()
