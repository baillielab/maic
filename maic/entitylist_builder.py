import logging
import re

from .entity import Entity
from .entitylist import EntityList, KnnEntityList, PolynomialEntityList, \
    ExponentialEntityList, SvrEntityList
from .errors import WarnValueError, KillValueError

from sys import maxsize

blank_matcher = re.compile("^\\s*$")

logging.basicConfig()
logger = logging.getLogger(__name__)


class EntityListBuilder(object):
    """
    An object that will construct a list of Entity objects from a string
    input line.
    """

    def __init__(self, list_type, limit=maxsize):
        """Initialise an EntityListBuilder"""
        self.__list_names = {}
        self.list_type = list_type
        self.limit = limit
        self._entity_dict = {}

    def build_list_from_string(self, string, limit=None):
        """
        Build a new EntityList object from a supplied string of data
        The supplied string is assumed to contain the data in tab-delimited
        columns. The first column is the list category name. The second
        column is the list name. The third column describes the list's
        'ranked' status. The fourth column is currently ignored.
        Columns subsequent to that are assumed to be the names of Entities
        within the list.
        If the string is too short, then the function throws an exception
        :param string:
        :param limit: The maximum number of entries to be contained in the list
        :return:
        """
        columns = string.strip().split("\t")
        if len(columns) < 4:
            raise WarnValueError('Insufficient columns to create an '
                                 'EntityList')
        if columns[1] in self.__list_names:
            raise KillValueError('List with that name already exists')
        is_ranked = columns[2].strip().upper() == "RANKED"
        entity_list = self.get_appropriate_entitylist(is_ranked)
        entity_list.is_ranked = is_ranked
        entity_list.category_name = columns[0]
        entity_list.name = columns[1]
        self.__list_names[columns[1]] = entity_list
        if limit is None:
            limit = self.limit
        counter = 0
        for x in range(4, len(columns)):
            m = blank_matcher.match(columns[x])
            if m:
                logger.warning("Found an empty column - column %d in list '%s'"
                               % (x + 1, columns[1]))
            else:
                if counter == limit:
                    # warn if items are omitted?
                    logger.warning("Some data in list '%s' was ignored due to "
                                   "a limit on list lengths (%s). Up to %d "
                                   "columns were skipped."
                                   % (columns[1], limit, len(columns) - x))
                    return entity_list
                entity = self.get_or_create_entity(columns[x])
                entity_list.append(entity)
                counter = len(entity_list)
        return entity_list

    def get_appropriate_entitylist(self, ranked):
        """
        Given the parameters of ranked and type then return an EntityList
        object of an appropriate type
        :param ranked: boolean - is this list a ranked list
        :return: an appropriate EntityList object
        """
        assert ranked is not None
        # entity_list = None
        if not ranked or self.list_type == 'none':
            entity_list = EntityList()
        elif self.list_type == 'knn':
            entity_list = KnnEntityList()
        elif self.list_type == 'polynomial':
            entity_list = PolynomialEntityList()
        elif self.list_type == 'exponential':
            entity_list = ExponentialEntityList()
        elif self.list_type == 'svr':
            entity_list = SvrEntityList()
        else:
            logger.warning("Unrecognised EntityList Type ('%s'). Returning an "
                           "unranked EntityList." % self.list_type)
            entity_list = EntityList()

        return entity_list

    def get_or_create_entity(self, entity_name):
        """
        Return the Entity corresponding to the supplied entity_name,
        creating it if required.
        """
        if entity_name not in self._entity_dict:
            self._entity_dict[entity_name] = Entity(entity_name)
        return self._entity_dict[entity_name]

    def entities(self):
        """Return a list of all the entities we have created"""
        return list(self._entity_dict.values())
