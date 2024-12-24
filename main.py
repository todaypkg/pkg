import os
import json
import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from datetime import datetime
from telethon.sessions import StringSession

# --- إعداد القيم من البيئة ---
api_id = int(os.getenv("API_ID"))  # API_ID من المتغيرات البيئية
api_hash = os.getenv("API_HASH")  # API_HASH من المتغيرات البيئية
phone = os.getenv("PHONE")  # رقم الهاتف من المتغيرات البيئية
username = os.getenv("USERNAME")  # اسم المستخدم للجلسة من المتغيرات البيئية
session_string = os.getenv("SESSION_STRING")  # الجلسة المخزنة كـ StringSession من المتغيرات البيئية

# --- إنشاء الجلسة مع Telethon ---
if session_string:
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
else:
    client = TelegramClient(username, api_id, api_hash)

# --- الكود لتحويل التاريخ إلى صيغة يمكن تخزينها ---
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, bytes):
            return list(o)
        return json.JSONEncoder.default(self, o)

# --- الدالة لتحميل الوسائط وإرسالها ---
async def download_and_send_file(url, client):
    try:
        # تنزيل الملف
        file = await client.download_media(url)
        
        # إرسال الملف إلى الرسائل المحفوظة
        await client.send_file('me', file, caption="تم تحميل الملف بنجاح!")
        print("تم تحميل الملف وإرساله بنجاح.")
    except Exception as e:
        print(f"حدث خطأ أثناء تحميل أو إرسال الملف: {e}")

# --- الدالة الرئيسية ---
async def main():
    await client.start()
    print("Client Created")
    
    # التحقق من تسجيل الدخول
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    # --- متابعة الرسائل ---
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

    # طلب إدخال القناة أو معرفها
    user_input_channel = input('Enter entity (Telegram URL or entity ID): ')
    
    # التحقق من إدخال URL أو ID
    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 0

    while True:
        print(f"Current Offset ID is: {offset_id}; Total Messages: {total_messages}")
        
        # الحصول على الرسائل من القناة
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        
        if not history.messages:
            break
        
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        
        offset_id = messages[-1].id
        total_messages = len(all_messages)
        
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    # حفظ الرسائل في ملف JSON
    with open('channel_messages.json', 'w') as outfile:
        json.dump(all_messages, outfile, cls=DateTimeEncoder)

    print("Finished saving messages.")

# --- بدء الجلسة وتشغيل الكود ---
if __name__ == "__main__":
    client.loop.run_until_complete(main())
