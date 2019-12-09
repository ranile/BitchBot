class Resource:

    def __str__(self):
        keys = {
            key: getattr(self, key)
            for key in self.__slots__
        }

        out = '{\n'

        for k, v in keys.items():
            out += f"{' ' * 4}{k}: {v},\n"

        if out.endswith(',\n'):
            out = ''.join(out[:-2])
        out += '\n}'
        return out

    def toDict(self):
        return {
            key: str(getattr(self, key))
            for key in self.__slots__
        }

    @classmethod
    def convert(cls, record):
        pass
