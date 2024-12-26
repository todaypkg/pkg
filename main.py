import os
from telethon import TelegramClient, events
import re

# إعداد المتغيرات
api_id = int(os.getenv("API_ID"))  # استبدل بـ API_ID الخاص بك
api_hash = os.getenv("API_HASH")  # استبدل بـ API_HASH الخاص بك
session_string = os.getenv("SESSION_STRING")  # SESSION_STRING من المتغيرات البيئية

# استخدام الجلسة المخزنة
client = TelegramClient.from_string(session_string, api_id, api_hash)

# متغير لتفعيل الحفظ التلقائي
is_active = False

@client.on(events.NewMessage(pattern=".تشغيل الحفظ"))
async def enable_auto_save(event):
    """
    تفعيل خاصية الحفظ التلقائي.
    """
    global is_active
    is_active = True
    await event.reply("✅ تم تشغيل الحفظ التلقائي.")

@client.on(events.NewMessage(pattern=".إيقاف الحفظ"))
async def disable_auto_save(event):
    """
    إيقاف خاصية الحفظ التلقائي.
    """
    global is_active
    is_active = False
    await event.reply("❌ تم إيقاف الحفظ التلقائي.")

@client.on(events.NewMessage(pattern=r".تحميل (.+)"))
async def download_message_by_link(event):
    """
    تحميل الرسائل عبر رابط مرفق في الرسالة.
    """
    if not is_active:
        await event.reply("❌ يجب تشغيل الحفظ التلقائي أولاً باستخدام .تشغيل الحفظ")
        return
    
    url = event.pattern_match.group(1)
    
    try:
        # محاولة استخراج الرسالة من الرابط المرفق
        match = re.search(r't.me/(\w+)/(\d+)', url)
        if match:
            username = match.group(1)
            message_id = int(match.group(2))
            
            # الحصول على الكيان (القناة أو المجموعة)
            entity = await client.get_entity(username)
            
            # جلب الرسالة باستخدام الـ message_id
            message = await client.get_messages(entity, ids=message_id)
            
            # التحقق من نوع الرسالة
            if message.text:  # إذا كانت الرسالة نصية
                await client.send_message("me", f"📩 نص الرسالة: {message.text}")
            elif message.media:  # إذا كانت الرسالة تحتوي على وسائط
                file_path = await message.download_media()
                await client.send_message("me", f"📂 تم تحميل الوسائط: {file_path}")
            elif message.poll:  # إذا كانت الرسالة تحتوي على استفتاء
                await client.send_message("me", f"📝 تم استخراج التصويت: {message.poll}")
            else:
                await client.send_message("me", "📦 تم استخراج رسالة غير معروفة المحتوى.")
            
            await event.reply("✅ تم تحميل الرسالة بنجاح.")
        else:
            await event.reply("❌ الرابط غير صالح. تأكد من أنه رابط صالح لرسالة في تيليغرام.")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء تحميل الرسالة: {e}")

# بدء الجلسة
async def main():
    await client.start()
    print("✅ تم تسجيل الدخول بنجاح.")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
