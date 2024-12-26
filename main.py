import os
from telethon import TelegramClient, events

# إعداد متغيرات Heroku أو ملء القيم يدويًا
api_id = int(os.getenv("API_ID"))  # استبدل بـ API ID الخاص بك
api_hash = os.getenv("API_HASH")  # استبدل بـ API Hash الخاص بك
session_string = os.getenv("SESSION_STRING")  # جلب الجلسة من البيئة إذا كانت موجودة

# إذا كانت الجلسة موجودة، استخدمها، وإذا لم تكن موجودة، استخدم الجلسة العادية
if session_string:
    client = TelegramClient("session_name", api_id, api_hash).from_string(session_string)
else:
    client = TelegramClient("session_name", api_id, api_hash)

# متغير لتفعيل الحفظ التلقائي
is_active = False

# تفعيل الحفظ التلقائي
@client.on(events.NewMessage(pattern=".تشغيل الحفظ"))
async def enable_auto_save(event):
    """
    تفعيل خاصية الحفظ التلقائي.
    """
    global is_active
    is_active = True
    await event.reply("✅ تم تشغيل الحفظ التلقائي.")

# إيقاف الحفظ التلقائي
@client.on(events.NewMessage(pattern=".إيقاف الحفظ"))
async def disable_auto_save(event):
    """
    إيقاف خاصية الحفظ التلقائي.
    """
    global is_active
    is_active = False
    await event.reply("❌ تم إيقاف الحفظ التلقائي.")

# تحميل الرسائل من قناة أو مجموعة
@client.on(events.NewMessage(pattern=".تحميل (.+)"))
async def download_messages(event):
    """
    تحميل رسائل قناة أو مجموعة.
    """
    if not is_active:
        await event.reply("❌ يجب تشغيل الحفظ التلقائي أولاً باستخدام .تشغيل الحفظ")
        return

    # استخراج رابط القناة أو اسم المجموعة
    entity_name = event.pattern_match.group(1)
    try:
        # الحصول على الكيان (القناة/المجموعة)
        entity = await client.get_entity(entity_name)

        # تحميل آخر 10 رسائل (يمكنك تغيير العدد)
        async for message in client.iter_messages(entity, limit=10):
            # حفظ الرسالة النصية أو وسائط الرسالة
            if message.text:  # إذا كانت الرسالة نصية
                await client.send_message("me", f"📩 {message.text}")
            elif message.media:  # إذا كانت الرسالة تحتوي على وسائط
                file_path = await message.download_media()
                await client.send_message("me", f"📂 تم تحميل الوسائط: {file_path}")

        await event.reply("✅ تم حفظ الرسائل والوسائط بنجاح.")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء تحميل الرسائل: {e}")

# الرد على رابط رسالة
@client.on(events.NewMessage(pattern="https://t.me/.+"))
async def reply_to_message(event):
    """
    الرد على رسالة قناة أو مجموعة باستخدام الرابط.
    """
    if not is_active:
        await event.reply("❌ يجب تشغيل الحفظ التلقائي أولاً باستخدام .تشغيل الحفظ")
        return

    try:
        message_link = event.text
        # الحصول على الرسالة عبر الرابط
        message = await client.get_messages(message_link)

        if message.text:  # إذا كانت الرسالة نصية
            await client.send_message("me", f"📩 تم حفظ الرسالة النصية: {message.text}")
        elif message.media:  # إذا كانت الرسالة تحتوي على وسائط
            file_path = await message.download_media()
            await client.send_message("me", f"📂 تم تحميل الوسائط: {file_path}")

        await event.reply("✅ تم حفظ الرسالة بنجاح.")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء حفظ الرسالة: {e}")

# بدء الجلسة
async def main():
    await client.start()
    print(f"✅ تم تسجيل الدخول بنجاح.")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
