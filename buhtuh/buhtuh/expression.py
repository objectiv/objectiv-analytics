"""
Copyright 2021 Objectiv B.V.
"""
from dataclasses import dataclass
from typing import Union, TYPE_CHECKING

import sql_models.expression

if TYPE_CHECKING:
    from buhtuh import BuhTuhSeries


@dataclass(frozen=True)
class Expression(sql_models.expression.Expression):
    """
    An Expression object represents a fragment of SQL as a series of sql-tokens.
    This one extends the sql_models.Expression, and just overrides one method to allow
    BuhTuhSeries to be passed.

    """
    @classmethod
    def construct(cls, fmt: str, *args: Union['Expression', 'BuhTuhSeries']) -> 'Expression':
        """
        Construct an Expression using a format string that can refer existing expressions.
        Every occurrence of `{}` in the fmt string will be replace with a provided expression (in order that
        they are given). All other parts of fmt will be converted to RawTokens.

        As a convenience, instead of Expressions it is also possible to give BuhTuhSeries as args, in that
        case the series's expression is taken as Expression.

        :param fmt: format string
        :param args: 0 or more Expressions or BuhTuhSeries. Number of args must exactly match number of `{}`
            occurrences in fmt.
        """
        from buhtuh.series import BuhTuhSeries
        return super().construct(fmt, *[a.expression if isinstance(a, BuhTuhSeries) else a for a in args])
