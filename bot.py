import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from telegram import Bot, Update
from telegram.ext import CommandHandler, CallbackContext, Updater

# Khởi tạo bot
TOKEN = '6663862739:AAGGrwtk-8S1rkRU-Uyshx88Rdsts8e3j-0'
bot = Bot(token=TOKEN)


def capture_screenshot(wallet_address: str):
    # Khởi tạo trình duyệt với Selenium ở chế độ headless
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    # Truy cập trang web
    url = f"https://rugcheck.xyz/tokens/{wallet_address}"
    driver.get(url)

    # Đợi cho đến khi không còn phần tử nào có chữ "Loading Score"
    try:
        WebDriverWait(driver, 30).until_not(EC.text_to_be_present_in_element((By.XPATH, "//*[contains(text(), 'Loading Score')]"), "Loading Score"))
    except TimeoutException:
        print("Trang web không tải xong sau 30 giây.")
        driver.quit()
        return None

    # Chụp ảnh trang web
    screenshot_path = f"screenshot_{wallet_address}.png"
    driver.set_window_size(1200, 840)  # Đặt kích thước cửa sổ trình duyệt
    driver.save_screenshot(screenshot_path)

    # Đóng trình duyệt
    driver.quit()

    return screenshot_path


def rugcheck(update: Update, context: CallbackContext) -> None:
    # Lấy thông tin ví Solana từ lệnh
    wallet_address = " ".join(context.args)

    # Kiểm tra xem có ví Solana được cung cấp không
    if not wallet_address:
        update.message.reply_text("Vui lòng cung cấp ví Solana.")
        return

    # Chụp ảnh và gửi ảnh vào bot
    screenshot_path = capture_screenshot(wallet_address)
    if screenshot_path:
        with open(screenshot_path, 'rb') as photo:
            update.message.reply_photo(photo)
        # Xóa ảnh sau khi đã gửi
        os.remove(screenshot_path)
    else:
        update.message.reply_text("Đã có lỗi xảy ra khi chụp ảnh trang web.")


def main():
    # Khởi tạo Updater
    updater = Updater(TOKEN, use_context=True)

    # Thêm handler cho lệnh /rugcheck
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("rugcheck", rugcheck))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
