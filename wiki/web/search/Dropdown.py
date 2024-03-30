from flask import jsonify
from wiki.web.search.DropdownSearch import SuggestionSearch


class Dropdown:
    """
    Dropdown class

    Class dedicated to handling autocomplete function for searching
    render() function to create serializable response based on all DropdownSearch
    classes required to create optimal autocomplete
    """
    suggestions = SuggestionSearch()

    def render(self, query):
        """
        Method intended to render all DropdownSearch classes into a renderable format for jsonify

        Args:
            query (str): Query to be searched for to find matching pages
        """
        return jsonify(self.suggestions.render(query))
