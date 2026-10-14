# MediaGroupMiddleware

Middleware for aiogram 3.x that collects media groups (albums) of photos and videos into a single list and passes them to the handler.

## How it works

Telegram sends each media item in an album as a separate message with the same `media_group_id`. Without middleware, the handler is called once for every item.

This middleware:

- Collects all messages of one media group
- Waits `timeout` seconds (default 1.0) after the first message
- Passes two values into the handler:
  - `media_group` — list of dicts `{"type": "photo"|"video", "id": file_id}`
  - `media_group_messages` — list of original `Message` objects
- Single photos/videos (without `media_group_id`) are also passed the same way
- Non-media messages are forwarded without changes

## Requirements

- Python 3.8+
- aiogram 3.x

```bash
pip install aiogram
```

## Usage

### 1. Register the middleware

```python
from aiogram import Bot, Dispatcher
from middlewares import MediaGroupMiddleware

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()

dp.message.middleware(MediaGroupMiddleware())
```

### 2. Handler example

```python
from aiogram import types, F
from aiogram.utils.media_group import MediaGroupBuilder

@dp.message(F.content_type.in_({"photo", "video"}))
async def handle_media(
    message: types.Message,
    media_group: list = None,
    media_group_messages: list = None
):
    if not media_group:
        return

    count = len(media_group)
    if count == 1:
        await message.answer(f"Received single {media_group[0]['type']}")
    else:
        await message.answer(f"Received album with {count} items")

    # Optional: send the album back
    builder = MediaGroupBuilder()
    for item in media_group:
        if item["type"] == "photo":
            builder.add_photo(media=item["id"])
        elif item["type"] == "video":
            builder.add_video(media=item["id"])

    await bot.send_media_group(chat_id=message.chat.id, media=builder.build())
```

### 3. Change timeout (optional)

```python
middleware = MediaGroupMiddleware()
middleware.timeout = 1.5  # seconds
dp.message.middleware(middleware)
```

## Files

| File | Description |
|------|-------------|
| `middlewares.py` | Middleware class |
| `main.py` | Minimal working example |

## Limitations

- Only photo and video are supported
- In-memory storage (not suitable for multiple processes / workers)
- Timeout is fixed per group (no adaptive waiting)

---

# MediaGroupMiddleware

Middleware для aiogram 3.x, которое собирает медиагруппы (альбомы) фото и видео в один список и передаёт его в хендлер.

## Как работает

Telegram присылает каждый элемент альбома отдельным сообщением с одинаковым `media_group_id`. Без middleware хендлер вызывается на каждый элемент отдельно.

Этот middleware:

- Собирает все сообщения одной медиагруппы
- Ждёт `timeout` секунд (по умолчанию 1.0) после первого сообщения
- Передаёт в хендлер два значения:
  - `media_group` — список словарей `{"type": "photo"|"video", "id": file_id}`
  - `media_group_messages` — список оригинальных объектов `Message`
- Одиночные фото/видео (без `media_group_id`) тоже передаются в том же формате
- Сообщения без медиа проходят дальше без изменений

## Требования

- Python 3.8+
- aiogram 3.x

```bash
pip install aiogram
```

## Использование

### 1. Регистрация middleware

```python
from aiogram import Bot, Dispatcher
from middlewares import MediaGroupMiddleware

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()

dp.message.middleware(MediaGroupMiddleware())
```

### 2. Пример хендлера

```python
from aiogram import types, F
from aiogram.utils.media_group import MediaGroupBuilder

@dp.message(F.content_type.in_({"photo", "video"}))
async def handle_media(
    message: types.Message,
    media_group: list = None,
    media_group_messages: list = None
):
    if not media_group:
        return

    count = len(media_group)
    if count == 1:
        await message.answer(f"Получено одиночное {media_group[0]['type']}")
    else:
        await message.answer(f"Получен альбом из {count} элементов")

    # Опционально: отправить альбом обратно
    builder = MediaGroupBuilder()
    for item in media_group:
        if item["type"] == "photo":
            builder.add_photo(media=item["id"])
        elif item["type"] == "video":
            builder.add_video(media=item["id"])

    await bot.send_media_group(chat_id=message.chat.id, media=builder.build())
```

### 3. Изменение таймаута (опционально)

```python
middleware = MediaGroupMiddleware()
middleware.timeout = 1.5  # секунды
dp.message.middleware(middleware)
```

## Файлы

| Файл | Описание |
|------|----------|
| `middlewares.py` | Класс middleware |
| `main.py` | Минимальный рабочий пример |

## Ограничения

- Поддерживаются только photo и video
- Хранение в памяти (не подходит для нескольких процессов / воркеров)
- Таймаут фиксированный для группы (без адаптивного ожидания)
```