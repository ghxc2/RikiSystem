class DropdownItem:
    """
    DropdownItem Class

    A data class to allow easy transformable formats for
    DropdownSearch rendering
    """
    def __init__(self, page):
        """
        Constructor for DropdownItem Class

        Args:
            page (Page): Page found in search of wiki to be converted to easier use
        """
        self.title = page.title
        self.url = page.url


class SuggestionItem(DropdownItem):
    """
    SuggestionItem Class

    DropdownItem class intended for SuggestionSearch items
    Currently only contains html class
    May be further implemented later
    """
    tag = ".suggestion"
