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
    
    # استخدام المسار المطلق لضمان عدم ضياع الملفات على السيرفر
    download_dir = os.getcwd()
    output_template = os.path.join(download_dir, f"video_{message.chat.id}.mp4")
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_template,
        'no_warnings': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.edit_message_text("📤 جاري رفع الفيديو إلى تيليجرام...", chat_id=message.chat.id, message_id=status_msg.message_id)

        # التأكد من وجود الملف قبل إرساله
        target_file = output_template
        if not os.path.exists(target_file):
            # أحياناً yt-dlp يضيف امتداد إضافي لو تغير الصيغة
            if os.path.exists(output_template + ".mp4"):
                target_file = output_template + ".mp4"

        with open(target_file, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        print(f"Error details: {e}")
        try:
            bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل، تأكد أن الرابط عام.", chat_id=message.chat.id, message_id=status_msg.message_id)
        except Exception:
            pass

    finally:
        if os.path.exists(output_template):
            os.remove(output_template)
        if os.path.exists(output_template + ".mp4"):
            os.remove(output_template + ".mp4")
        if os.path.exists(output_template + ".part"):
            os.remove(output_template + ".part")

print("🤖 Python Bot is running...")
bot.infinity_polling()
