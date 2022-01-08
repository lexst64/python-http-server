from typing import Any


class OffsetIterator:
    def __init__(self, items, step: int = 1) -> None:
        self.items = list(items)
        self.offset = 0
        if step == 0:
            raise ValueError('step arg must be > 0')
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        # while self.items: return self.items.pop()
        while self.offset < len(self.items):
            item = self.items[self.offset]
            self.offset += self.step
            return item
        raise StopIteration


class Iterable:
    def __init__(self, items: list | tuple) -> None:
        self.items = items
        self._change = 2
    
    def __iter__(self):
        return OffsetIterator(self.items, 1)
        # return (i for i in self.items)
        # yield from self.items

    def __contains__(self, value):
        return value in self.items

    def __getitem__(self, index):
        return self.items[index]
    
    def __setitem__(self, index, value):
        self.items[index] = value

    # it invokes when python can't find attr in inheritance tree
    def __getattr__(self, __name):
        # return None
        raise AttributeError('Attribute not found')
    
    # when raises AttributeError, __getattr__ is invoked
    def __getattribute__(self, __name: str) -> Any:
        return super().__getattribute__(__name)

    # catches all attr changes and assigns
    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name.startswith('_') and __name in self.__dict__:
            raise AttributeError('private attrs cannot be changed')
        self.__dict__[__name] = __value

    def __delattr__(self, __name: str) -> None:
        if __name not in self.__dict__:
            raise AttributeError('Attribute not found')
        if __name.startswith('_'):
            raise AttributeError('private attrs cannot be deleted')
        del self.__dict__[__name]
    
    # has more priority than __len__
    def __bool__(self):
        return bool(self.items)
    
    def __len__(self):
        return len(self.items)


iterable = Iterable(tuple(range(10)))
for i in iterable:
    print(i)
print(2 in iterable)
