import telebot
import time
import re
from datetime import datetime
import pytz
from collections import defaultdict
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = '8905159909:AAHiWazwRD5nTS58O_c8ftdKQEOghcLgewU'
ADMIN_ID = 5828924210  

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

banned_users = set()
registered_users = set()
user_messages = defaultdict(list)

def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_info = KeyboardButton("ℹ️ အချက်အလက်များ")
    btn_contact = KeyboardButton("📞 ဆက်သွယ်ရန်")
    markup.row(btn_info, btn_contact)
    return markup

def is_office_closed():
    tz = pytz.timezone('Asia/Rangoon')
    now = datetime.now(tz)
    current_hour = now.hour
    if current_hour >= 23 or current_hour < 7:
        return True
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id in banned_users: return
    registered_users.add(message.chat.id)
    user_name = message.from_user.first_name
    
    try:
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEF1zti_...") 
    except:
        pass
        
    welcome_text = f"မင်္ဂလာပါ *{user_name}* ခင်ဗျာ 🙏\n\nကျွန်ုပ်တို့ထံ စာတို၊ ဓာတ်ပုံ၊ အသံဖိုင်၊ စတစ်ကာ သို့မဟုတ် မည်သည့် File မဆို ပို့နိုင်ပါပြီ။ မကြာမီ ပြန်လည်ဖြေကြားပေးပါမည်။"
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.message_handler(commands=['ban'], func=lambda message: message.chat.id == ADMIN_ID)
def ban_user(message):
    try:
        target_id = int(message.text.split())
        banned_users.add(target_id)
        bot.reply_to(message, f"🔒 User ID: `{target_id}` ကို Bot သုံးခွင့် ပိတ်ပင်လိုက်ပါပြီ။")
    except:
        bot.reply_to(message, "❌ အသုံးပြုပုံ မှားယွင်းနေပါသည်။ ဥပမာ - `/ban 12345678` ဟု ရိုက်ပါ။")

@bot.message_handler(commands=['unban'], func=lambda message: message.chat.id == ADMIN_ID)
def unban_user(message):
    try:
        target_id = int(message.text.split())
        banned_users.discard(target_id)
        bot.reply_to(message, f"🔓 User ID: `{target_id}` ကို ပြန်လည် ခွင့်ပြုလိုက်ပါပြီ။")
    except:
        bot.reply_to(message, "❌ အသုံးပြုပုံ မှားယွင်းနေပါသည်။ ဥပမာ - `/unban 12345678` ဟု ရိုက်ပါ။")

@bot.message_handler(commands=['stats'], func=lambda message: message.chat.id == ADMIN_ID)
def show_stats(message):
    bot.reply_to(message, f"📊 *VIP Bot Statistics*\n\n👥 စုစုပေါင်း အသုံးပြုသူဦးရေ: {len(registered_users)} ယောက်\n🚫 ပိတ်ပင်ထားသော ဦးရေ: {len(banned_users)} ယောက်")

@bot.message_handler(commands=['broadcast'], func=lambda message: message.chat.id == ADMIN_ID)
def broadcast_message(message):
    try:
        broadcast_text = message.text.replace("/broadcast", "").strip()
        if not broadcast_text:
            bot.reply_to(message, "❌ ပို့မည့်စာသားကို ထည့်သွင်းပါ။ ဥပမာ - `/broadcast မင်္ဂလာပါ`")
            return
        
        success_count = 0
        for user_id in registered_users:
            try:
                bot.send_message(user_id, broadcast_text)
                success_count += 1
            except:
                continue
        bot.reply_to(message, f"📢 လူဦးရေ {success_count} ယောက်ထံသို့ သတင်းစကား ကြေညာပြီးပါပြီ။")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def is_spamming(user_id):
    current_time = time.time()
    user_messages[user_id] = [t for t in user_messages[user_id] if current_time - t < 10]
    if len(user_messages[user_id]) > 5:
        return True
    user_messages[user_id].append(current_time)
    return False

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.reply_to_message is not None, content_types=['text', 'photo', 'voice', 'audio', 'video', 'document', 'sticker'])
def reply_to_user(message):
    try:
        orig_msg = message.reply_to_message
        target_text = orig_msg.text if orig_msg.text else orig_msg.caption
        
        user_id = None
        if target_text and "User ID" in target_text:
            match = re.search(r"User ID\s*:\s*(\d+)", target_text)
            if match:
                user_id = int(match.group(1))

        if user_id:
            bot.send_chat_action(user_id, 'typing')
            if message.content_type == 'text': bot.send_message(user_id, message.text, parse_mode=None)
            elif message.content_type == 'photo': bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption, parse_mode=None)
            elif message.content_type == 'voice': bot.send_voice(user_id, message.voice.file_id)
            elif message.content_type == 'audio': bot.send_audio(user_id, message.audio.file_id, caption=message.caption, parse_mode=None)
            elif message.content_type == 'video': bot.send_video(user_id, message.video.file_id, caption=message.caption, parse_mode=None)
            elif message.content_type == 'document': bot.send_document(user_id, message.document.file_id, caption=message.caption, parse_mode=None)
            elif message.content_type == 'sticker': bot.send_sticker(user_id, message.sticker.file_id)
                
            bot.reply_to(message, "✅ ပြန်လည်ပေးပို့ပြီးပါပြီ။")
        else:
            bot.reply_to(message, "❌ မူရင်းစာပို့သူကို ရှာမတွေ့ပါ။ စာကို Reply စနစ်ဖြင့် တိုက်ရိုက် ပြန်ပေးပါ။")
    except Exception as e:
        bot.reply_to(message, f"❌ ပို့၍မရပါ- {str(e)}")

@bot.message_handler(func=lambda message: message.text in ["ℹ️ အချက်အလက်များ", "📞 ဆက်သွယ်ရန်"])
def handle_menu_buttons(message):
    if message.chat.id in banned_users: return
    registered_users.add(message.chat.id)
    
    if message.text == "ℹ️ အချက်အလက်များ":
        bot.reply_to(message, "ℹ️ *လုံခြုံရေးနှင့် သတင်းအချက်အလက်*\n\nဤ Bot သည် သုံးစွဲသူများနှင့် အက်ဒမင်တို့ တိုက်ရိုက် လုံခြုံစွာ စကားပြောနိုင်ရန် ဖန်တီးထားသော အဆင့်မြင့် VIP Support Bot ဖြစ်ပါသည်။")
    elif message.text == "📞 ဆက်သွယ်ရန်":
        bot.reply_to(message, "📞 *ဆက်သွယ်ရန်*\n\nသင်သိလိုသော မေးခွန်းများ သို့မဟုတ် ပေးပို့လိုသော ဖိုင်များကို ဤချက်တင်ထဲတွင် တိုက်ရိုက် ရေးသားပေးပို့နိုင်ပါသည်။ အက်ဒမင်မှ အမြန်ဆုံး ဖတ်ရှုဖြေကြားပေးပါမည်။")

@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID, content_types=['text', 'photo', 'voice', 'audio', 'video', 'document', 'sticker'])
def forward_to_admin(message):
    if message.chat.id in banned_users: return
    registered_users.add(message.chat.id)
    
    if is_spamming(message.chat.id):
        bot.reply_to(message, "⚠️ စာများကို ခဏခဏ ဇတ်တိုက် မပို့ပါနှင့်။ ခေတ္တ စောင့်ဆိုင်းပေးပါ။")
        return

    user_id = message.chat.id
    mention = f"[{message.from_user.first_name}](tg://user?id={user_id})"
    info_text = f"👤 *Name* : {mention}\n🆔 *User ID* : {user_id}"
    
    if message.content_type == 'text':
        info_text += f"\n\n💬 *ပို့လိုက်တဲ့စာ* -\n{message.text}"
        bot.send_message(ADMIN_ID, info_text)
    elif message.content_type == 'photo':
        info_text += f"\n\n📸 *ဓာတ်ပုံတစ်ပုံ ပို့လိုက်ပါသည်။*"
        if message.caption: info_text += f"\nCaption: {message.caption}"
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=info_text)
    elif message.content_type == 'voice':
        bot.send_message(ADMIN_ID, info_text + f"\n\n🎙️ *Voice တစ်ခု ပို့လိုက်ပါသည်။*")
        bot.send_voice(ADMIN_ID, message.voice.file_id)
    elif message.content_type == 'audio':
        bot.send_audio(ADMIN_ID, message.audio.file_id, caption=info_text + f"\n\n🎵 *Audio ပို့လိုက်ပါသည်။*")
    elif message.content_type == 'video':
        bot.send_video(ADMIN_ID, message.video.file_id, caption=info_text + f"\n\n🎥 *ဗီဒီယို ပို့လိုက်ပါသည်။*")
    elif message.content_type == 'document':
        bot.send_document(ADMIN_ID, message.document.file_id, caption=info_text + f"\n\n📂 *ဖိုင် ပို့လိုက်ပါသည်။*")
    elif message.content_type == 'sticker':
        bot.send_message(ADMIN_ID, info_text + f"\n\n🃏 *Sticker တစ်ခု ပို့လိုက်ပါသည်။*")
        bot.send_sticker(ADMIN_ID, message.sticker.file_id)

    if is_office_closed():
        bot.send_message(user_id, "🌙 *အလိုအလျောက် သတိပေးချက်* -\n\nယခုအချိန်သည် ရုံးပိတ်ချိန် (ညဘက်) ဖြစ်သဖြင့် အက်ဒမင်မှ မနက်ပိုင်းတွင် ဖတ်ရှုပြီး ချက်ချင်း ပြန်လည်ဖြေကြားပေးပါမည်။ ကျေးဇူးတင်ပါသည်။")
    else:
        bot.send_message(user_id, "✉️ သင့်ပေးပို့ချက်ကို လက်ခံရရှိပါပြီ။ မကြာမီ ကျွန်တော်ကိုယ်တိုင် ဖတ်ရှုပြီး ပြန်လည်ဖြေကြားပေးပါမည်။ ကျေးဇူးတင်ပါသည်။", parse_mode=None)

print("စနစ်စုံလင်သော Ultimate VIP Live Chat Bot စတင် အလုပ်လုပ်နေပါပြီ...")
bot.infinity_polling()
