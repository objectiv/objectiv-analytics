"""
Copyright 2021 Objectiv B.V.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ExpressionToken:
    pass


@dataclass(frozen=True)
class TextToken(ExpressionToken):
    value: str


@dataclass(frozen=True)
class TableToken(ExpressionToken):
    pass


@dataclass(frozen=True)
class Expression:
    data: List[ExpressionToken] = field(default_factory=list)

    @classmethod
    def construct(cls, fmt: str, *args: 'Expression') -> 'Expression':
        """ TODO: comments"""
        # todo: maybe use a different placeholder than {}, so as not to clash with format?
        sub_strs = fmt.split('{}')
        data = []
        if len(args) != len(sub_strs) - 1:
            raise ValueError(f'For each {{}} in the fmt there should be an Expression provided. '
                             f'Found {{}}: {len(sub_strs) - 1}, provided expressions: {len(args)}')
        for i, sub_str in enumerate(sub_strs):
            if i > 0:
                data.extend(args[i - 1].data)
            if sub_str != '':
                data.append(TextToken(value=sub_str))
        return cls(data=data)

    @classmethod
    def construct_raw(cls, value: str) -> 'Expression':
        """ TODO: comments"""
        return Expression([TextToken(value)])

    @classmethod
    def construct_table_field(cls, field_name: str) -> 'Expression':
        """ Construct an expression for field-name, where field-name is in a table or cte. """
        # todo escape quotes in field_name
        return Expression([TableToken(), TextToken(f'"{field_name}"')])

    def to_string(self, table_name: Optional[str] = None) -> str:
        """ TODO: comments """
        data_str = []
        for data_item in self.data:
            if isinstance(data_item, TableToken):
                if table_name:
                    data_str.append('"')
                    data_str.append(table_name)  # todo: escape quotes in table_name?
                    data_str.append('".')
            elif isinstance(data_item, TextToken):
                data_str.append(data_item.value)
            else:
                raise Exception("This should never happen; programming error.")
        return ''.join(data_str)
