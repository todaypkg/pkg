import os
import json
import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from datetime import datetime
from telethon.sessions import StringSession

# إعداد القيم من البيئة
api_id = int(os.getenv("API_ID"))  # API_ID من المتغيرات البيئية
api_hash = os.getenv("API_HASH")  # API_HASH من المتغيرات البيئية
phone = os.getenv("PHONE")  # رقم الهاتف من المتغيرات البيئية
session_string = os.getenv("SESSION_STRING")  # الجلسة المخزنة كـ StringSession من المتغيرات البيئية

# إنشاء الجلسة مع Telethon
client = TelegramClient(StringSession(session_string), api_id, api_hash)

# الكود لتحويل التاريخ إلى صيغة يمكن تخزينها
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, bytes):
            return list(o)
        return json.JSONEncoder.default(self, o)

# الدالة لتحميل الوسائط وإرسالها
async def download_and_send_file(url, client):
    try:
        # تنزيل الملف
        file = await client.download_media(url)
        
        # إرسال الملف إلى الرسائل المحفوظة
        await client.send_file('me', file, caption="تم تحميل الملف بنجاح! جابلك دكتور محتوى مقيد")
        print("تم تحميل الملف وإرساله بنجاح.")
    except Exception as e:
        print(f"حدث خطأ أثناء تحميل أو إرسال الملف: {e}")

# الدالة الرئيسية
async def main():
    await client.start()
    print("Client Created")
    
    # التحقق من تسجيل الدخول
    if not await client.is_user_authorized():
        print("الجلسة غير مفوضة! تأكد من أن الجلسة صحيحة.")
        return

    # متابعة الرسائل
    @client.on(events.NewMessage(pattern=r'.تحميل'))
    async def handler(event):
        # التحقق من إذا كانت الرسالة تحتوي على رابط
        if event.reply_to_msg_id:
            replied_message = await event.get_reply_message()
            if replied_message:
                # إذا كانت الرسالة تحتوي على رابط
                if replied_message.text and 'http' in replied_message.text:
                    await download_and_send_file(replied_message.text, client)
                else:
                    await event.reply("لم يتم العثور على رابط في الرسالة.")
            else:
                await event.reply("لم يتم العثور على رسالة للرد عليها.")

    print("الاستماع للأوامر جاهز...")
    
    # تحديد القناة أو معرفها من متغيرات البيئة (أو يتم توفيرها في الرد على الرسائل)
    # سنستخدم هنا الـ events للتفاعل مع الأوامر القادمة.
    await client.run_until_disconnected()

# بدء الجلسة وتشغيل الكود
if __name__ == "__main__":
    client.loop.run_until_complete(main())
