from abc import ABCMeta, abstractmethod
from wiki.web import current_wiki
from wiki.web.search.DropdownItem import SuggestionItem


class DropdownSearch(metaclass=ABCMeta):
    """
    DropdownSearch Template Class

    Template class dedicated to creating DropdownSearch classes
    Used primarily for implementing search method that will be used
    To locate search results for autocomplete, and will include
    render() method to return them as a json serializable output
    """

    @abstractmethod
    def render(self, query): pass

    """
    Method responsible for returning data from search in a
    serializable form that will be valid when returned with jsonify
    allows for easy returning of results from search
    
    Args:
        query (str): Query to be searched for to find matching pages
    """

    @abstractmethod
    def search(self, query): pass

    """
    Method responsible for implementing search algorithm used to find pages
    Should convert to matching DropdownItem type classes to allow
    Easy conversion from pages to usable data needed for search

    Args:
        query (str): Query to be searched for to find matching pages
    """


class SuggestionSearch(DropdownSearch):
    """
    SuggestionSearch Class

    Class dedicated to creating SuggestionSearch class
    Used for Searching for results on system related to query provided
    To locate search results for autocomplete
    """

    def render(self, query):
        """
        Method responsible for returning data from search in a
        serializable form that will be valid when returned with jsonify
        allows for easy returning of results from search

        Will only return results unrelated to user history

        Args:
            query (str): Query to be searched for to find matching pages
        """
        items = self.search(query)
        titles = []
        for item in items:
            titles.append(item.title)

        return titles

    def search(self, query):
        """
        Method responsible for implementing search algorithm used to find pages
        Should convert to matching DropdownItem type classes to allow
        Easy conversion from pages to usable data needed for search

        Will only return results unrelated to user history

        Args:
            query (str): Query to be searched for to find matching pages

        >>> t = SuggestionSearch()
        >>> t.search("testing")[0].title
        'Testing'
        """
        results = current_wiki.search(query)
        items = []
        for page in results:
            items.append(SuggestionItem(page))
        return items


if __name__ == "__main__":
    import doctest
    doctest.testmod(extraglobs={'t': SuggestionSearch()})
