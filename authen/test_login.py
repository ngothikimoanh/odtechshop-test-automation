import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import db_connection

website = "http://localhost/auth/login"

db = db_connection.get_db_connection()
cursor = db.cursor()

# Initialize WebDriver
service = Service("geckodriver.exe")
driver = webdriver.Firefox(service=service)
driver.maximize_window()
driver.implicitly_wait(5)


def fill_input(field, value):
    field.clear()
    field.send_keys(value)
    WebDriverWait(driver, 3).until(lambda d: field.get_attribute("value") == value)
    return field.get_attribute("value")


def is_login_successful():
    time.sleep(2)  # Chờ trang xử lý
    return driver.current_url != website


def run_test_case(phone_number, password):

    driver.get(website)
    form = driver.find_element("xpath", '//form[@method="post"]')

    phone_input = form.find_element("xpath", './/input[@name="phone_number"]')
    phone_filled = fill_input(phone_input, phone_number)
    password_input = form.find_element("xpath", './/input[@name="password"]')
    password_filled = fill_input(password_input, password)

    login_button = form.find_element("xpath", './/button[@type="submit"]')
    login_button.click()

    print(phone_filled, password_filled)

    print(f"📲 Testing login for: {phone_number} | {password}")

    if is_login_successful():
        print("✅ Đăng nhập thành công!")
    else:
        if phone_number == "" or password == "":
            print("❌ Đăng nhập thất bại! Lỗi: Tài khoản hoặc mật khẩu không được để trống.")
        elif phone_number == "0784253466" and password != "P@ssw0rd1":
            print("❌ Đăng nhập thất bại! Lỗi: Sai mật khẩu.")
        elif phone_number == "0905656187":
            print("❌ Đăng nhập thất bại! Lỗi: Tài khoản không tồn tại.")
        else:
            print("❌ Đăng nhập thất bại! Lỗi không xác định.")


# Running multiple test cases
def main():
    test_cases = [
        ("0784253466", "wrong_pass"),  # Sai mật khẩu
        ("0905656187", "valid_pass"),  # Tài khoản không tồn tại
        ("", "valid_pass"),  # Bỏ trống tài khoản
        ("0784253466", ""),  # Bỏ trống mật khẩu
        ("0784253467", "P@ssw0rd1"),  # Đăng nhập thành công
    ]

    for case in test_cases:
        run_test_case(*case)
        time.sleep(3)  # Wait between test cases


if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
        cursor.close()
        db.close()
