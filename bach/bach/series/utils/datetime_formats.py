from enum import Enum


# https://strftime.org/
class SupportedDateFormatCodes(Enum):
    ABBREVIATED_WEEKDAY = '%a'
    WEEKDAY = '%A'
    WEEKDAY_NUMBER = '%w'
    DAY = 'DD'
    ABBREVIATED_MONTH = 'Mon'
    MONTH = 'Month'
    MONTH_NUMBER = 'MM'
    YEAR_WITHOUT_CENTURY = '%y'
    YEAR_WITH_CENTURY = '%Y'

    HOUR24 = '%H'
    HOUR12 = '%I'
    AM_OR_PM = '%p'
    MINUTE = '%M'
    SECOND = '%S'
    MICROSECOND = '%f'
    UTC_OFFSET = '%z'
    TIME_ZONE_NAME = '%Z'

    DAY_OF_YEAR = '%j'
    WEEK_NUMBER_OF_YEAR_SUNDAY_FIRST = '%U'
    WEEK_NUMBER_OF_YEAR_MONDAY_FIRST = '%W'

    LOCALE_DATE_TIME = '%c'
    LOCALE_DATE = '%x'
    LOCALE_TIME = '%X'

    _CAN_BE_NON_ZERO_PADDED = (
        DAY, MONTH_NUMBER, HOUR24, HOUR12, MINUTE, SECOND, DAY_OF_YEAR,
    )


class PostgresSupportedDateFormatCodes(Enum):
    ABBREVIATED_WEEKDAY = '%a'
    WEEKDAY = '%A'
    WEEKDAY_NUMBER = '%w'
    DAY = '%d'
    ABBREVIATED_MONTH = '%b'
    MONTH = '%B'
    MONTH_NUMBER = '%m'
    YEAR_WITHOUT_CENTURY = 'YY'
    YEAR_WITH_CENTURY = 'YYYY'

    HOUR24 = 'HH24'
    HOUR12 = 'HH12'
    MINUTE = 'MI'
    SECOND = 'SS'
    MICROSECOND = 'US'
    UTC_OFFSET = 'OF'
    TIME_ZONE_NAME = 'TZ'
