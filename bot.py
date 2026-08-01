import os
import telebot
import yt_dlp

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_youtube_link(message):
    raw_url = message.text.split('?')[0] 
    
    if 'youtube.com' not in raw_url and 'youtu.be' not in raw_url:
        bot.reply_to(message, "❌ عذراً، يرجى إرسال رابط يوتيوب صالح.")
        return

    # خدعة تحويل رابط الـ Shorts إلى فيديو عادي
    if '/shorts/' in raw_url:
        video_id = raw_url.split('/shorts/')[1]
        final_url = f"https://www.youtube.com/watch?v={video_id}"
    else:
        final_url = raw_url

    status_msg = bot.reply_to(message, "⏳ جاري التحميل...")
    
    output_template = f"video_{message.chat.id}.mp4"
    cookie_path = os.path.join(os.getcwd(), 'cookies.txt')
    
    # الصيغة المرنة: تدمج أعلى جودة، وإذا فشلت تسحب أفضل ملف جاهز
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
        'outtmpl': output_template,
        'no_warnings': True,
        'cookiefile': cookie_path,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([final_url])

        final_file = output_template
        if not os.path.exists(final_file) and os.path.exists(output_template + ".mp4"):
            final_file = output_template + ".mp4"

        bot.edit_message_text("📤 جاري الرفع إلى تيليجرام...", chat_id=message.chat.id, message_id=status_msg.message_id)

        with open(final_file, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        bot.delete_message(message.chat.id, status_msg.message_id)

        if os.path.exists(final_file):
            os.remove(final_file)

    except Exception as e:
        error_details = str(e)
        print(f"CRITICAL ERROR: {error_details}")
        try:
            bot.edit_message_text(f"❌ خطأ بالتحميل:\n{error_details[:100]}", chat_id=message.chat.id, message_id=status_msg.message_id)
        except:
            pass

print("🤖 Python Bot is running...")
bot.infinity_polling()
