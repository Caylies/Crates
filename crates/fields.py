from query_builder_widget.types import QueryBuilderField

_BOOLEAN_OPERATORS = (("equals", "="), ("not_equals", "!="))

_COMMON_NUMBER_OPERATORS = (
    *_BOOLEAN_OPERATORS,
    ("greater", ">"),
    ("greater_or_equal", ">="),
    ("less", "<"),
    ("less_or_equal", "<="),
)

POOL_FIELDS: dict[str, QueryBuilderField] = {
    "completion": {"text": "Ball completion percentage", "operators": _COMMON_NUMBER_OPERATORS},
    "ball_count": {"text": "Ball count", "operators": _COMMON_NUMBER_OPERATORS},
    "server": {"text": "Server", "operators": _BOOLEAN_OPERATORS},
    "user": {"text": "User", "operators": _BOOLEAN_OPERATORS},
}
