import os
import requests
from telethon import TelegramClient, events
from PIL import Image
from realesrgan import RealESRGAN

# إعداد معلومات Telegram API
BOT_TOKEN = os.getenv("BOT_TOKEN")  # ضع توكن البوت الخاص بك هنا
API_ID = int(os.getenv("API_ID", "0"))  # ضع الـ API ID الخاص بك هنا
API_HASH = os.getenv("API_HASH")  # ضع الـ API Hash الخاص بك هنا

# رابط الأوزان واسم الملف
WEIGHTS_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.3.0/RealESRGAN_x4plus.pth"
WEIGHTS_FILE = "weights/RealESRGAN_x4plus.pth"

# التأكد من تحميل الأوزان
def download_weights():
    if not os.path.exists(WEIGHTS_FILE):
        print("Downloading weights...")
        os.makedirs(os.path.dirname(WEIGHTS_FILE), exist_ok=True)
        response = requests.get(WEIGHTS_URL, stream=True)
        with open(WEIGHTS_FILE, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Weights downloaded successfully!")

# تحسين الصورة باستخدام Real-ESRGAN
def enhance_image(input_image_path, output_image_path):
    model = RealESRGAN(device="cpu", scale=4)
    model.load_weights(WEIGHTS_FILE)

    with Image.open(input_image_path) as img:
        sr_image = model.predict(img)
        sr_image.save(output_image_path)

# بدء تشغيل البوت
bot = TelegramClient("bot_session", API_ID, API_HASH)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond("أهلاً بك! أرسل لي صورة وسأقوم بتحسينها باستخدام الذكاء الاصطناعي 🚀.")

@bot.on(events.NewMessage(incoming=True, func=lambda e: e.photo))
async def handle_image(event):
    sender = await event.get_sender()
    await event.reply("جارٍ معالجة الصورة، يرجى الانتظار... ⏳")

    # تنزيل الصورة
    input_image_path = await event.download_media(file="input_image.jpg")
    output_image_path = "output_image.jpg"

    try:
        # تحسين الصورة
        enhance_image(input_image_path, output_image_path)

        # إرسال الصورة المحسّنة
        await bot.send_file(event.chat_id, output_image_path, caption="✨ تم تحسين الصورة بنجاح!")
    except Exception as e:
        await event.reply(f"حدث خطأ أثناء تحسين الصورة: {str(e)}")
    finally:
        # تنظيف الملفات
        if os.path.exists(input_image_path):
            os.remove(input_image_path)
        if os.path.exists(output_image_path):
            os.remove(output_image_path)

# بدء تشغيل البوت
async def main():
    print("Downloading weights if not already downloaded...")
    download_weights()

    print("Starting bot...")
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot is running...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
