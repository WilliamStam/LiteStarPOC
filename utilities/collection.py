import json
from collections.abc import Sequence
from typing import List, TypeVar

from .pagination import Pagination

T = TypeVar("T")


#
class Collection(Sequence[T]):
    """
    The `Collection` class is a custom implementation of a sequence in Python. It provides several methods to manipulate and access the elements in the collection.

    Attributes:
        - `collection`: A list that stores the elements in the collection.

    Methods:
        - `__init__(self, data: List[T] = list(), **kwargs)`: Initializes a new instance of the `Collection` class. The `data` parameter is an optional list of initial elements to add to the collection. Any additional keyword arguments passed will be set as attributes on the instance.

        - `__bool__(self) -> bool`: Returns `True` if the collection has elements, otherwise returns `False`.

        - `__getitem__(self, index) -> T`: Retrieves the element at the specified index in the collection.

        - `__len__(self) -> int`: Returns the number of elements in the collection.

        - `__str__(self) -> str`: Returns a JSON-formatted string representation of the collection.

        - `__getattr__(self, attr)`: Retrieves a collection of values from the elements in the collection that have the specified attribute.

        - `__copy__(self) -> List[T]`: Creates a shallow copy of the collection.

        - `__deepcopy__(self, memo) -> List[T]`: Creates a deep copy of the collection.

        - `add(self, item: T) -> T`: Adds an item to the collection and returns the added item.

        - `remove(self, item)`: Removes the specified item from the collection if it exists.

        - `reverse(self) -> Collection[T]`: Creates and returns a new collection with the elements in reverse order.

        - `first(self) -> T`: Returns the first element in the collection or `None` if the collection is empty.

        - `last(self) -> T`: Returns the last element in the collection or `None` if the collection is empty.

        - `sort(self, *args, **kwargs)`: Sorts the elements in the collection in place using the given arguments and keyword arguments.

    Note:
        - This class extends the `Sequence` abstract base class from the `collections.abc` module.
        - The `T` in `Sequence[T]` represents a type variable that can be any type.
        - The `Collection` class requires the `Pagination` class from the `pagination` module, which should be imported separately.
    """
    
    def __init__(self, data: List[T] = list(), **kwargs):
        self.collection: List[T] = list()
        for item in data:
            self.add(item)
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __bool__(self):
        return True if len(self.collection) else False
    
    def __getitem__(self, index) -> T:
        return self.collection[index]
    
    def __len__(self) -> int:
        return len(self.collection)
    
    def __str__(self) -> str:
        return json.dumps([str(x) for x in self.collection], default=str, indent=4)
    
    def __getattr__(self, attr):
        collection = Collection()
        for item in self.collection:
            if hasattr(item, attr):
                collection.add(getattr(item, attr))
        
        return collection
    
    def __copy__(self) -> List[T]:
        return list(self.collection)
    
    def __deepcopy__(self, memo) -> List[T]:
        
        return list(self.collection)
    
    def add(self, item: T) -> T:
        self.collection.append(item)
        return item
    
    def remove(self, item):
        if item in self.collection:
            self.collection.remove(item)
        return self
    
    def reverse(self):
        collection = Collection()
        if self.collection:
            for item in self.collection[::-1]:
                collection.add(item)
        
        return collection
    
    def first(self) -> T:
        if len(self.collection):
            return self.collection[0]
        return None
    
    def last(self) -> T:
        if len(self.collection):
            return self.collection[-1]
        return None
    
    def sort(self, *args, **kwargs):
        return self.collection.sort(*args, **kwargs)


class PaginatedCollection(Collection):
    """
    PaginatedCollection Class

    A class representing a paginated collection of items.

    Attributes:
        pagination (Pagination): The pagination object used for managing the collection's pagination.

    Methods:

    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.pagination = Pagination()