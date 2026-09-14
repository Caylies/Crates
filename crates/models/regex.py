import re

SLASH_COMMAND_RE = re.compile(r"^[a-z0-9_-]{1,32}$")
HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
