import json
from pprint import pprint
import services
import resources
from util.base_handler import BaseHandler


class HelloHandler(BaseHandler):

    async def get(self):
        self.set_status(200)
        self.write({'articles': [article.toDict() for article in (await services.EmojiService().getAll())]})
        await self.finish()

    async def post(self):
        print("yeehaw")
        self.set_status(201)
        emoji = resources.Emoji.convert(json.loads(self.request.body))
        await services.EmojiService().insert(emoji)
        self.write(emoji.toDict())
