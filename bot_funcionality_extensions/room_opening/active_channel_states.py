
# create enum for channel states
from enum import Enum
class ChannelState(Enum):
    PUBLIC = 1
    PRIVATE = 2
    SPECIAL = 3
