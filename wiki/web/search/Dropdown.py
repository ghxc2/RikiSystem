from flask import jsonify

import wiki.web
from wiki.web.search.DropdownSearch import SuggestionSearch, HistorySearch


class Dropdown:
    """
    Dropdown class

    Class dedicated to handling autocomplete function for searching
    render() function to create serializable response based on all DropdownSearch
    classes required to create optimal autocomplete
    """

    def __init__(self, pages, database=None, user=None):
        self.suggestions = SuggestionSearch(pages)
        self.history = HistorySearch(pages, user, database)
        self.database = database
    def render(self, query):
        """
        Method intended to render all DropdownSearch classes into a renderable format for jsonify

        Args:
            query (str): Query to be searched for to find matching pages
        """
        if self.database is None:
            return jsonify(self.suggestions.render(query))
        return jsonify(self.suggestions.render(query), self.history.render(query))
