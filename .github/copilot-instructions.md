<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Meet Bot - AI-Enhanced Dating Bot

This is a modern Telegram dating bot built with Python and aiogram 3.x framework. The bot features AI-powered profile improvements, user matching, and modern UI with inline keyboards.

## Project Structure

- `bot.py` - Main bot file and entry point
- `config.py` - Configuration management with environment variables
- `database/` - Database models and operations using aiosqlite
- `handlers/` - Message and callback handlers organized by functionality
- `utils/` - Utility functions for keyboards, validation, and AI features
- `middlewares/` - Custom middleware for throttling and other features

## Key Features

- User profile creation and management
- Photo gallery support (up to 5 photos per profile)
- Swipe-based matching system
- AI-powered bio improvement using OpenAI API
- Geolocation-based user discovery
- Content moderation and validation
- Match system with chat functionality
- Modern inline keyboard interface

## Technical Details

- **Framework**: aiogram 3.4.1
- **Database**: SQLite with aiosqlite
- **AI Integration**: OpenAI GPT-3.5-turbo for content improvement
- **State Management**: FSM (Finite State Machine) for user interactions
- **Middleware**: Custom throttling and database injection
- **Validation**: Comprehensive input validation and sanitization

## Code Style Guidelines

- Use async/await for all database operations
- Follow Python naming conventions (snake_case)
- Use type hints where possible
- Keep handlers focused and modular
- Use meaningful error messages with emojis
- Implement proper logging for debugging
- Use database models consistently
- Validate user input before processing

## Database Schema

- `users` - User profiles and settings
- `user_photos` - Photo gallery for each user
- `swipes` - Like/dislike actions
- `matches` - Mutual likes (successful matches)
- `chats` - Chat sessions between matched users
- `messages` - Chat messages

## Environment Variables

- `BOT_TOKEN` - Telegram bot token from @BotFather
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `DATABASE_URL` - SQLite database file path
- `DEBUG` - Debug mode flag
- `ADMIN_IDS` - Comma-separated admin user IDs

## Development Notes

- The bot uses modern aiogram 3.x syntax with Router-based handlers
- All user interactions use inline keyboards for better UX
- Database operations are async and use connection pooling
- AI features are optional and gracefully degrade if API is unavailable
- The code includes comprehensive input validation and security measures
