
class EntityListModel:
    
    def __init__(self, *args, name=None, category=None, entities=None):
        if name is None or category is None or entities is None:
            raise ValueError

        self._name = name
        self._category = category
        self._entities = entities

    @property
    def name(self):
        return self._name

    @property
    def category(self):
        return self._category

    @property
    def entities(self):
        return self._entities

