#!/usr/bin/env python3
"""
Minimal Telegram Bot Example for Eva AI Assistant
This is a simplified proof-of-concept to get started quickly

Requirements:
- pip install python-telegram-bot httpx python-dotenv

Environment Variables (.env):
- TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
- OPENAI_API_KEY=your_openai_key
- TELEGRAM_ADMIN_IDS=your_telegram_user_id
"""

import asyncio
import os
import logging
from typing import Dict, List
from dotenv import load_dotenv
import httpx

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Load environment variables from .env file
load_dotenv()

# Configure logging to show info and debug messages
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8002')

# Admin user IDs (comma-separated in env var)
ADMIN_IDS_STR = os.getenv('TELEGRAM_ADMIN_IDS', '')
ADMIN_IDS = set([int(id.strip()) for id in ADMIN_IDS_STR.split(',') if id.strip()])

# In-memory conversation storage (use Redis/Database in production)
conversations: Dict[int, List[Dict]] = {}

def is_authorized(user_id: int) -> bool:
    """Check if user is authorized to use the bot"""
    # For now, only admins can use the bot
    # In production, maintain a proper whitelist
    return user_id in ADMIN_IDS

async def call_openai_chat(messages: List[Dict]) -> str:
    """
    Call OpenAI Chat Completion API directly
    In production, route through your backend API
    """
    try:
        # Prepare request to OpenAI API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {OPENAI_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4',  # or 'gpt-3.5-turbo' for lower cost
                    'messages': messages,
                    'max_tokens': 1000,
                    'temperature': 0.7
                }
            )
            
            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return "Sorry, I encountered an error communicating with the AI service."
                
    except Exception as e:
        logger.error(f"Error calling OpenAI: {e}")
        return "Sorry, I couldn't process your request right now."

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Check authorization
    if not is_authorized(user_id):
        await update.message.reply_text(
            "⚠️ Sorry, you are not authorized to use this bot.\n"
            "Please contact the administrator to request access."
        )
        logger.warning(f"Unauthorized access attempt by user {user_id}")
        return
    
    # Initialize conversation for this user
    conversations[user_id] = []
    
    # Send welcome message
    welcome_message = f"""
👋 Hi {user_name}! I'm Eva, your AI assistant.

I can help you with:
• 💬 Natural conversations
• ❓ Answering questions
• 📝 Writing and editing text
• 💡 Brainstorming ideas
• And much more!

Just send me a message to get started!

Use /help to see all available commands.
"""
    
    await update.message.reply_text(welcome_message)
    logger.info(f"User {user_id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    help_text = """
📚 **Available Commands:**

/start - Start the bot and see welcome message
/help - Show this help message
/clear - Clear your conversation history
/status - Check bot status

💬 **How to Use:**
Simply send me any text message and I'll respond!

🎤 **Voice Messages:**
Send voice messages for transcription (coming soon)

📄 **Files:**
Upload documents for analysis (coming soon)

Need more help? Use /status to check if I'm working properly.
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /clear command - clear conversation history"""
    user_id = update.effective_user.id
    
    # Check authorization
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorized to use this bot.")
        return
    
    # Clear conversation history for this user
    conversations[user_id] = []
    
    await update.message.reply_text(
        "✅ Your conversation history has been cleared.\n"
        "Start fresh with a new message!"
    )
    logger.info(f"User {user_id} cleared conversation history")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /status command - show bot status"""
    user_id = update.effective_user.id
    
    # Check authorization
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorized to use this bot.")
        return
    
    # Get conversation stats
    msg_count = len(conversations.get(user_id, []))
    
    # Check backend connectivity (if backend URL is configured)
    backend_status = "⚠️ Not configured"
    if BACKEND_URL != 'http://localhost:8002':
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{BACKEND_URL}/health")
                if response.status_code == 200:
                    backend_status = "✅ Connected"
                else:
                    backend_status = "❌ Error"
        except Exception:
            backend_status = "❌ Unavailable"
    
    status_text = f"""
🤖 **Bot Status**

Status: ✅ Online
Backend: {backend_status}
Your Messages: {msg_count}
User ID: `{user_id}`

Everything looks good! 🎉
"""
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Check authorization
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorized to use this bot.")
        logger.warning(f"Unauthorized message from user {user_id}")
        return
    
    # Show "typing" indicator to user
    await update.message.chat.send_action("typing")
    
    logger.info(f"User {user_id} sent: {user_message[:50]}...")
    
    try:
        # Get or create conversation history for this user
        if user_id not in conversations:
            conversations[user_id] = []
        
        # Add user message to conversation history
        conversations[user_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Limit conversation history to last 10 messages to save tokens
        # Keep system message + last 9 messages
        conversation_history = [
            {
                "role": "system",
                "content": "You are Eva, a helpful AI assistant integrated with Telegram. "
                          "Be concise, friendly, and helpful. Keep responses under 1000 characters when possible."
            }
        ] + conversations[user_id][-9:]
        
        # Call OpenAI API with conversation history
        assistant_response = await call_openai_chat(conversation_history)
        
        # Add assistant response to conversation history
        conversations[user_id].append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # Send response to user
        await update.message.reply_text(assistant_response)
        
        logger.info(f"Sent response to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await update.message.reply_text(
            "😔 Sorry, I encountered an error processing your message.\n"
            "Please try again or use /clear to start fresh."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the bot"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Try to inform the user about the error
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "😔 An unexpected error occurred. Please try again later."
            )
    except Exception:
        pass

def main():
    """Start the bot"""
    # Validate configuration
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set in environment!")
        print("\n⚠️  Please set TELEGRAM_BOT_TOKEN in your .env file")
        print("   Get your token from @BotFather on Telegram")
        return
    
    if not OPENAI_API_KEY:
        logger.error("❌ OPENAI_API_KEY not set in environment!")
        print("\n⚠️  Please set OPENAI_API_KEY in your .env file")
        print("   Get your API key from https://platform.openai.com/")
        return
    
    if not ADMIN_IDS:
        logger.warning("⚠️  No admin IDs configured, bot will not accept any users!")
        print("\n⚠️  Please set TELEGRAM_ADMIN_IDS in your .env file")
        print("   Get your Telegram user ID from @userinfobot")
        print("   Example: TELEGRAM_ADMIN_IDS=123456789,987654321")
    
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Register message handler for text messages
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler)
    )
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot in polling mode
    logger.info("🤖 Starting Eva Telegram Bot...")
    logger.info(f"📋 Authorized users: {ADMIN_IDS}")
    print("\n✅ Bot is running! Press Ctrl+C to stop.")
    print(f"📱 Open Telegram and search for your bot")
    print(f"💬 Send /start to begin\n")
    
    # Run the bot until Ctrl+C is pressed
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

