import enum

from log import log

logger = log.getLogger(__name__)

from sqlalchemy import asc, desc


class TempEnum(str, enum.Enum):
    pass


class Ordering():
    
    def __init__(self, name="OrderColumnEnum"):
        self._items = {}
        self._default = None
        self._name = name
    
    def add(self, key: str, column, default=False):
        self._items[key] = column
        if default:
            self._default = key
    
    @property
    def columns(self):
        cols = {}
        for k, v in self._items.items():
            cols[k] = k
        return TempEnum(self._name, cols)
    
    @property
    def default(self):
        if self._items:
            return self._default if self._default in self._items.keys() else None
        return None
    
    @property
    def direction(self):
        return TempEnum(
            'OrderDirectionEnum', {
                "asc": "asc",
                "desc": "desc"
            }
        )
    
    def apply_table_ordering(self, records, column: str, direction: str):
        def order_dir(dir, column):
            if dir == "desc":
                return desc(column)
            return asc(column)
        
        column = column.value if isinstance(column, enum.Enum) else str(column)
        direction = direction.value if isinstance(direction, enum.Enum) else str(direction)
        
        if self._items.get(column, None):
            return records.order_by(order_dir(str(direction), self._items.get(column)))
        
        if self._items.get(self._default, None):
            return records.order_by(order_dir(str(direction), self._items.get(self._default)))
        
        return records