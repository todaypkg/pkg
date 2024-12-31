from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
from moviepy.editor import VideoFileClip
import os

# جلب التوكن من متغيرات البيئة
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("مرحباً! أرسل لي فيديو وسأستخرج الصوت وأعيده لك كملف صوتي.")

async def handle_video(update: Update, context: CallbackContext):
    # تحميل الفيديو الذي أرسله المستخدم
    video_file = update.message.video or update.message.document
    if video_file:
        video_path = await video_file.get_file().download_to_drive()
        audio_path = f"{os.path.splitext(video_path)[0]}.mp3"

        try:
            # استخراج الصوت باستخدام moviepy
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path)

            # إرسال الملف الصوتي للمستخدم
            with open(audio_path, "rb") as audio_file:
                await update.message.reply_audio(audio_file)

        except Exception as e:
            await update.message.reply_text(f"حدث خطأ أثناء معالجة الفيديو: {e}")

        finally:
            # تنظيف الملفات المؤقتة
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
    else:
        await update.message.reply_text("يرجى إرسال فيديو صالح.")

def main():
    PORT = int(os.environ.get('PORT', 8443))
    APP_NAME = "pkg56"

    # إنشاء تطبيق Telegram
    application = Application.builder().token(TOKEN).build()

    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.MimeType("video/mp4"), handle_video))

    # إعداد Webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://{APP_NAME}.herokuapp.com/{TOKEN}"
    )

if __name__ == "__main__":
    main()
