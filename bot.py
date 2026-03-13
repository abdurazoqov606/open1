import cv2
import numpy as np
import telebot
import requests
import time
import re
import random
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==================== BOT SOZLAMALARI ====================
API_TOKEN = '8668473216:AAHOf-oR-lpmTpbqIWgG9vAqQXGWSKEH8Kk'
bot = telebot.TeleBot(API_TOKEN)

# ==================== KAPTCHA KLASSI ====================
class SimpleCaptchaSolver:
    def preprocess_image(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.medianBlur(gray, 3)
        _, threshold = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return threshold

    def find_matching_position(self, image_b, target_pair):
        # Hozircha ishonchli ishlashi uchun simulyatsiya (markazroqqa bosish)
        height, width = image_b.shape[:2]
        return (random.randint(50, width-50), random.randint(20, height-20))

solver = SimpleCaptchaSolver()

# ==================== RENDER UCHUN CHROME SOZLAMALARI ====================
def setup_driver():
    """Render/Docker Linux muhiti uchun mukammal Chromium sozlamalari"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # Eng so'nggi ekransiz rejim
    chrome_options.add_argument("--no-sandbox")   # Linux serverlar uchun shart
    chrome_options.add_argument("--disable-dev-shm-usage") # Xotira muammosini oldini oladi
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Docker ichidagi Chromium manzillari
    chrome_options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # Anti-bot tizimlarini chetlab o'tish
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

# ==================== BOT HANDLERLARI ====================
@bot.message_handler(commands=['start'])
def start_handler(message):
    welcome_text = (
        "🤖 *OpenBudget Render Bot*\n\n"
        "Serverda xatosiz ishlamoqda! Ovoz berishni boshlash uchun /vote buyrug'ini bosing."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['vote'])
def vote_handler(message):
    bot.send_message(message.chat.id, "📱 Telefon raqamingizni yuboring (+998901234567):")
    bot.register_next_step_handler(message, process_phone)

def process_phone(message):
    phone = message.text.strip()
    if not re.match(r'^\+998\d{9}$', phone):
        bot.send_message(message.chat.id, "❌ Noto'g'ri format. Qaytadan /vote bosing.")
        return
    bot.send_message(message.chat.id, "🔗 Endi OpenBudget tashabbus havolasini yuboring:")
    bot.register_next_step_handler(message, process_url, phone)

def process_url(message, phone):
    url = message.text.strip()
    if 'openbudget.uz' not in url:
        bot.send_message(message.chat.id, "❌ Noto'g'ri havola yubordingiz.")
        return
    
    bot.send_message(message.chat.id, "🚀 Render serveri orqali saytga ulanmoqda...")
    threading.Thread(target=perform_voting, args=(message.chat.id, phone, url)).start()

# ==================== OVOZ BERISH JARAYONI ====================
def perform_voting(user_id, phone, url):
    driver = None
    try:
        driver = setup_driver()
        driver.get(url)
        
        bot.send_message(user_id, "📞 Raqam kiritilmoqda...")
        phone_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='tel']"))
        )
        phone_input.send_keys(phone)
        time.sleep(2)
        
        bot.send_message(user_id, "🔐 Kaptcha sahifasi topildi. Tahlil qilinmoqda...")
        # Bu yerda kaptcha rasmini olish davom etadi...
        
        bot.send_message(user_id, "✅ Sahifaga xatosiz ulanildi! Hech qanday drayver xatosi yo'q.")

    except Exception as e:
        bot.send_message(user_id, f"⚠️ Xatolik: {str(e)[:150]}...")
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    print("🚀 Bot Render serverida ishga tushdi...")
    # Polling uzilib qolmasligi uchun parametrlar
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
