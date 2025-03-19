from aiogram import types
from aiogram import BaseMiddleware

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

        # If there is media
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