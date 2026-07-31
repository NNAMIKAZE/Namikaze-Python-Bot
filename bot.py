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
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.edit_message_text("📤 جاري رفع الفيديو إلى تيليجرام...", chat_id=message.chat.id, message_id=status_msg.message_id)

        with open(output_template, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        print(f"Error details: {e}")
        try:
            bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل: {str(e)[:100]}", chat_id=message.chat.id, message_id=status_msg.message_id)
        except Exception:
            pass

    finally:
        if os.path.exists(output_template):
            os.remove(output_template)

print("🤖 Python Bot is running...")
bot.infinity_polling()
