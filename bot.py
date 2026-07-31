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
    
    output_template = f"video_{message.chat.id}.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_template,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # التأكد من وجود الملف بأي صيغة تركها yt-dlp
        final_file = output_template
        if not os.path.exists(final_file):
            if os.path.exists(output_template + ".mp4"):
                final_file = output_template + ".mp4"

        bot.edit_message_text("📤 جاري رفع الفيديو إلى تيليجرام...", chat_id=message.chat.id, message_id=status_msg.message_id)

        with open(final_file, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        bot.delete_message(message.chat.id, status_msg.message_id)

        # تنظيف الملفات
        if os.path.exists(final_file):
            os.remove(final_file)
        if os.path.exists(output_template + ".part"):
            os.remove(output_template + ".part")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        try:
            bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل: {str(e)[:50]}", chat_id=message.chat.id, message_id=status_msg.message_id)
        except:
            pass

print("🤖 Python Bot is running...")
bot.infinity_polling()
