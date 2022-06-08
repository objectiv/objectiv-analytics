"""
Copyright 2022 Objectiv B.V.
"""
import re
import warnings

# https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
_SUPPORTED_C_STANDARD_CODES = {
    # week codes
    '%a',  # WEEKDAY_ABBREVIATED
    '%A',  # WEEKDAY_FULL_NAME
    '%w',  # WEEKDAY_NUMBER
    '%U',  # WEEK_NUMBER_OF_YEAR_SUNDAY_FIRST
    '%W',  # WEEK_NUMBER_OF_YEAR_MONDAY_FIRST

    # day codes
    '%d',  # DAY_OF_MONTH
    '%e',  # DAY_OF_MONTH_PRECEDED_BY_A_SPACE
    '%j',  # DAY_OF_YEAR

    # month codes
    '%b',  # MONTH_ABBREVIATED
    '%h',  # MONTH_ABBREVIATED_2
    '%B',  # MONTH_FULL_NAME
    '%m',  # MONTH_NUMBER

    # year codes
    '%y',  # YEAR_WITHOUT_CENTURY
    '%Y',  # YEAR_WITH_CENTURY
    '%C',  # CENTURY
    '%Q',  # QUARTER
    '%D',  # MONTH_DAY_YEAR
    '%F',  # YEAR_MONTH_DAY

    # iso 8601 codes
    '%G',  # ISO_8601_YEAR_WITH_CENTURY
    '%g',  # ISO_8601_YEAR_WITHOUT_CENTURY
    '%V',  # ISO_8601_WEEK_NUMBER_OF_YEAR
    '%u',  # ISO_8601_WEEKDAY_NUMBER

    # time unit codes
    '%H',  # HOUR24
    '%I',  # HOUR12
    '%k',  # HOUR24_PRECEDED_BY_A_SPACE
    '%l',  # HOUR12_PRECEDED_BY_A_SPACE
    '%M',  # MINUTE
    '%S',  # SECOND
    '%s',  # EPOCH
    '%f',  # MICROSECOND

    '%z',  # UTC_OFFSET
    '%Z',  # TIME_ZONE_NAME

    # format codes
    '%R',  # HOUR_MINUTE
    '%T',  # HOUR_MINUTE_SECOND

    # special characters
    '%n',  # NEW_LINE
    '%t',  # TAB
    '%%',  # PERCENT_CHAR
}

# https://www.postgresql.org/docs/current/functions-formatting.html#FUNCTIONS-FORMATTING-DATETIME-TABLE
_C_STANDARD_CODES_X_POSTGRES_DATE_CODES = {
    "%a": "Dy",
    "%A": "FMDay",
    "%w": "D",  # Sunday is 1 and Saturday is 7
    "%d": "DD",
    "%j": "DDD",
    "%b": "Mon",
    "%h": "Mon",
    "%B": "FMMonth",
    "%m": "MM",
    "%y": "YY",
    "%Y": "YYYY",
    "%C": "CC",
    "%Q": "Q",
    "%D": "MM/DD/YY",
    "%F": "YYYY-MM-DD",
    "%G": "IYYY",
    "%g": "IY",
    "%V": "IW",
    "%u": "ID",
    "%H": "HH24",
    "%I": "HH12",
    "%M": "MI",
    "%S": "SS",
    "%f": "US",
    "%z": "OF",
    "%Z": "TZ",
    "%R": "HH24:MI",
    "%T": "HH24:MI:SS",
}


def parse_c_standard_code_to_postgres_code(date_format: str) -> str:
    """
    Parses a date format string from standard codes to Postgres date codes.
    If c-standard code has no equivalent, it will remain in resultant string.

    Steps to follow:
        date_format = '%Y%m-%Y%m-%Y%m%d-%d'

        Step 1: Get all unique groups of continuous c-codes,
            groups are processed based on length in order to avoid
            replacing occurrences of other groups (e.g %Y%m occurs in %Y%m%d, but both are different groups):
                ['%Y%m%d', '%Y%m', '%d']

        Step 2: Split initial dateformat by c-code groups

        Step 3: For token from previous step:
            If token is not a supported c-code, then treat the token as a literal and quote it.
                (e.g Year: -> "Year:")
            else:
                1) Get individual codes from token
                2) Replace each code with respective Postgres Code
                3) Recreate group by joining all results from previous step with an empty literal.
                    (e.g %Y%m%d -> YYYY""MM""DD

    .. note:: We use double quotes to force TO_CHAR interpret an empty string as literals, this way
            continuous date codes yield the correct value as intended
            For example having '%y%Y':
              TO_CHAR(cast('2022-01-01' as date), 'YY""YYYY') will generate '222022' (correct)
              vs.
              TO_CHAR(cast('2022-01-01' as date), 'YYYYYY') will generate '202222' (incorrect)

    """

    codes_base_pattern = '|'.join(_SUPPORTED_C_STANDARD_CODES)
    grouped_codes_matches = re.findall(pattern=rf"(?P<codes>(?:{codes_base_pattern})+)", string=date_format)
    if not grouped_codes_matches:
        # return it as a literal
        date_format = date_format.replace('"', r'\"')
        return f'"{date_format}"'

    tokenized_c_codes = sorted(set(grouped_codes_matches), key=len, reverse=True)
    unsupported_c_codes = set()
    single_c_code_regex = re.compile(rf'{codes_base_pattern}')

    new_date_format_tokens = []
    all_tokens = re.split(pattern=rf"({'|'.join(tokenized_c_codes)})", string=date_format)
    for token in all_tokens:
        # empty space
        if not token:
            continue

        # is a literal
        if token not in tokenized_c_codes:
            formatted_literal = token.replace('"', r'\"')
            new_date_format_tokens.append(f'"{formatted_literal}"')
            continue

        # get individual codes from the group
        codes_to_replace = single_c_code_regex.findall(token)
        replaced_codes = []
        for to_repl_code in codes_to_replace:
            if to_repl_code not in _C_STANDARD_CODES_X_POSTGRES_DATE_CODES:
                unsupported_c_codes.add(to_repl_code)
                replaced_codes.append(to_repl_code)
                continue

            # get correspondent postgres code
            replaced_codes.append(_C_STANDARD_CODES_X_POSTGRES_DATE_CODES[to_repl_code])

        new_date_format_tokens.append('""'.join(replaced_codes))

    if unsupported_c_codes:
        warnings.warn(
            message=f'There are no equivalent codes for {sorted(unsupported_c_codes)}.',
            category=UserWarning,
        )

    return ''.join(new_date_format_tokens)


def parse_c_code_to_bigquery_code(date_format: str) -> str:
    """
    Replaces all '%S.%f' with '%E6S', since BigQuery does not support microseconds c-code.
    """
    if '%S.%f' in date_format:
        date_format = re.sub(r'%S\.%f', '%E6S', date_format)

    if '%f' in date_format:
        warnings.warn(
            message=f'There are no equivalent codes for %f.',
            category=UserWarning,
        )
    return date_format
