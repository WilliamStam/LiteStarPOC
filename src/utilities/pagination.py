import dataclasses


@dataclasses.dataclass
class Pagination():
    """

    Class Pagination

    This class represents a pagination object used for navigating through a collection of data.

    Attributes:
    - page (int): The current page number.
    - total (int): The total number of items in the collection.
    - paginate (int): The number of items to display per page.

    """
    page: int = None
    total: int = None
    paginate: int = None