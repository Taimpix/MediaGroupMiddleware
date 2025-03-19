from aiogram import Bot, Dispatcher, types, F
from aiogram import BaseMiddleware
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import Command
import asyncio

# Initializing the bot
bot = Bot(token="TOKEN")
dp = Dispatcher()

# Класс middleware для обработки медиа-групп и одиночных медиа
class MediaGroupMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        # Словарь для хранения медиа-групп
        self.media_groups = {}
        # Таймаут для ожидания всех медиа (в секундах)
        self.timeout = 1.0

    async def __call__(self, handler, event: types.Message, data: dict):
        # Создаем список медиа для текущего сообщения
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
            # Если это не медиа-группа, сразу передаем одиночное медиа
            if not event.media_group_id:
                data["media_group"] = media_list
                data["media_group_messages"] = [event]
                return await handler(event, data)
            
            # Обработка медиа-группы
            media_group_id = event.media_group_id
            
            # Инициализируем группу, если она новая
            if media_group_id not in self.media_groups:
                self.media_groups[media_group_id] = {
                    "media_list": [],
                    "messages": [],
                    "task": None
                }
            
            group = self.media_groups[media_group_id]
            
            # Добавляем медиа в список
            group["media_list"].extend(media_list)
            group["messages"].append(event)
            
            # Если это первое сообщение в группе, запускаем задачу обработки
            if len(group["messages"]) == 1:
                async def process_group():
                    await asyncio.sleep(self.timeout)
                    # Передаем список словарей в хэндлер
                    data["media_group"] = group["media_list"]
                    data["media_group_messages"] = group["messages"]
                    await handler(event, data)
                    # Очищаем группу после обработки
                    del self.media_groups[media_group_id]
                    
                group["task"] = asyncio.create_task(process_group())
            
            # Для всех сообщений группы возвращаем None, чтобы хэндлер не срабатывал отдельно
            return None
        
        # Если это не медиа, передаем управление дальше
        return await handler(event, data)

# Регистрируем middleware
dp.message.middleware(MediaGroupMiddleware())

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Отправьте мне фото или альбом с фото/видео!")

# Обработчик медиа-групп и одиночных медиа
@dp.message(F.content_type.in_({'photo', 'video'}))
async def handle_media(message: types.Message, media_group: list = None, media_group_messages: list = None):
    if media_group and media_group_messages:
        media_count = len(media_group)
        if media_count == 1:
            await message.answer(f"Получено одиночное медиа типа {media_group[0]['type']}")
        else:
            await message.answer(f"Получен альбом с {media_count} элементами")
        
        # Выводим информацию о каждом элементе
        for item in media_group:
            print(f"Type: {item['type']}, ID: {item['id']}")
        
        # Опционально: можно создать MediaGroupBuilder для отправки обратно
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

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
