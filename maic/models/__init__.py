
class EntityListModel:
    """Immutable model for passing entity lists into a maic cross-validation."""

    def __init__(self, *args, name=None, category=None, ranked=False, entities=None):
        """
        Create a new EntityListModel for passing to a cross-validation. Arguments must be passed by keyword.
        
        Arguments:
            @name: the name of this list. This must be unique within the cross-validation.
            @category: the name of the category for this list.
            @ranked: a boolean indicating whether the entities in this list are ranked (default: False).
            @entities: a sequence of strings representing the names of each entity in this list.
        
        """
        if name is None or category is None or entities is None:
            missing = [k for k, v in { "name": name, "category": category, "entities": entities}.items() if v is None]
            raise ValueError(f"The following keyword parameters must be provided: {','.join(missing)}")

        self._name = name
        self._category = category
        self._is_ranked = ranked
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

    @property
    def is_ranked(self):
        return self._is_ranked

