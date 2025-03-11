import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.firefox.service import Service

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
driver.implicitly_wait(7)  # Chờ tối đa 5 giây khi tìm element


def fill_input(field, value):
    field.clear()
    field.send_keys(value)
    time.sleep(3)
    return field.get_attribute("value")


def login():
    """Đăng nhập vào hệ thống."""
    driver.get(LOGIN_URL)
    form = driver.find_element("xpath", '//form[@method="post"]')

    phone_input = form.find_element("xpath", './/input[@name="phone_number"]')
    fill_input(phone_input, "0784253460")
    password_input = form.find_element("xpath", './/input[@name="password"]')
    fill_input(password_input, "Kimoanh2003@")

    login_button = form.find_element("xpath", './/button[@type="submit"]')
    login_button.click()
    time.sleep(2)


def navigate_to_product_manager():
    """Đi tới trang quản lý sản phẩm."""
    admin_button = driver.find_element("xpath", '//a[@href="/users/"]')
    admin_button.click()
    products_manager_button = driver.find_element("xpath", '//a[@href="/products/"]')
    products_manager_button.click()


def validate_test_case(name, price, thumbnail_image):
    errors = []
    if not name:
        errors.append("Tên sản phẩm không được để trống")
    if not price:
        errors.append("Giá sản phẩm không được để trống")
    elif not isinstance(price, int) or price < 1:
        errors.append("Giá sản phẩm phải là số nguyên dương")
    if thumbnail_image and not thumbnail_image.lower().endswith((".png", ".jpg", ".jpeg")):
        errors.append("Định dạng ảnh không hợp lệ")
    return errors


def is_product_exist(name):
    cursor.execute("SELECT name FROM products WHERE name = %s LIMIT 1", (name,))
    return cursor.fetchone() is not None


def add_product(name, price, thumbnail_image):
    """Thêm sản phẩm vào hệ thống."""

    form = driver.find_element("xpath", '//form[@enctype="multipart/form-data"]')
    name_input = form.find_element("xpath", './/input[@name="name"]')
    fill_input(name_input, name)
    time.sleep(2)  # Để đảm bảo input không bị lỗi delay
    price_input = form.find_element("xpath", './/input[@name="price"]')
    fill_input(price_input, price)

    if thumbnail_image:
        abs_thumbnail_image = os.path.abspath(thumbnail_image)
        if os.path.exists(abs_thumbnail_image):
            thumbnail_image = form.find_element("xpath", './/input[@name="thumbnail_image"]')
            thumbnail_image.send_keys(abs_thumbnail_image)
        else:
            print(f"⚠ Lỗi: File ảnh không tồn tại - {abs_thumbnail_image}")
    time.sleep(2)
    update_button = form.find_element("xpath", './/button[@type="submit"]')
    update_button.click()


def run_test_case(name, price, thumbnail_image):
    product_exist = is_product_exist(name)

    if product_exist:
        print(f"{name}: ⚠️  Sản phẩm đã tồn tại!")
        return
    else:
        if not product_exist:
            print("Tiến hành tạo sản phẩm mới.....")

    errors = validate_test_case(name, price, thumbnail_image)
    if name and price and name.lower() not in driver.page_source.lower():
        errors.append("⚠ Lỗi: Sản phẩm không hiển thị trong danh sách (có thể do trùng tên)")

    print("=" * 60)
    print(f"🔎 **Test Case**: {name} | Giá: {price} | Ảnh: {thumbnail_image or 'Không có'}")

    if errors:

        print(f"❌ Test Case FAILED: {name} - {price}")
        for msg in errors:
            print("   " + msg)
    else:
        print(f"✅ Test Case PASSED: {name} - {price}")

    add_product(name, price, thumbnail_image)


def main():
    """Chạy toàn bộ test case."""
    login()
    navigate_to_product_manager()
    test_cases = [
        ("", 30000000, ""),  # trống tên sản phẩm
        ("iPhone 16 Pro Max", "", ""),  # trống giá
        ("iPhone 16 Pro Max", "50000000d", ""),  # sai định dạng giá
        ("iPhone 16 Pro Max", -50000000, ""),  # giá không là số âm
        ("iPhone 16 Pro Max", 55.5, ""),  # không được là số thâp phân
        ("iPhone 16 Pro Max", 0, ""),  # giá không thể bằng 0
        ("iPhone 16 Pro Max", 1, "media/speaking-writing-sample-tests IIG.pdf"),  # sai định dạng ảnh
        ("iPhone 14 Pro Max", 30000000, "media/iphone_14_pro_max.png"),  # trùng key
        ("iPhone 16 Pro Max", 30000000, "media/iphone-16-pro-tu-nhien-1.png"),  # hợp lệ
    ]

    for case in test_cases:
        run_test_case(*case)
        time.sleep(3)


if __name__ == "__main__":
    main()
    driver.quit()
    cursor.close()
    db.close()
