import sqlite3
from abc import ABCMeta, abstractmethod
from wiki.web.search.DropdownItem import SuggestionItem, HistoryItem


class DropdownSearch(metaclass=ABCMeta):
    """
    DropdownSearch Template Class

    Template class dedicated to creating DropdownSearch classes
    Used primarily for implementing search method that will be used
    To locate search results for autocomplete, and will include
    render() method to return them as a json serializable output
    """

    @abstractmethod
    def __init__(self, index): pass

    """
    Inits Dropdown Search
    Inteded to init page index used during searching
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

    def __init__(self, index):
        """
        Inits SuggestionSearch
        Inits pages index for searching
        """
        self.index = index

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

        """

        items = []
        for page in self.index:
            if query.lower() in page.title.lower():
                items.append(SuggestionItem(page.title))
        return items


class HistorySearch(DropdownSearch):
    """
        HistorySearch Class

        Class dedicated to creating HistorySearch class
        Used for Searching for results on system related to query provided
        To locate search results for autocomplete.
        Uses SQL Database
        """

    def __init__(self, index, user, database):
        """
        Inits SuggestionSearch
        Inits pages index for searching
        Inits database to be used
        Inits user to be queried by
        """
        self.index = index
        self.user = user
        self.database = database

    def render(self, query):
        """
        Method responsible for returning data from search in a
        serializable form that will be valid when returned with jsonify
        allows for easy returning of results from search

        Will only return results related to user history

        Args:
            query (str): Query to be searched for to find matching pages
        """
        results = self.search(query)
        results.sort(key=lambda r: r.date, reverse=True)
        titles = []
        for item in results:
            titles.append(item.title)
        return titles

    def search(self, query):
        """
        Method responsible for implementing search algorithm used to find pages
        Should convert to matching DropdownItem type classes to allow
        Easy conversion from pages to usable data needed for search
        Uses results  from database using user's results.

        Will only return results related to user history

        Args:
            query (str): Query to be searched for to find matching pages

        """
        results = self.get_history_from_db()
        items = []
        for item in results:
            if query.lower() in item[0].lower():
                for page in self.index:
                    if query.lower() in page.title.lower():
                        items.append(HistoryItem(item[0], item[1]))

        return items

    def get_history_from_db(self):
        """
        Retrieve's user history from database

        Returns a list of all user's found history
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        db_query = '''SELECT url, date_last_accessed
                    FROM user_history
                    WHERE user = ?'''
        cursor.execute(db_query, (self.user,))
        result = cursor.fetchall()
        conn.close()
        return result
