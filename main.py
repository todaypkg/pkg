import os
import platform
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendMessageRequest

# إعداد متغيرات Telegram API
api_id = 28534158  # استبدل بـ api_id الخاص بك
api_hash = 'b21e141e7ba0b22f9eddb64fd4799733'  # استبدل بـ api_hash الخاص بك
username = 'baniqi'

# إنشاء العميل
client = TelegramClient(username, api_id, api_hash, device_model='baniqi')

# التأكد من وجود المجلد لحفظ الوسائط
os.makedirs("saved_media", exist_ok=True)

@client.on(events.NewMessage)
async def handle_message(event):
    # تحقق إذا كانت الرسالة تحتوي على صورة
    if event.photo:
        sender = await event.get_sender()
        photo = await event.download_media(file="saved_media/")

        # معلومات النظام
        system_info = platform.system()
        node_name = platform.node()

        # صيغة الرسالة
        custom_message = f"\U0001F496 {username} جابلك صورة حب! \U0001F496\n"
        custom_message += f"\u2728 الجهاز: {node_name}\n\u2728 النظام: {system_info}"

        # إرسال الصورة مع الرسالة إلى الرسائل المحفوظة
        await client.send_message('me', custom_message)
        await client.send_file('me', photo, caption="\U0001F4E3 وين صورك؟ يلا شارك!")

    # تحقق إذا كانت الرسالة تحتوي على فيديو
    elif event.video:
        sender = await event.get_sender()
        video = await event.download_media(file="saved_media/")

        # معلومات النظام
        system_info = platform.system()
        node_name = platform.node()

        # صيغة الرسالة
        custom_message = f"\U0001F4F9 {username} جابلك فيديو حب! \U0001F4F9\n"
        custom_message += f"\u2728 الجهاز: {node_name}\n\u2728 النظام: {system_info}"

        # إرسال الفيديو مع الرسالة إلى الرسائل المحفوظة
        await client.send_message('me', custom_message)
        await client.send_file('me', video, caption="\U0001F4E3 وين فيديوهاتك؟ يلا شارك!")

# تشغيل العميل
with client:
    print("البوت قيد التشغيل باسم baniqi...")
    client.run_until_disconnected()
