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

# Memory tracking
warn_database = {}
message_counts = {}  # Tracks group messages per user


# Helper function to check if the user is an admin or owner
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
        await update.message.reply_text("❌ Reply to the message of the user you want to mute.")
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
        await update.message.reply_text(f"🤐 **{target_user.first_name}** has been muted.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error muting user: {e}")


async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to the message of the user you want to unmute.")
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
        await update.message.reply_text(f"🔊 **{target_user.first_name}** has been unmuted.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error unmuting user: {e}")


async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to the message of the user you want to warn.")
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
                f"🚨 **{target_user.first_name}** received {current_warns}/3 warnings. Automatically **MUTED**!"
            )
            warn_database[user_id] = 0
        except Exception as e:
            await update.message.reply_text(f"❌ Could not mute user: {e}")
    else:
        await update.message.reply_text(
            f"⚠️ Warning {current_warns}/3 for **{target_user.first_name}**. Please follow the rules!"
        )


# --- 5 MESSAGE LIMIT & AUTO-KICK FILTER ---


async def group_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ignore private chats and admins/owner
    if update.effective_chat.type == "private" or await is_admin(update, context):
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name

    # Increment message counter for the user
    message_counts[user_id] = message_counts.get(user_id, 0) + 1
    current_count = message_counts[user_id]

    if current_count == 4:
        # Warning message before getting kicked
        await update.message.reply_text(
            f"⚠️ **Warning {first_name}!** You have sent {current_count}/5 messages. "
            f"You will be **KICKED** from the group if you exceed 5 messages!"
        )
    elif current_count >= 5:
        # Execute kick on 5th message
        try:
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
            await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)  # Unban immediately so they can rejoin later if invited
            await update.message.reply_text(
                f"🚨 **{first_name}** has reached the limit of {current_count} messages and has been **KICKED** from the group."
            )
            message_counts[user_id] = 0  # Reset counter
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to kick user: {e}")


app = Application.builder().token(BOT_TOKEN).build()

# Commands
app.add_handler(CommandHandler("start", start))

# Moderation Commands
app.add_handler(CommandHandler("mute", mute_user))
app.add_handler(CommandHandler("unmute", unmute_user))
app.add_handler(CommandHandler("warn", warn_user))

# APK handler (Processes documents first)
app.add_handler(MessageHandler(filters.Document.ALL, apk_handler))

# Group Text/Media Monitor (Counts regular user messages)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_message_handler))

print("Bot running...")
app.run_polling()
