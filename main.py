from telethon import TelegramClient, events
from moviepy.editor import VideoFileClip
import os

# جلب API ID و API Hash من متغيرات البيئة
api_id = os.environ.get("API_ID")   # جلب API ID
api_hash = os.environ.get("API_HASH")  # جلب API Hash
bot_token = os.environ.get("BOT_TOKEN")  # جلب التوكن من متغيرات البيئة

# إنشاء عميل Telethon
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("مرحباً! أرسل لي فيديو وسأستخرج الصوت وأعيده لك كملف صوتي.")

@client.on(events.NewMessage())
async def handle_video(event):
    if event.video or (event.document.mime_type == 'video/mp4'):
        video_path = await event.download_media()
        audio_path = f"{os.path.splitext(video_path)[0]}.mp3"

        try:
            # استخراج الصوت باستخدام moviepy
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path)

            # إرسال الملف الصوتي للمستخدم
            await event.reply(file=audio_path)

        except Exception as e:
            await event.reply(f"حدث خطأ أثناء معالجة الفيديو: {e}")

        finally:
            # تنظيف الملفات المؤقتة
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)

# تشغيل العميل
client.run_until_disconnected()
