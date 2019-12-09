import json
from pprint import pprint

from resources.article import Article
from services.article_service import ArticleService
from util.base_handler import BaseHandler


class HelloHandler(BaseHandler):

    async def get(self):
        self.set_status(200)
        self.write({'articles': [article.toDict() for article in (await ArticleService().getAll())]})
        await self.finish()

    async def post(self):
        print("yeehaw")
        self.set_status(201)
        article = Article.convert(json.loads(self.request.body))
        await ArticleService().insert(article)
        self.write(article.toDict())

#  default=str(key)
