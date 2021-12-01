"""
Copyright 2021 Objectiv B.V.
"""
import string

from sql_models.model import SqlModelBuilder


def assert_roughly_equal_sql(sql_a: str, sql_b: str):
    """ Check that two strings are equal after removing whitespace"""
    # TODO check sql better
    whitespace_remove_trans = str.maketrans(dict.fromkeys(string.whitespace))
    a_stripped = sql_a.translate(whitespace_remove_trans)
    b_stripped = sql_b.translate(whitespace_remove_trans)
    if a_stripped != b_stripped:
        print(f'\n\n{a_stripped}\n\n != \n\n{b_stripped}\n\n')
        raise AssertionError(f'\n\n{a_stripped}\n\n != \n\n{b_stripped}\n\n')


class ValueModel(SqlModelBuilder):
    @property
    def sql(self) -> str:
        return "select '{key}' as key, {val} as value"


class RefModel(SqlModelBuilder):
    @property
    def sql(self) -> str:
        return 'select * from {{ref}}'


class RefValueModel(SqlModelBuilder):
    @property
    def sql(self) -> str:
        return 'select key, value + {val} as value from {{ref}}'


class JoinModel(SqlModelBuilder):
    @property
    def sql(self) -> str:
        return '''
            select l.key, l.value + r.value as value
            from {{ref_left}} as l
            inner join {{ref_right}} as r on l.key=r.key
        '''
