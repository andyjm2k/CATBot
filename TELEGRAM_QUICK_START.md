# Telegram Bot Integration - Quick Start Guide

Get your Eva AI Assistant running on Telegram in just 5 minutes!

---

## Prerequisites

- Python 3.10 or higher
- Active Telegram account
- OpenAI API key

---

## Step 1: Create Your Telegram Bot (2 minutes)

1. **Open Telegram** on your phone or desktop

2. **Search for @BotFather** and start a chat

3. **Send the command**: `/newbot`

4. **Choose a name** for your bot (e.g., "Eva AI Assistant")

5. **Choose a username** (must end in "bot", e.g., "eva_ai_assistant_bot")

6. **Copy the bot token** that BotFather gives you
   - It looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
   - Keep this secret! ⚠️

7. **Get your Telegram User ID**:
   - Search for @userinfobot on Telegram
   - Start a chat and it will tell you your user ID
   - It's a number like: `123456789`

---

## Step 2: Install Dependencies (1 minute)

Open your terminal in the AI_assistant directory and run:

```bash
pip install python-telegram-bot httpx python-dotenv
```

---

## Step 3: Configure Environment Variables (1 minute)

1. **Create a new file** named `.env` in your AI_assistant directory

2. **Copy these lines** and replace with your actual values:

```bash
TELEGRAM_BOT_TOKEN=paste_your_bot_token_here
OPENAI_API_KEY=paste_your_openai_key_here
TELEGRAM_ADMIN_IDS=paste_your_user_id_here
```

Example:
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OPENAI_API_KEY=sk-proj-abc123xyz789
TELEGRAM_ADMIN_IDS=123456789
```

3. **Save the file**

---

## Step 4: Run the Bot (30 seconds)

In your terminal, run:

```bash
python telegram_bot_minimal_example.py
```

You should see:
```
✅ Bot is running! Press Ctrl+C to stop.
📱 Open Telegram and search for your bot
💬 Send /start to begin
```

---

## Step 5: Test Your Bot (30 seconds)

1. **Open Telegram** and search for your bot username

2. **Start a chat** with your bot

3. **Send**: `/start`

4. **You should receive a welcome message!** 🎉

5. **Try these commands**:
   - `/help` - See all available commands
   - `/status` - Check bot status
   - Send any text message and get an AI response!

---

## Troubleshooting

### Bot doesn't respond

**Check that:**
- ✅ The bot script is running (you should see console output)
- ✅ Your bot token is correct
- ✅ Your user ID is in TELEGRAM_ADMIN_IDS
- ✅ You sent `/start` first

### "Not authorized" error

**Fix:**
- Make sure your Telegram user ID is correct
- Get it from @userinfobot
- Add it to TELEGRAM_ADMIN_IDS in .env
- Restart the bot

### OpenAI errors

**Check that:**
- ✅ Your OpenAI API key is valid
- ✅ You have credits in your OpenAI account
- ✅ The API key has proper permissions

### Bot stops unexpectedly

**Check:**
- Console for error messages
- Your internet connection
- OpenAI API status: https://status.openai.com/

---

## What's Next?

Now that you have a basic bot running, you can:

### Immediate Next Steps

1. **Customize the bot**:
   - Edit the system prompt in `telegram_bot_minimal_example.py`
   - Change the welcome message
   - Add more commands

2. **Test different features**:
   - Have conversations
   - Test the conversation history
   - Try the `/clear` command

### Advanced Features (See Full Plan)

For production deployment and advanced features, check out:

- 📖 **Full Feature Plan**: `TELEGRAM_INTEGRATION_FEATURE_PLAN.md`
  - Complete architecture and design
  - Security considerations
  - Production deployment strategies
  - All planned features and timeline

- ✅ **Implementation Checklist**: `TELEGRAM_INTEGRATION_CHECKLIST.md`
  - Step-by-step implementation guide
  - Phase 1, 2, 3 features
  - Testing procedures
  - Deployment checklist

### Suggested Implementation Order

1. ✅ **You are here**: Basic text messaging working
2. **Add voice messages**: Transcribe voice to text
3. **Add file support**: Upload and process documents
4. **Add web search**: Integrate search capabilities
5. **Add session storage**: Use Redis for better memory
6. **Deploy to production**: Setup webhook mode
7. **Add advanced features**: Browser automation, AutoGen workflows

---

## Key Files

- `telegram_bot_minimal_example.py` - Simple bot you're currently running
- `TELEGRAM_INTEGRATION_FEATURE_PLAN.md` - Complete feature plan (20+ sections)
- `TELEGRAM_INTEGRATION_CHECKLIST.md` - Implementation checklist
- `telegram_env_example.txt` - Environment variable reference
- `.env` - Your configuration (create this file)

---

## Commands Reference

### Bot Commands
- `/start` - Initialize bot and see welcome message
- `/help` - Show available commands
- `/clear` - Clear your conversation history
- `/status` - Check bot status and connectivity

### Development Commands

```bash
# Start the bot
python telegram_bot_minimal_example.py

# Stop the bot
Press Ctrl+C

# View this guide
cat TELEGRAM_QUICK_START.md

# View full feature plan
cat TELEGRAM_INTEGRATION_FEATURE_PLAN.md
```

---

## Cost Estimation

### Development/Testing
- **Telegram Bot**: Free
- **OpenAI API (light usage)**: ~$5-10/month
- **Total**: ~$5-10/month

### Production (100 active users)
- **Telegram Bot**: Free
- **OpenAI API**: ~$50-100/month
- **Hosting**: ~$20-50/month
- **Redis**: ~$10-20/month
- **Total**: ~$80-170/month

---

## Security Reminders

⚠️ **Important Security Notes:**

1. **Never share your bot token** - It's like a password
2. **Keep .env file private** - Don't commit to git
3. **Use whitelist** - Only authorized users can use the bot
4. **Monitor usage** - Watch for unusual activity
5. **Rate limiting** - Implement in production

Add `.env` to your `.gitignore`:
```bash
echo ".env" >> .gitignore
```

---

## Getting Help

### Documentation
- 📖 Read the full feature plan for detailed information
- ✅ Follow the implementation checklist for structured development
- 🔍 Check the troubleshooting section above

### External Resources
- [Telegram Bot API Docs](https://core.telegram.org/bots/api)
- [python-telegram-bot Library](https://docs.python-telegram-bot.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

### Community
- Create an issue in your repository
- Check existing documentation
- Review error logs in console

---

## FAQ

**Q: Can multiple people use my bot?**  
A: Yes! Add their Telegram user IDs to TELEGRAM_ADMIN_IDS (comma-separated)

**Q: How much will this cost?**  
A: Telegram is free. You only pay for OpenAI API usage (~$0.01-0.03 per conversation)

**Q: Can I use this in production?**  
A: This minimal example is great for testing. For production, follow the full feature plan for webhook mode, Redis, and proper error handling.

**Q: How do I deploy this to a server?**  
A: See the "Production Deployment" section in the full feature plan

**Q: Can the bot handle voice messages?**  
A: Not yet in this minimal version. It's planned for Phase 2 (see checklist)

**Q: How do I customize the bot's personality?**  
A: Edit the system prompt in the `call_openai_chat` function

**Q: Can I use a different AI model?**  
A: Yes! Change `'model': 'gpt-4'` to `'gpt-3.5-turbo'` or other models

**Q: How do I stop the bot?**  
A: Press `Ctrl+C` in the terminal where it's running

---

## Success! 🎉

If you've made it this far and your bot is responding on Telegram, congratulations! You've successfully integrated your AI assistant with Telegram.

### Share Your Success
- Test with friends (add them to whitelist)
- Customize the bot for your needs
- Consider implementing advanced features

### Next Steps
1. Review the full feature plan for production deployment
2. Follow the checklist for structured implementation
3. Add voice message support (Phase 2)
4. Deploy to production with webhook mode

---

**Happy Building! 🚀**

*For detailed implementation guidance, see TELEGRAM_INTEGRATION_FEATURE_PLAN.md*

