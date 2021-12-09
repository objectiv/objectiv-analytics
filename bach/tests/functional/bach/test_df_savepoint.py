"""
Copyright 2021 Objectiv B.V.
"""
from bach.savepoints import Savepoints
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data


def test_savepoint_simple():
    df = get_bt_with_test_data()
    engine = df.engine
    sp = Savepoints()
    df.set_savepoint(sp, "savepoint1")
    result = sp.execute(engine)
    assert result == {
        'savepoint1': [
            (1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285),
            (2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456),
            (3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268)
        ]
    }

    df['x'] = 'abcdef'
    df = df[['city', 'founding', 'x']]
    df = df.materialize()
    df.set_savepoint(sp, "savepoint2")
    result = sp.execute(engine)
    assert result == {
        'savepoint1': [
            (1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285),
            (2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456),
            (3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268)
        ],
        'savepoint2': [
            (1, 'Ljouwert', 1285, 'abcdef'),
            (2, 'Snits', 1456, 'abcdef'),
            (3, 'Drylts', 1268, 'abcdef')
        ]
    }
