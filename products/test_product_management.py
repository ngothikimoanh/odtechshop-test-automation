import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import db_connection

# URLs
LOGIN_URL = "http://localhost/auth/login"

# Khởi tạo database
db = db_connection.get_db_connection()
cursor = db.cursor()

# Khởi tạo WebDriver
service = Service("geckodriver.exe")
driver = webdriver.Firefox(service=service)
driver.maximize_window()
driver.implicitly_wait(5)  # Chờ tối đa 5 giây khi tìm element


def fill_input(field, value):
    field.clear()
    field.send_keys(value)
    WebDriverWait(driver, 5).until(lambda d: field.get_attribute("value") == value)
    return field.get_attribute("value")


def login():
    """Thực hiện đăng nhập vào hệ thống."""
    driver.get(LOGIN_URL)
    time.sleep(3)
    # Tìm form đăng nhập
    form = WebDriverWait(driver, 5).until(lambda d: d.find_element("xpath", '//form[@method="post"]'))

    # Điền số điện thoại và mật khẩu
    phone_input = form.find_element("xpath", './/input[@name="phone_number"]')
    phone_filled = fill_input(phone_input, "0784253460")

    password_input = form.find_element("xpath", './/input[@name="password"]')
    password_filled = fill_input(password_input, "Kimoanh2003@")

    # Click nút đăng nhập
    login_button = form.find_element("xpath", './/button[@type="submit"]')
    login_button.click()

    time.sleep(3)  # Chờ trang load

    if driver.current_url != LOGIN_URL:
        print(f"✅ Đăng nhập thành công! Chuyển đến {driver.current_url}")
    else:
        print("❌ Đăng nhập thất bại!")


def validate_test_case(name, price, image_path):
    """Kiểm tra lỗi test case theo logic của hệ thống"""
    errors = []
    if not name:
        errors.append("⚠ Lỗi: Thiếu tên sản phẩm")

    # Kiểm tra giá sản phẩm
    try:
        price = int(price)
        if price < 0:
            errors.append("⚠ Lỗi: Giá trị không được âm")
        elif price == 0:
            errors.append("⚠ Lỗi: Giá trị không được bằng 0")
    except ValueError:
        errors.append("⚠ Lỗi: Giá trị không hợp lệ")

    if image_path:
        abs_image_path = os.path.abspath(image_path)
        if not os.path.exists(abs_image_path):
            errors.append(f"⚠ Lỗi: File ảnh không tồn tại - {abs_image_path}")
        elif not image_path.lower().endswith((".png", ".jpg", ".jpeg")):
            errors.append("⚠ Lỗi: Định dạng file ảnh không hợp lệ (chỉ chấp nhận JPG, PNG)")

    return errors


def run_test_case(name, price, image_path):
    login()
    time.sleep(5)
    admin_button = driver.find_element("xpath", '//a[@href="/users/"]')
    admin_button.click()
    product_manager_button = driver.find_element("xpath", '//a[@href="/products/"]')
    product_manager_button.click()

    form = WebDriverWait(driver, 5).until(lambda d: d.find_element("xpath", '//form[@enctype="multipart/form-data"]'))

    # Điền tên sản phẩm
    input_name = form.find_element("xpath", './/input[@name="name"]')
    fill_input(input_name, name)

    # Điền giá
    input_price = form.find_element("xpath", './/input[@name="price"]')
    fill_input(input_price, str(price))

    # Upload ảnh
    if image_path:
        abs_image_path = os.path.abspath(image_path)
        if os.path.exists(abs_image_path):
            input_image = form.find_element("xpath", './/input[@name="thumbnail_image"]')
            input_image.send_keys(abs_image_path)
        else:
            print(f"⚠ Lỗi: File ảnh không tồn tại - {abs_image_path}")

    # Submit form
    submit_button = form.find_element("xpath", './/button[@type="submit"]')
    submit_button.click()

    driver.get("http://localhost/products/")

    error_messages = validate_test_case(name, price, image_path)
    if name and price and name.lower() not in driver.page_source.lower():
        error_messages.append("⚠ Lỗi: Sản phẩm không hiển thị trong danh sách (có thể do trùng tên)")

    # Hiển thị kết quả test case
    print("=" * 60)
    print(f"🔎 **Chạy Test Case**: {name} - {price}")

    if error_messages:
        print(f"❌ Test Case FAILED: {name} - {price}")
        for msg in error_messages:
            print("   " + msg)
    else:
        print(f"✅ Test Case PASSED: {name} - {price}")

    time.sleep(2)  # Chờ 2 giây trước khi chạy test case tiếp theo

    print(f"✅ Thêm sản phẩm: {name} - {price}")
    time.sleep(2)


def main():

    test_cases = [
        ("iPhone 14 Pro Max", 30000000, "media/iphone_14_pro_max.png"),  # hợp lệ
        ("iPhone 14 Pro Max", 30000000, "media/iphone_14_pro_max.png"),  # trùng key
        ("", 30000000, ""),  # trống tên sản phẩm
        ("iPhone 16 Pro Max", "", "media/iphone-16-pro-tu-nhien-1.png"),  # trống giá
        ("iPhone 16 Pro Max", "50000000d", ""),  # sai định dạng giá
        ("iPhone 16 Pro Max", -50000000, ""),  # sai định dạng giá
        ("iPhone 16 Pro Max", 50000.000, ""),  # sai định dạng giá
        ("iPhone 16 Pro Max", 0, ""),  # sai định dạng giá
        ("iPhone 16 Pro Max", 1, "media/speaking-writing-sample-tests IIG.pdf"),  # sai định dạng ảnh
    ]

    for case in test_cases:
        run_test_case(*case)
        time.sleep(3)  # Chờ giữa các test case


if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()  # Đóng trình duyệt
        cursor.close()
        db.close()
