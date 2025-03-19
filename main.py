from aiogram import Bot, Dispatcher, types, F
from aiogram import BaseMiddleware
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import Command
import asyncio

# Importing MediaGroupMiddleware from a file middlewares.py
from middlewares import MediaGroupMiddleware

# Initializing the bot
api_token = "TOKEN"
bot = Bot(token=api_token)
dp = Dispatcher()

# Registering middleware
dp.message.middleware(MediaGroupMiddleware())

# Handler of the /start command
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Send me a photo or an album with photos/videos!")

# Media group handler and single photos or videos 
@dp.message(F.content_type.in_({'photo', 'video'}))
async def handle_media(message: types.Message, media_group: list = None, media_group_messages: list = None):
    if media_group and media_group_messages:
        media_count = len(media_group)
        if media_count == 1:
            await message.answer(f"A single media of the {media_group[0]['type']} type was received")
        else:
            await message.answer(f"An album with {media_count} elements was received")
        
        # We display information about each object
        for item in media_group:
            print(f"Type: {item['type']}, ID: {item['id']}")
        
        # Optional: you can create a MediaGroupBuilder to send back
        builder = MediaGroupBuilder()
        for item in media_group:
            if item["type"] == "photo":
                builder.add_photo(media=item["id"])
            elif item["type"] == "video":
                builder.add_video(media=item["id"])
        
        await bot.send_media_group(
            chat_id=message.chat.id,
            media=builder.build()
        )

# Launching the bot
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
