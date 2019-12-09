from abc import ABC


class Service(ABC):
    async def get(self, id):
        pass

    async def getAll(self):
        pass

    async def insert(self, res):
        pass

    async def update(self, replacement):
        pass

    async def delete(self, id):
        pass

    async def rawQuery(self, query):
        pass
