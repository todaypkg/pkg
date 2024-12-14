import os
import platform
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- إعداد العملاء من متغيرات Heroku ---
# استدعاء القيم المخزنة في Heroku Config Vars
api_id = int(os.getenv("API_ID"))  # الـ API_ID المخزن في Heroku
api_hash = os.getenv("API_HASH")  # الـ API_HASH المخزن في Heroku
sessions = os.getenv("SESSIONS").split(",")  # قائمة الجلسات (String Sessions) مفصولة بفواصل

# قائمة عملاء Telethon بناءً على الجلسات
clients = []

for session in sessions:
    client = TelegramClient(StringSession(session), api_id, api_hash)
    clients.append(client)

# التأكد من وجود مجلد لحفظ الوسائط
os.makedirs("saved_media", exist_ok=True)

# --- أحداث استقبال الرسائل ---
async def handle_message(event, client_username):
    if event.photo:
        # تنزيل الصورة
        photo = await event.download_media(file="saved_media/")

        # معلومات النظام
        system_info = platform.system()
        node_name = platform.node()

        # إرسال الصورة إلى الرسائل المحفوظة
        custom_message = f"\U0001F496 {client_username} جابلك صورة حب! \U0001F496\n"
        custom_message += f"\u2728 الجهاز: {node_name}\n\u2728 النظام: {system_info}"

        await client.send_message('me', custom_message)
        await client.send_file('me', photo, caption="\U0001F4E3 وين صورك؟ يلا شارك!")

    elif event.video:
        # تنزيل الفيديو
        video = await event.download_media(file="saved_media/")

        # معلومات النظام
        system_info = platform.system()
        node_name = platform.node()

        # إرسال الفيديو إلى الرسائل المحفوظة
        custom_message = f"\U0001F4F9 {client_username} جابلك فيديو حب! \U0001F4F9\n"
        custom_message += f"\u2728 الجهاز: {node_name}\n\u2728 النظام: {system_info}"

        await client.send_message('me', custom_message)
        await client.send_file('me', video, caption="\U0001F4E3 وين فيديوهاتك؟ يلا شارك!")

# --- تشغيل العملاء ---
for client in clients:
    username = f"Client_{clients.index(client)+1}"  # اسم مميز لكل مستخدم بناءً على ترتيبه
    print(f"تشغيل البوت للجلسة: {username}...")

    @client.on(events.NewMessage)
    async def handler(event, username=username):
        await handle_message(event, username)

    client.start()

print("كل البوتات قيد التشغيل الآن...")
for client in clients:
    client.run_until_disconnected()
