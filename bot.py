import os
import telebot
import yt_dlp

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_youtube_link(message):
    url = message.text
    if 'youtube.com' not in url and 'youtu.be' not in url:
        bot.reply_to(message, "❌ عذراً، يرجى إرسال رابط يوتيوب صالح.")
        return

    status_msg = bot.reply_to(message, "⏳ جاري تحميل الفيديو عبر السيرفر...")
    
    download_dir = os.getcwd()
    output_template = os.path.join(download_dir, f"video_{message.chat.id}.mp4")
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_template,
        'no_warnings': True,
        'quiet': True,
    }

    try:
        # مرحلة التحميل
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # تحديد مكان الملف بدقة
        target_file = output_template
        if not os.path.exists(target_file):
            if os.path.exists(output_template + ".mp4"):
                target_file = output_template + ".mp4"

        # مرحلة الرفع
        bot.edit_message_text("📤 جاري رفع الفيديو إلى تيليجرام...", chat_id=message.chat.id, message_id=status_msg.message_id)

        with open(target_file, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        # حذف رسالة الانتظار فقط إذا تمت الأمور بنجاح
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        print(f"Error details: {e}")
        try:
            bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل، تأكد أن الرابط عام.", chat_id=message.chat.id, message_id=status_msg.message_id)
        except Exception:
            pass

    finally:
        # تنظيف الملفات المؤقتة بأمان بدون إحداث مشاكل
        for ext in ["", ".mp4", ".part"]:
            file_path = output_template + ext if ext else output_template
            if ext == "" and os.path.exists(output_template):
                try: os.remove(output_template)
                except: pass
            elif ext != "" and os.path.exists(output_template + ext):
                try: os.remove(output_template + ext)
                except: pass

print("🤖 Python Bot is running...")
bot.infinity_polling()
