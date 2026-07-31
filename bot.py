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
    
    output_file = f"video_{message.chat.id}.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_file,
        'no_warnings': True,
        'quiet': True,
    }

    try:
        # تحميل الفيديو
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # التحقق من اسم الملف النهائي
        actual_file = output_file
        if not os.path.exists(actual_file) and os.path.exists(output_file + ".mp4"):
            actual_file = output_file + ".mp4"

        # رفع الفيديو
        bot.edit_message_text("📤 جاري رفع الفيديو إلى تيليجرام...", chat_id=message.chat.id, message_id=status_msg.message_id)

        with open(actual_file, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        # حذف رسالة الانتظار بنجاح تام
        bot.delete_message(message.chat.id, status_msg.message_id)

        # تنظيف وحذف الملف بعد الإرسال الناجح
        if os.path.exists(actual_file):
            os.remove(actual_file)
        if os.path.exists(output_file + ".part"):
            os.remove(output_file + ".part")

    except Exception as e:
        print(f"Error: {e}")
        try:
            bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل، تأكد أن الرابط عام.", chat_id=message.chat.id, message_id=status_msg.message_id)
        except:
            pass

print("🤖 Python Bot is running...")
bot.infinity_polling()
