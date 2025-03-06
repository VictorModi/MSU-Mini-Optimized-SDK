from typing import Final, List

DEVICE_RESPONSE_PREFIX: Final[bytes] = b'MSN'
DEVICE_INITIAL_COMMAND: Final[bytes] = b'\x00MSNCN'

DEFAULT_BAUD_RATE: Final[int] = 19200

DEFAULT_WIDTH: Final[int] = 160
DEFAULT_HEIGHT: Final[int] = 80

MAX_RETRIES: Final[int] = 5

SERIAL_TIMEOUT: Final[int] = 2

SERIAL_EXCEPTION_DESCRIPTION: Final[List[str]] = ["Bluetooth", "蓝牙"]
