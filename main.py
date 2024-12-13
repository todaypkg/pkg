import os
import platform
import asyncio
from telethon import TelegramClient, events, sessions
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import InputMessagesFilterSelfDestruct

# إعداد المجلد لحفظ الوسائط
os.makedirs("saved_media", exist_ok=True)

# إعداد معلومات البوت عبر متغيرات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", "0"))  # يتم تعيين القيمة الافتراضية لـ 0 إذا لم يتم تعريف المتغير
API_HASH = os.getenv("API_HASH")

if not BOT_TOKEN or not API_ID or not API_HASH:
    raise ValueError("يرجى تحديد القيم الخاصة بـ BOT_TOKEN، API_ID، و API_HASH كمتغيرات بيئة.")

# قائمة الحسابات
accounts = []

# إنشاء البوت
bot = TelegramClient('bot_session', API_ID, API_HASH)

# دالة للتعامل مع الرسائل ذاتية التدمير
async def handle_self_destruct_message(client, event, username):
    if event.photo:
        photo = await event.download_media(file="saved_media/")
        system_info = platform.system()
        node_name = platform.node()

        custom_message = f"\U0001F496 {username} جابلك صورة حب ذاتية التدمير! \U0001F496\n"
        custom_message += f"\u2728 الجهاز: {node_name}\n\u2728 النظام: {system_info}"

        await client.send_message('me', custom_message)
        await client.send_file('me', photo, caption="\U0001F4E3 تم التقاط صورة ذاتية التدمير!")
    elif event.video:
        video = await event.download_media(file="saved_media/")
        system_info = platform.system()
        node_name = platform.node()

        custom_message = f"\U0001F4F9 {username} جابلك فيديو حب ذاتي التدمير! \U0001F4F9\n"
        custom_message += f"\u2728 الجهاز: {node_name}\n\u2728 النظام: {system_info}"

        await client.send_message('me', custom_message)
        await client.send_file('me', video, caption="\U0001F4E3 تم التقاط فيديو ذاتي التدمير!")

# بدء تشغيل الحساب الجديد
async def start_account(api_id, api_hash, phone, session_name):
    session = sessions.StringSession()
    client = TelegramClient(session, api_id, api_hash)
    
    await client.connect()
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(phone)
            print(f"تم إرسال رمز التحقق إلى {phone}")
            
            # انتظار إدخال رمز التحقق
            code = input(f"أدخل رمز التحقق للحساب {phone}: ")
            await client.sign_in(phone, code)

            if await client.is_user_authorized():
                print(f"تم تسجيل الدخول بنجاح للحساب {phone}")
        except SessionPasswordNeededError:
            password = input(f"أدخل كلمة مرور المصادقة الثنائية للحساب {phone}: ")
            await client.sign_in(password=password)
    
    accounts.append(client)
    client.add_event_handler(lambda event, acc=phone: handle_self_destruct_message(client, event, acc), events.NewMessage(incoming=True, filters=InputMessagesFilterSelfDestruct))
    await client.start()
    print(f"الحساب {phone} يعمل الآن.")

# تشغيل البوت
@bot.on(events.NewMessage(pattern='/add_account'))
async def add_account(event):
    await event.respond("أرسل المعلومات بالشكل التالي: API_ID|API_HASH|PHONE")

@bot.on(events.NewMessage)
async def handle_new_account(event):
    if '|' in event.raw_text:
        try:
            api_id, api_hash, phone = event.raw_text.split('|')
            await start_account(int(api_id), api_hash, phone, f"session_{phone}")
            await event.respond(f"تمت إضافة الحساب {phone} بنجاح!")
        except Exception as e:
            await event.respond(f"حدث خطأ أثناء إضافة الحساب: {str(e)}")
    else:
        await event.respond("صيغة غير صحيحة. يرجى المحاولة مرة أخرى.")

# تشغيل البوت وجميع الحسابات
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("البوت قيد التشغيل... أرسل /add_account لإضافة حساب جديد.")
    await bot.run_until_disconnected()

asyncio.run(main())
        
