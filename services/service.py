from abc import ABC


class Service(ABC):
    @classmethod
    async def get(cls, name, value):
        pass

    @classmethod
    async def getAll(cls):
        pass

    @classmethod
    async def insert(cls, res):
        pass

    @classmethod
    async def update(cls, replacement):
        pass

    @classmethod
    async def delete(cls, id):
        pass

    @classmethod
    async def rawSelectQuery(cls, query, args):
        pass

    @classmethod
    async def rawQuery(cls, query, args):
        pass
