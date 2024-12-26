import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_string = os.getenv("SESSION_STRING")  # SESSION_STRING من المتغيرات البيئية

# إنشاء العميل باستخدام الجلسة المخزنة
client = TelegramClient("session_name", api_id, api_hash)

# تحميل الجلسة باستخدام string
client.session = client.session.__class__(client.loop, session_string)

# متغير لتفعيل الحفظ التلقائي
is_active = False

@client.on(events.NewMessage(pattern=".تشغيل الحفظ"))
async def enable_auto_save(event):
    global is_active
    is_active = True
    await event.reply("✅ تم تشغيل الحفظ التلقائي.")

@client.on(events.NewMessage(pattern=".إيقاف الحفظ"))
async def disable_auto_save(event):
    global is_active
    is_active = False
    await event.reply("❌ تم إيقاف الحفظ التلقائي.")

@client.on(events.NewMessage(pattern=".تحميل (.+)"))
async def download_messages(event):
    if not is_active:
        await event.reply("❌ يجب تشغيل الحفظ التلقائي أولاً باستخدام .تشغيل الحفظ")
        return

    entity_name = event.pattern_match.group(1)
    try:
        entity = await client.get_entity(entity_name)

        async for message in client.iter_messages(entity, limit=10):
            if message.text:
                await client.send_message("me", f"📩 {message.text}")
            elif message.media:
                file_path = await message.download_media()
                await client.send_message("me", f"📂 تم تحميل الوسائط: {file_path}")

        await event.reply("✅ تم حفظ الرسائل والوسائط بنجاح.")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء تحميل الرسائل: {e}")

async def main():
    await client.start()
    print(f"✅ تم تسجيل الدخول بنجاح.")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
