import os
import time
from telethon import TelegramClient, events
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

# تثبيت ChromeDriver تلقائيًا
chromedriver_autoinstaller.install()

# إعداد متغيرات Heroku
api_id = int(os.getenv("API_ID"))  # تأكد أن API_ID مخزن كعدد صحيح
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME", "session_name")  # اسم الجلسة الافتراضي

# إنشاء جلسة Telethon باستخدام اسم الجلسة من Heroku Config Vars
client = TelegramClient(session_name, api_id, api_hash)

# إعداد خيارات Selenium لتشغيل Chrome في وضع headless
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# متغير لتفعيل الحفظ التلقائي
is_active = False

# تفعيل الحفظ التلقائي
@client.on(events.NewMessage(pattern=".تشغيل الحفظ"))
async def enable_auto_save(event):
    global is_active
    is_active = True
    await event.reply("✅ تم تشغيل الحفظ التلقائي.")

# تحميل الوسائط من قناة باستخدام Selenium
@client.on(events.NewMessage(pattern=".تحميل (.+)"))
async def download_from_channel(event):
    if not is_active:
        await event.reply("❌ يجب تشغيل الحفظ التلقائي أولاً باستخدام .تشغيل الحفظ")
        return

    channel_url = event.pattern_match.group(1)
    try:
        # فتح رابط القناة في المتصفح
        driver.get(channel_url)
        time.sleep(5)  # انتظار تحميل الصفحة

        # البحث عن الرسائل التي تحتوي على وسائط
        messages = driver.find_elements(By.CSS_SELECTOR, ".message")
        for message in messages:
            try:
                download_button = message.find_element(By.CSS_SELECTOR, ".download-button")
                download_button.click()
                time.sleep(2)  # انتظار التنزيل
                
                # إرسال إشعار بأن الوسائط تم حفظها
                await client.send_message("me", "✅ تم حفظ الوسائط.")
            except Exception as e:
                print(f"خطأ أثناء محاولة التنزيل: {e}")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء تحميل القناة: {e}")
    finally:
        driver.quit()  # تأكد من إغلاق المتصفح بعد الانتهاء

# بدء الجلسة
async def main():
    await client.start()
    print(f"✅ تم تسجيل الدخول باستخدام الجلسة: {session_name}")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
    
