"""Persistent configuration handling.

To access the settings, import the "settings" object. This is a nested set of `dict` objects that are automatically
loaded from a ".env" file, if one exists in the current working directory.
"""


class DottedDictException(Exception):
    """An exception accessing a DottedDict."""

    pass


class DottedDict:
    """A dict-like object that allows access via dotted strings."""

    def __init__(self: 'DottedDict') -> None:
        """Initialise an empty DottedDict."""
        self._data = {}

    def __setitem__(self: 'DottedDict', key: str, value) -> None:  # noqa: ANN001
        """Set a value."""
        key = key.lower()
        head, tail = self.__splitkey__(key)
        if head in self._data:
            if tail is None:
                if isinstance(self._data[head], DottedDict):
                    raise DottedDictException(f'{head} must not be a DottedDict')
                else:
                    self._data[head] = value
            else:
                if isinstance(self._data[head], DottedDict):
                    self._data[head][tail] = value
                else:
                    raise DottedDictException(f'{head} is required to be a DottedDict')
        else:
            if tail is not None:
                self._data[head] = DottedDict()
                self._data[head][tail] = value
            else:
                self._data[head] = value

    def __getitem__(self: 'DottedDict', key: str):  # noqa: ANN204
        """Get a value via a key."""
        key = key.lower()
        head, tail = self.__splitkey__(key)
        value = self._data[head]
        if tail is None:
            return value
        elif isinstance(value, DottedDict):
            return value[tail]
        else:
            raise DottedDictException(f'{head} is required to be a DottedDict')

    def __contains__(self: 'DottedDict', key: str) -> bool:
        """Check whether a key exists."""
        key = key.lower()
        head, tail = self.__splitkey__(key)
        if head in self._data:
            if tail is None:
                return True
            if isinstance(self._data[head], DottedDict):
                return tail in self[head]
        return False

    def __splitkey__(self: 'DottedDict', key: str):  # noqa: ANN204
        """Split the key into head and tail."""
        if '.' in key:
            return (key[0:key.find('.')], key[key.find('.') + 1:])
        else:
            return (key, None)

    def __repr__(self: 'DottedDict') -> str:
        """Return a representation of this DottedDict."""
        return f'DottedDict({self._data})'

    def serialise(self: 'DottedDict') -> list:
        """Serialise the data into a list of key, value tuples."""
        items = []
        for key, value in self._data.items():
            if (isinstance(value, DottedDict)):
                for sub_key, sub_value in value.serialise():
                    items.append((f'{key}.{sub_key}', sub_value))
            else:
                items.append((key, value))
        return items


class PersistentConfiguration(DottedDict):
    """Access settings defined in a .env file."""

    def __init__(self: 'PersistentConfiguration') -> None:
        """Create a Settings object, loading settings from the .env file."""
        super().__init__()
        try:
            with open('.env') as in_f:
                for line in in_f.readlines():
                    line = line.strip()
                    if line.startswith('#'):
                        continue
                    if '=' in line:
                        key = line[0:line.find('=')]
                        value = line[line.find('=') + 1:]
                        super().__setitem__(key, value)
        except OSError as e:
            print(e)

    def __setitem__(self: 'PersistentConfiguration', key: str, value) -> None:  # noqa: ANN001
        """Persist the updated configuration values."""
        super().__setitem__(key, value)
        try:
            with open('.env', 'w') as out_f:
                for key, value in self.serialise():
                    print(f'{key.upper()}={value}', file=out_f)
        except OSError as e:
            print(e)


settings = PersistentConfiguration()
