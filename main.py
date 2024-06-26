from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from yt_dlp import YoutubeDL
import os
import time
import uvloop


API_ID = "YOUR_ID"
API_HASH = "YOUR_HASH"
BOT_TOKEN = "YOUR_TOKEN"
CHANNEL_USERNAME = "YOUR_CHANNEL_WITHOUT_@"

uvloop.install()

app = Client("teledownloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "السلام عليكم ورحمة الله وبركاته، \n"
        "هذا بوت تنزيل مقاطع الفيديو من مواقع التواصل الاجتماعي"
        " (فيسبوك، انستغرام، يوتيوب، إكس (تويتر) ومواقع أخرى لاحقا) \n"
        "\n البوت يعمل عن طريق إرسال رابط الفيديو المراد تحميله لا أكثر."
    )


@app.on_message(filters.command("cookies"))
async def change_cookies(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        admin = await client.get_chat_member(chat_id, user_id)
        if admin.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await client.send_message(chat_id, "الرجاء إرسال ملف الكوكيز.")

            @app.on_message(filters.document & filters.user(user_id))
            async def receive_document(client, message):
                if not message.document:
                    return

                file_id = message.document.file_id
                file_path = await client.download_media(file_id)
                os.makedirs("cookies", exist_ok=True)
                os.rename(file_path, "cookies/cookies.txt")
                await client.send_message(chat_id, "تم تحديث ملف الكوكيز بنجاح.")
        else:
            await client.send_message(chat_id, "أنت لا تملك صلاحية استخدام هذا الأمر.")
    except Exception as e:
        print(e)
        await client.send_message(chat_id, "حدث خطأ ما. الرجاء المحاولة مرة أخرى.")


@app.on_message(filters.text & filters.private)
async def download_video(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    video_url = message.text

    try:
        if video_url.startswith("https://"):
            is_member = await client.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
            if is_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                await client.send_message(chat_id, "جاري تنزيل الفيديو...")

                timestamp = int(time.time())
                output_template = f'{chat_id}-{timestamp}.mp4'

                ydl_opts = {
                    'outtmpl': output_template
                }
                if "youtube.com" in video_url or "youtu.be" in video_url:
                    if "list=" in video_url:
                        await client.send_message(chat_id, "رجاءً إرسال رابط الفيديو الفردي.")
                        return
                    elif "live" in video_url:
                        await client.send_message(chat_id, "لا يمكن تنزيل البث المباشر.")
                        return
                    ydl_opts['extractor-args'] = 'youtube:player_client=ios,web'
                elif any(domain in video_url for domain in
                         ["facebook.com", "fb.watch", "twitter.com", "t.co", "x.com", "instagram.com"]):
                    if "instagram.com" in video_url:
                        ydl_opts['cookiefile'] = './cookies/cookies.txt'

                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

                video_file = output_template
                await client.send_video(chat_id, video_file)
                if os.path.exists(video_file):
                    os.remove(video_file)
            else:
                await client.send_message(chat_id,
                                          f"عذرا قبل التحميل من البوت عليك الاشتراك بالقناة التالية"
                                          f" ثم إعادة إرسال الرابط المراد تحميله:\nhttps://t.me/{CHANNEL_USERNAME}")
        else:
            await client.send_message(chat_id, "الرجاء إرسال رابط فيديو صالح من يوتيوب، فيسبوك، تويتر، أو إنستغرام.")
    except Exception as e:
        print(e)
        await client.send_message(chat_id, "حدث خطأ أثناء تنزيل الفيديو. الرجاء المحاولة مرة أخرى.")


if __name__ == "__main__":
    app.run()
