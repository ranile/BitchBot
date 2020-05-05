class SQL:
    def __init__(self, **kwargs):
        self.createTable = kwargs.pop('createTable')
