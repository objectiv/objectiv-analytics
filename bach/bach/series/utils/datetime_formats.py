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

    '%p',  # AM_OR_PM_UPPER
    '%P',  # AM_OR_PM_LOWER
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
    "%p": "AM",
    "%P": "am",
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

        Step 2: For each group
                                                               '%Y%m%d'             %Y%m'      '%d'
            1) Get individual codes                       ['%Y', '%m', '%d']   ['%Y', '%m']   ['%d']
            2) Replace with respective Postgres Code     ['YYYY', 'MM', 'DD'] ['YYYY', 'MM']  ['DD']
            3) Recreate group (joined by ")                 'YYYY"MM"DD'        'YYYY"MM'      'DD'
            4) Replace all original group occurrences
               in original date_format string               'YYYY""MM-YYYY""MM-YYYY""MM""DD-DD'
               with result from previous step

    .. note:: We use double quotes to force TO_CHAR interpret an empty string as literals, this way
            continuous date codes yield the correct value as intended
            For example having '%y%Y':
              TO_CHAR(cast('2022-01-01' as date), 'YY""YYYY') will generate '222022' (correct)
              vs.
              TO_CHAR(cast('2022-01-01' as date), 'YYYYYY') will generate '202222' (incorrect)

    """

    codes_base_pattern = '|'.join(_SUPPORTED_C_STANDARD_CODES)
    grouped_codes_matches = re.findall(pattern=rf"(?P<codes>({codes_base_pattern})+)", string=date_format)
    if not grouped_codes_matches:
        return date_format

    # regex used in findall has 2 groups, we are interested in the first group
    # Here we get all unique groups of continuous c-codes, sorted by largest to smaller
    # this way we avoid replacing nested groups
    tokenized_c_codes = sorted({tokens for tokens, _ in grouped_codes_matches}, key=len, reverse=True)
    unsupported_c_codes = set()
    single_c_code_regex = re.compile(rf'{codes_base_pattern}')

    new_date_format = date_format
    for grouped_c_codes in tokenized_c_codes:
        # get individual codes from the group
        codes_to_replace = single_c_code_regex.findall(grouped_c_codes)
        replaced_codes = []
        for to_repl_code in codes_to_replace:
            if to_repl_code not in _C_STANDARD_CODES_X_POSTGRES_DATE_CODES:
                unsupported_c_codes.add(to_repl_code)
                replaced_codes.append(to_repl_code)
                continue

            # get correspondent postgres code
            replaced_codes.append(_C_STANDARD_CODES_X_POSTGRES_DATE_CODES[to_repl_code])

        # replace all group occurrences
        new_date_format = re.sub(
            pattern=rf'({grouped_c_codes})', repl='""'.join(replaced_codes), string=new_date_format,
        )

    if unsupported_c_codes:
        warnings.warn(
            message=f'There are no equivalent codes for {sorted(unsupported_c_codes)}.',
            category=UserWarning,
        )

    return new_date_format
