import re
import time

import psycopg2
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait

website = "http://localhost/auth/register"

# Thông tin kết nối cơ sở dữ liệu
db = psycopg2.connect(
    dbname="od-tech-shop-local",
    user="od-tech-shop-user",
    password="od-tech-shop-password",
    host="localhost",
    port="5432",
)
cursor = db.cursor()

# Initialize WebDriver
service = Service("geckodriver.exe")
driver = webdriver.Firefox(service=service)
driver.maximize_window()
driver.implicitly_wait(5)


def is_user_exist(phone_number):
    cursor.execute("SELECT phone_number FROM users WHERE phone_number = %s LIMIT 1", (phone_number,))
    return cursor.fetchone() is not None


def fill_input(field, value):
    field.send_keys(value)
    WebDriverWait(driver, 3).until(lambda d: field.get_attribute("value") == value)
    return field.get_attribute("value")


def validate_phone(phone_number):

    phone_pattern = r"0\d{9,11}|84\d{8,10}"
    repeated_pattern = r"^(\d)\1+$"

    if re.fullmatch(phone_pattern, phone_number) and not re.fullmatch(repeated_pattern, phone_number):
        print(f"{phone_number}: ✅ Hợp lệ")
        return True
    else:
        print(f"{phone_number}: ❌ Không hợp lệ")
        return False


def validate_password(password):
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])\S{8,}$"
    if re.fullmatch(pattern, password):
        print(f"{password}: ✅ Hợp lệ")
        return True
    else:
        print(f"{password}: ❌ Không hợp lệ")
        return False


def run_test_case(phone_number, password, confirm_password):
    user_exist = is_user_exist(phone_number)

    if user_exist:
        print(f"{phone_number}: ⚠️  Số điện thoại đã tồn tại!")
        return
    else:
        if not user_exist:
            print("Tiến hành đăng ký tài khoản mới...")

    driver.get(website)
    form = driver.find_element("xpath", '//form[@method="post"]')

    phone_input = form.find_element("xpath", './/input[@name="phone_number"]')
    phone_filled = fill_input(phone_input, phone_number)
    password_input = form.find_element("xpath", './/input[@name="password"]')
    password_filled = fill_input(password_input, password)
    confirm_password_input = form.find_element("xpath", './/input[@id="password_confirm"]')
    confirm_password_filled = fill_input(confirm_password_input, confirm_password)

    register_button = form.find_element("xpath", './/button[@type="submit"]')
    register_button.click()

    print(phone_filled, password_filled, confirm_password_filled)
    phone_valid = validate_phone(phone_number)
    password_valid = validate_password(password)

    if confirm_password != password:
        print("Mật khẩu không khớp, nhập lại 📝")
    else:
        if (phone_valid and password_valid) and confirm_password == password:
            print("Mật khẩu khớp ✔️")

    if phone_valid and password_valid and confirm_password == password:
        print("Đăng kí thành công 🥰🥰")
    else:
        if not phone_valid:
            print("📵 Đăng kí thất bại: Số điện thoại không hợp lệ")
        if not password_valid:
            print("🔑 Đăng kí thất bại: Mật khẩu không hợp lệ")


# Running multiple test cases
def main():
    test_cases = [
        # test số điện thoại
        ("0898@134", "kimoanh2003", "kimoanh2003"),  # chứa kí tự đặc biệt
        ("0898abc134", "kimoanh2003", "kimoanh2003"),  # chứa kí tự
        ("abc0898134", "kimoanh2003", "kimoanh2003"),  # chứa kí tự
        ("0898134abc", "kimoanh2003", "kimoanh2003"),  # chứa kí tự
        ("0785 467765", "kimoanh2003", "kimoanh2003"),  # chứa khoảng trắng
        ("00000000000", "kimoanh2003", "kimoanh2003"),  # chứa nhiều số giống nhau
        ("089816715", "kimoanh2003", "kimoanh2003"),  # độ dài không đủ
        ("123456789", "kimoanh2003", "kimoanh2003"),  # sai định dạng
        ("0914406376", "kimoanh2003", "kimoanh2003"),  # đã tồn tại
        ("8478526498", "Kimoanh2003@", "Kimoanh2003@"),  # hợp lệ
        # test mật khẩu
        ("0784253466", "12345678", "12345678"),  # chỉ có số
        ("0784253466", "abcdefgh", "abcdefgh"),  # chỉ có chữ thường
        ("0784253466", "ABCDEFGH", "ABCDEFGH"),  # chỉ có chữ hoa
        ("0784253466", "@#$%^&*!", "@#$%^&*!"),  # chỉ có kí tự
        ("0784253466", "ABCD1234", "ABCD1234"),  # không có chữ thường và kí tự đặc biệt
        ("0784253466", "1234@#$%", "1234@#$%"),  # không có chữ hoa và chữ thường
        ("0784253466", "abcd@#$%", "abcd@#$%"),  # không có chữ hoa và số
        ("0784253466", "abcdABCD", "abcdABCD"),  # không có số và kí tự đặc biệt
        ("0784253466", "ABCD@#$%", "ABCD@#$%"),  # không có số và chữ thường
        ("0784253466", "P@ss w0rd1", "P@ss w0rd1"),  # chứa khoảng cách
        # test confirm pass
        ("0784253466", "P@ssw0rd1", ""),  # bỏ trống
        ("0784253466", "P@ssw0rd1", "L@ssw0rd1"),  # Không khớp
        ## hợp lệ
        ("0784253466", "P@ssw0rd1", "P@ssw0rd1"),  # hợp lệ
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
        db.close()
