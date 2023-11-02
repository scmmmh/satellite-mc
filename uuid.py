"""UUID generation module."""
import os
import ubinascii


class UUID:
    """Generic UUID class."""

    def __init__(self: 'UUID', bytes: bytearray) -> None:
        """Initialise with the given bytes."""
        if len(bytes) != 16:
            raise ValueError('bytes arg must be 16 bytes long')
        self._bytes = bytes

    @property
    def hex(self: 'UUID') -> str:
        """Return as a hex string."""
        return ubinascii.hexlify(self._bytes).decode()

    def __str__(self: 'UUID') -> str:
        """Return hex string representation of this UUID."""
        h = self.hex
        return '-'.join((h[0:8], h[8:12], h[12:16], h[16:20], h[20:32]))

    def __repr__(self: 'UUID') -> str:
        """Return the bytes representation of this UUID."""
        return "<UUID: %s>" % str(self)


def uuid4() -> UUID:
    """Generate a random UUID compliant to RFC 4122 pg.14."""
    random = bytearray(os.urandom(16))
    random[6] = (random[6] & 0x0F) | 0x40
    random[8] = (random[8] & 0x3F) | 0x80
    return UUID(bytes=random)
