import re
from typing import Dict

from sqlalchemy.engine import Engine

from sql_models.util import is_bigquery, is_postgres

# https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
_STANDARD_DATE_FORMAT_CODES = {
    # week codes
    'WEEKDAY_ABBREVIATED': '%a',
    'WEEKDAY_FULL_NAME': '%A',
    'WEEKDAY_NUMBER': '%w',  # Sunday is 0, Saturday is 6
    'WEEK_NUMBER_OF_YEAR_SUNDAY_FIRST': '%U',
    'WEEK_NUMBER_OF_YEAR_MONDAY_FIRST': '%W',

    # day codes
    'DAY_OF_MONTH': '%d',
    'DAY_OF_MONTH_SUPPRESSED': '%-d',
    'DAY_OF_MONTH_PRECEDED_BY_A_SPACE': '%e',
    'DAY_OF_YEAR': '%j',
    'DAY_OF_YEAR_SUPPRESSED': '%-j',

    # month codes
    'MONTH_ABBREVIATED': '%b',
    'MONTH_ABBREVIATED_2': '%h',
    'MONTH_FULL_NAME': '%B',
    'MONTH_NUMBER': '%m',
    'MONTH_NUMBER_SUPPRESSED': '%-m',

    # year codes
    'YEAR_WITHOUT_CENTURY': '%y',
    'YEAR_WITH_CENTURY': '%Y',
    'CENTURY': '%C',
    'QUARTER': '%Q',
    'MONTH_DAY_YEAR': '%D',  # MM/DD/YY
    'YEAR_MONTH_DAY': '%F',  # YYYY/MM/DD

    # iso 8601 codes
    'ISO_8601_YEAR_WITH_CENTURY': '%G',
    'ISO_8601_YEAR_WITHOUT_CENTURY': '%g',
    'ISO_8601_WEEK_NUMBER_OF_YEAR': '%V',
    'ISO_8601_WEEKDAY_NUMBER': '%u',  # Monday is 1, Sunday is 7

    # time unit codes
    'HOUR24': '%H',
    'HOUR24_SUPPRESSED': '%-H',
    'HOUR12': '%I',
    'HOUR12_SUPPRESSED': '%-I',
    'HOUR24_PRECEDED_BY_A_SPACE': '%k',
    'HOUR12_PRECEDED_BY_A_SPACE': '%l',
    'MINUTE': '%M',
    'MINUTE_SUPPRESSED': '%-M',
    'SECOND': '%S',
    'SECOND_SUPPRESSED': '%-S',
    'EPOCH': '%s',
    'MICROSECOND': '%f',

    'AM_OR_PM_UPPER': '%p',
    'AM_OR_PM_LOWER': '%P',
    'UTC_OFFSET': '%z',
    'TIME_ZONE_NAME': '%Z',

    # format codes
    'HOUR_MINUTE': '%R',
    'HOUR_MINUTE_SECOND': '%T',
    'LOCALE_DATE_TIME': '%c',
    'LOCALE_DATE': '%x',  # MM/DD/YY
    'LOCALE_TIME': '%X',  # HH:MM:SS

    # special characters
    'NEW_LINE': '%n',
    'TAB': '%t',
    'PERCENT_CHAR': '%%',
}

# https://www.postgresql.org/docs/current/functions-formatting.html#FUNCTIONS-FORMATTING-DATETIME-TABLE
_POSTGRES_DATE_FORMAT_CODES = {
    # week codes
    'WEEKDAY_ABBREVIATED': 'Dy',
    'WEEKDAY_FULL_NAME': 'FMDay',
    'WEEKDAY_NUMBER': 'D',  # Sunday is 1 and Saturday is 7

    # day codes
    'DAY_OF_MONTH': 'DD',
    'DAY_OF_MONTH_SUPPRESSED': 'FMDD',
    'DAY_OF_YEAR': 'DDD',
    'DAY_OF_YEAR_SUPPRESSED': 'FMDDD',

    # month codes
    'MONTH_ABBREVIATED': 'Mon',
    'MONTH_ABBREVIATED_2': 'Mon',
    'MONTH_FULL_NAME': 'FMMonth',
    'MONTH_NUMBER': 'MM',
    'MONTH_NUMBER_SUPPRESSED': 'FMMM',

    # year codes
    'YEAR_WITHOUT_CENTURY': 'YY',
    'YEAR_WITH_CENTURY': 'YYYY',
    'CENTURY': 'CC',

    # quarter
    'QUARTER': 'Q',

    # date formats
    'MONTH_DAY_YEAR': 'MM/DD/YY',
    'YEAR_MONTH_DAY': 'YYYY-MM-DD',

    # iso 8601
    'ISO_8601_YEAR_WITH_CENTURY': 'IYYY',
    'ISO_8601_YEAR_WITHOUT_CENTURY': 'IY',
    'ISO_8601_WEEK_NUMBER_OF_YEAR': 'IW',
    'ISO_8601_WEEKDAY_NUMBER': 'ID',  # Monday is 1, Sunday is 7

    # time units
    'HOUR24': 'HH24',
    'HOUR24_SUPPRESSED': 'FMHH24',
    'HOUR12': 'HH12',
    'HOUR12_SUPPRESSED': 'FMHH12',
    'MINUTE': 'MI',
    'MINUTE_SUPPRESSED': 'FMMI',
    'SECOND': 'SS',
    'SECOND_SUPPRESSED': 'FMSS',
    'MICROSECOND': 'US',

    'AM_OR_PM_UPPER': 'AM',
    'AM_OR_PM_LOWER': 'am',

    # utc and timezone
    'UTC_OFFSET': 'OF',
    'TIME_ZONE_NAME': 'TZ',

    # time formats
    'HOUR_MINUTE': 'HH24:MI',
    'HOUR_MINUTE_SECOND': 'HH24:MI:SS',

    # locale based formats
    'LOCALE_DATE_TIME': 'Dy Mon  FMDD HH24:MI:SS YYYY',
    'LOCALE_DATE': 'MM/DD/YY',
    'LOCALE_TIME': 'HH24:MI:SS',
}


# BQ has no code for suppressing leading zeros
_BIGQUERY_DATE_FORMAT_SUPPRESSED_CODES = {
    'DAY_OF_MONTH_SUPPRESSED': '%d',
    'DAY_OF_YEAR_SUPPRESSED': '%j',
    'MONTH_NUMBER_SUPPRESSED': '%m',
    'HOUR24_SUPPRESSED': '%H',
    'HOUR12_SUPPRESSED': '%I',
    'MINUTE_SUPPRESSED': '%M',
    'SECOND_SUPPRESSED': '%S',
}

# https://cloud.google.com/bigquery/docs/reference/standard-sql/format-elements#format_elements_date_time
_BIGQUERY_DATE_FORMAT_CODES = {
    **_STANDARD_DATE_FORMAT_CODES,
    **_BIGQUERY_DATE_FORMAT_SUPPRESSED_CODES,
}


def parse_date_format_str(engine: Engine, date_format: str) -> str:
    """
    Parses a date format string from standard codes to its supported codes based on engine.
    If standard code has no equivalent, it will remain in resultant string.
    """
    if not is_bigquery(engine) and not is_postgres(engine):
        return date_format

    if is_bigquery(engine):
        codes_to_replace = {
            code_name: _STANDARD_DATE_FORMAT_CODES[code_name]
            for code_name in _BIGQUERY_DATE_FORMAT_SUPPRESSED_CODES.keys()
        }
        new_codes = _BIGQUERY_DATE_FORMAT_SUPPRESSED_CODES
    else:
        codes_to_replace = _STANDARD_DATE_FORMAT_CODES
        new_codes = _POSTGRES_DATE_FORMAT_CODES

    return _replace_date_codes(
        codes_to_replace=codes_to_replace,
        new_codes=new_codes,
        date_format=date_format
    )


def _replace_date_codes(
    *,
    codes_to_replace: Dict[str, str],
    new_codes: Dict[str, str],
    date_format: str,
) -> str:
    """
    Helper function that replaces a string's date codes with its equivalent.
    :param codes_to_replace: Dictionary containing all c-standard codes to be replaced.
    :param new_codes: Dictionary containing codes used for replacement. Code will be used if key exists in
        codes_to_replace.
    :param date_format: string to be replaced

    returns the string obtained by replacing old codes with new codes.
    """
    to_repl_codes_tokens = re.findall(pattern='|'.join(codes_to_replace.values()), string=date_format)

    new_date_format = date_format
    for to_repl_code in to_repl_codes_tokens:
        code_name = [name for name, code in codes_to_replace.items() if code == to_repl_code][0]
        if code_name not in new_codes:
            continue

        new_code = new_codes[code_name]
        new_date_format = re.sub(pattern=rf'{to_repl_code}', repl=new_code, string=new_date_format)

    return new_date_format
