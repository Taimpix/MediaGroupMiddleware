from aiogram import Bot, Dispatcher, types, F
from aiogram import BaseMiddleware
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import Command
import asyncio

# Initializing the bot
bot = Bot(token="TOKEN")
dp = Dispatcher()

# Middleware class for processing media groups and single media
class MediaGroupMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        # Dictionary for storing media groups
        self.media_groups = {}
        # Timeout for waiting for all media (in seconds)
        self.timeout = 1.0

    async def __call__(self, handler, event: types.Message, data: dict):
        # Creating a media list for the current message
        media_list = []
        
        if event.photo:
            media_list.append({
                "type": "photo",
                "id": event.photo[-1].file_id
            })
        elif event.video:
            media_list.append({
                "type": "video",
                "id": event.video.file_id
            })

        # Если есть медиа
        if media_list:
            # If this is not a media group, we immediately send a single media
            if not event.media_group_id:
                data["media_group"] = media_list
                data["media_group_messages"] = [event]
                return await handler(event, data)
            media_group_id = event.media_group_id
            if media_group_id not in self.media_groups:
                self.media_groups[media_group_id] = {
                    "media_list": [],
                    "messages": [],
                    "task": None
                }
            
            group = self.media_groups[media_group_id]
            
            # Adding media to the list
            group["media_list"].extend(media_list)
            group["messages"].append(event)
            
            # If this is the first message, we run about
            if len(group["messages"]) == 1:
                async def process_group():
                    await asyncio.sleep(self.timeout)
                    # Passing the dictionary list to the handler
                    data["media_group"] = group["media_list"]
                    data["media_group_messages"] = group["messages"]
                    await handler(event, data)
                    # Clearing the group after processing
                    del self.media_groups[media_group_id]
                    
                group["task"] = asyncio.create_task(process_group())
            
            # For all messages in the group, we return None so that the handler does not fire separately.
            return None
        
        # If it's not media, we pass the control on.
        return await handler(event, data)

# Registering middleware
dp.message.middleware(MediaGroupMiddleware())

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Отправьте мне фото или альбом с фото/видео!")

# Media group handler and single photos or videos 
@dp.message(F.content_type.in_({'photo', 'video'}))
async def handle_media(message: types.Message, media_group: list = None, media_group_messages: list = None):
    if media_group and media_group_messages:
        media_count = len(media_group)
        if media_count == 1:
            await message.answer(f"Получено одиночное медиа типа {media_group[0]['type']}")
        else:
            await message.answer(f"Получен альбом с {media_count} элементами")
        
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
