"""
Copyright 2022 Objectiv B.V.
"""
from functools import reduce
from typing import Union, List, Optional, Tuple, TYPE_CHECKING, overload

from bach.expression import Expression

if TYPE_CHECKING:
    from bach.dataframe import DataFrame
    from bach.series.series import Series, SeriesBoolean
    from bach.types import AllSupportedLiteralTypes

IndexLabel = Union['SeriesBoolean', List[str], List[int]]
LocKey = Union[IndexLabel, Tuple[Union[IndexLabel, slice], Union[str, slice]]]


class BaseLocIndex(object):
    """
    Base class for `loc` property. Contains helper methods for getting and setting values.
    """
    obj: 'DataFrame'

    def __init__(self, obj: 'DataFrame'):
        self.obj = obj

    def _get_data_columns_subset(self, labels: Union[slice, str, List[str]]) -> List[str]:
        """
        returns a list of column labels
        """
        if isinstance(labels, slice):
            return self._parse_column_slicing(labels)

        return [
            label
            for label in (labels if isinstance(labels, list) else [labels])
            if self._get_label_index(label) is not None
        ]

    def _parse_column_slicing(self, label_slicing: slice) -> List[str]:
        """
        returns a subset of labels based on a slice
        """
        data_columns = self.obj.data_columns
        if label_slicing.start is None and label_slicing.stop is None:
            return data_columns

        index_start = self._get_label_index(label_slicing.start) if label_slicing.start else None
        index_stop = self._get_label_index(label_slicing.stop) + 1 if label_slicing.stop else None

        if index_start is not None and index_stop is not None:
            return data_columns[index_start:index_stop]

        if index_start is not None:
            return data_columns[index_start:]

        return data_columns[:index_stop]

    def _get_label_index(self, label: str) -> int:
        """
        returns the position of the label in the dataframe
        """
        if label not in self.obj.data_columns:
            raise ValueError(f'{label} does not exists in data columns')

        return self.obj.data_columns.index(label)

    def _get_index_label_mask(self, labels: Union[int, str, IndexLabel]) -> 'SeriesBoolean':
        """
        returns a boolean series representing the subset to get
        """
        from bach.series import SeriesBoolean
        if not self.obj.index and not isinstance(labels, SeriesBoolean):
            raise ValueError('Cannot access rows by label if DataFrame/Series has no index.')

        if isinstance(labels, SeriesBoolean):
            return labels

        level_0_index = self.obj.index_columns[0]

        list_of_labels = [labels] if isinstance(labels, (str, int)) else labels
        loc_conditions = [self.obj.index[level_0_index] == label for label in list_of_labels]
        return reduce(lambda cond1, cond2: cond1 | cond2, loc_conditions)

    def _get_sliced_subset(
        self,
        start: Optional[Union[str, int]],
        stop: Optional[Union[str, int]],
    ) -> 'DataFrame':
        """
        returns a subset from the caller based on the slicing filters.

        In order to identify the subset, the following steps are performed:
        1. Number each row based on the index
        2. Identify the position of the start and stop labels.
        3. Get the rows which row numbers are between start and stop positions (stop is inclusive).
            start_row_number <= current_row_number <= stop_row_number
        .. note::
          caller should be sorted in order to perform slicing operations.
        """
        start_stop_labels = [lbl for lbl in [start, stop] if lbl is not None]
        if not start_stop_labels:
            return self.obj.copy()

        if not self.obj.index and (start or stop):
            raise ValueError('Cannot slice rows if DataFrame/Series has no index.')

        if not self.obj.order_by:
            raise ValueError('Can only apply index slicing if DataFrame/Series is sorted.')

        numbered_df = self.__get_numbered_df_by_index()

        # need this constant since we cannot merge 2 dataframes without indexes
        numbered_df['constant_index'] = 1
        start_stop_df = numbered_df[['constant_index', 'position']].loc[start_stop_labels]
        start_stop_df = start_stop_df.groupby(by='constant_index').agg({'position': ['min', 'max']})
        start_stop_df = start_stop_df.materialize('loc_start_stop')

        numbered_df = numbered_df.reset_index(drop=False).set_index('constant_index')
        mask = []
        if start:
            mask.append(numbered_df['position'] >= start_stop_df['position_min'])

        if stop:
            mask.append(numbered_df['position'] <= start_stop_df['position_max'])

        sliced_df = numbered_df.merge(start_stop_df, on=mask)
        sliced_df = sliced_df.set_index(list(self.obj.index_columns), drop=True)
        sliced_df = sliced_df[self.obj.data_columns]
        return sliced_df

    def __get_numbered_df_by_index(self) -> 'DataFrame':
        """
        Returns the number of the current row within the index
        """
        from bach.partitioning import Window, WindowFrameMode

        level_0_index = self.obj.index_columns[0]

        numbered_df = self.obj.copy()
        numbered_df['position'] = numbered_df.all_series[level_0_index].window_row_number(
            window=Window([], mode=WindowFrameMode.ROWS, order_by=self.obj.order_by),
        )

        return numbered_df.materialize('numbered_index')


class LocIndexer(BaseLocIndex):
    """
    Enables setting and getting operations for DataFrame and Series.
    See :py:attr:`bach.DataFrame.loc` for more information.
    """
    @overload
    def __getitem__(self, key: Union[str, int]) -> 'Series':
        ...

    @overload
    def __getitem__(self, key: LocKey) -> 'DataFrame':
        ...

    def __getitem__(self, key):
        """
        returns a dataframe or series based on the key to be found.
        """
        if isinstance(key, tuple):
            index_labels, column_labels = key
        else:
            index_labels = key
            column_labels = None

        if isinstance(index_labels, slice):
            filtered_index_df = self._get_sliced_subset(index_labels.start, index_labels.stop)
        else:
            filtered_index_df = self.obj[self._get_index_label_mask(index_labels)]

        if column_labels:
            filtered_index_df = filtered_index_df[self._get_data_columns_subset(column_labels)]

        # if index_accessor is a single label, it returns a series
        if isinstance(index_labels, (str, int)):
            return filtered_index_df.reset_index(drop=True).stack()

        return filtered_index_df

    def __setitem__(self, key: LocKey, value: 'AllSupportedLiteralTypes') -> None:
        """
        modifies a subset from the caller based on a key.
        """
        from bach.series.series import Series, value_to_series
        if isinstance(key, tuple):
            index_labels, column_labels = key
            parsed_column_labels = self._get_data_columns_subset(column_labels)
        else:
            index_labels = key
            parsed_column_labels = self.obj.data_columns
        series_value = value if isinstance(value, Series) else value_to_series(self.obj, value)

        if not isinstance(index_labels, slice):
            df = self._set_item_by_labels(index_labels, parsed_column_labels, series_value)
        else:
            df = self._set_item_by_slicing(index_labels, parsed_column_labels, series_value)

        # TODO: remove call to private method
        self.obj._update_self_from_df(df)

    def _set_item_by_labels(
        self, labels: IndexLabel, col_labels: List[str], value: 'Series',
    ) -> 'DataFrame':
        """
        returns a new dataframe with replaced values based on labels.
        Adds a case when clause for each column to be modified.
        """
        from bach.utils import get_merged_series_dtype

        mask = self._get_index_label_mask(labels)
        base_expr = f'CASE WHEN {{}} THEN {{}} ELSE {{}} END'

        obj_copy = self.obj.copy()
        # add series, this way we avoid duplicating checks
        obj_copy[f'__{value.name}'] = value

        for series_name in col_labels:
            dtype = get_merged_series_dtype({value.dtype, self.obj[series_name].dtype})
            new_expr = Expression.construct(
                base_expr,
                *[mask, obj_copy[f'__{value.name}'].astype(dtype), self.obj[series_name].astype(dtype)],
            )
            obj_copy[series_name] = obj_copy[series_name].copy_override(expression=new_expr)
            obj_copy[series_name] = obj_copy[series_name].copy_override_dtype(dtype)

        return obj_copy[self.obj.data_columns]

    def _set_item_by_slicing(
        self,
        index_labels: slice,
        col_labels: List[str],
        value: 'Series',
    ) -> 'DataFrame':
        """
        returns a new dataframe with replaced values based on provided slicing.
        steps to follow:
        1. Add the value as a series to the caller. This is a way to check if the value is actually supported
            by the caller, at the same time simplifies the final subquery.
        2. Get the sliced subset from the result of previous step.
        3. Add copy of index as a data column to the sliced dataframe, it is needed in further steps as it
            helps us identify if the row is part of the sliced subset.
        4. Merge dataframe from step 1 with result from previous step.
        5. Modify each series found in col_labels using the normal _set_item_by_labels. Rows to be modified
           are identified with the following condition:
             column_to_modify == column_to_modify_from_sliced AND index_from_sliced IS NOT NULL
        """
        obj_cp = self.obj.copy()
        obj_cp[f'__{value.name}'] = value
        obj_cp = obj_cp.copy_override(order_by=self.obj.order_by)

        index_name = self.obj.index_columns[0]
        sliced_df = obj_cp.loc[index_labels, col_labels]
        sliced_df[f'{index_name}__data_column'] = sliced_df.index[index_name].copy()
        merged = obj_cp.merge(
            sliced_df, how='left', on=self.obj.index_columns, suffixes=('', '__sliced')
        )
        for col in col_labels:
            # original series and sliced series should have same values
            # in case both original series and sliced series are NULL
            # we need to be sure that row actually comes from the sliced subset, therefore check
            # if index value is not null
            mask = (
                (merged[col] == merged[f'{col}__sliced']) & (merged[f'{index_name}__data_column'].notnull())
            )
            merged.loc[mask, col] = merged[f'__{value.name}']

        return merged[self.obj.data_columns].copy_override(order_by=self.obj.order_by)
