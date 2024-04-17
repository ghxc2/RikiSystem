from flask import jsonify

import wiki.web
from wiki.web.search.DropdownSearch import SuggestionSearch


class Dropdown:
    """
    Dropdown class

    Class dedicated to handling autocomplete function for searching
    render() function to create serializable response based on all DropdownSearch
    classes required to create optimal autocomplete
    """
    def __init__(self, pages):
        self.suggestions = SuggestionSearch(pages)

    def render(self, query):
        """
        Method intended to render all DropdownSearch classes into a renderable format for jsonify

        Args:
            query (str): Query to be searched for to find matching pages
        """
        return jsonify(self.suggestions.render(query))
