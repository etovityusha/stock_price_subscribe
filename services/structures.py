from typing import Generic, Hashable, Iterable, Iterator, TypeVar

ValueType = TypeVar("ValueType")


class OrderedSet(Generic[ValueType]):
    """
    An ordered set implementation in Python.

    This class provides a generic implementation of an ordered set data structure.
    An ordered set is a collection of unique elements with a defined order.

    Attributes:
        dict (dict[ValueType, None]): A dictionary that stores the elements of the set.

    Generic Parameters:
        ValueType: The type of values stored in the set.

    Methods:
        __init__(objects: Iterable[ValueType] | None = None) -> None:
            Initializes an OrderedSet object with optional initial values.

        add(value: ValueType) -> None:
            Adds a value to the set.

        remove(value: ValueType) -> None:
            Removes a value from the set.

        __contains__(value: Hashable) -> bool:
            Checks if a value is present in the set.

        __iter__() -> Iterator[ValueType]:
            Returns an iterator over the elements in the set.

        __len__() -> int:
            Returns the number of elements in the set.

        __str__() -> str:
            Returns a string representation of the set.

        __repr__() -> str:
            Returns a string representation of the set.

        first() -> ValueType | None:
            Returns the first element of the set.

    """

    def __init__(self, objects: Iterable[ValueType] | None = None) -> None:
        self.dict: dict[ValueType, None] = {value: None for value in objects} if objects else {}

    def add(self, value: ValueType) -> None:
        self.dict[value] = None

    def remove(self, value: ValueType) -> None:
        if value in self.dict:
            self.dict.pop(value)

    def __contains__(self, value: Hashable) -> bool:
        return value in self.dict

    def __iter__(self) -> Iterator[ValueType]:
        return iter(self.dict)

    def __len__(self) -> int:
        return len(self.dict)

    def __str__(self) -> str:
        return self._repr()

    def __repr__(self) -> str:
        return self._repr()

    def _repr(self) -> str:
        return "{" + ", ".join(repr(key) for key in self.dict) + "}"

    def first(self) -> ValueType | None:
        try:
            return next(iter(self.dict))
        except StopIteration:
            return None
