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
        self.title = page


class SuggestionItem(DropdownItem):
    """
    SuggestionItem Class

    DropdownItem class intended for SuggestionSearch items
    Currently only contains html class
    May be further implemented later
    """
    tag = ".suggestion"


class HistoryItem(DropdownItem):
    """
    HistoryItem Class

    DropdownItem class intended for HistorySearch items
    Currently only contains html class
    May be further implemented later
    """
    tag = ".history"

    def __init__(self, page, date):
        """
        Constructor for HistoryItem Class

        Args:
            page (Page): Page found in search of wiki to be converted to easier use
            date (DateTime): Date of last access
        """
        super().__init__(page)
        self.date = date
