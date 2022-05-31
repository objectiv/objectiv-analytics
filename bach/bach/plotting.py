"""
Copyright 2022 Objectiv B.V.
"""
from typing import TYPE_CHECKING, Optional, Union, List, cast

import numpy
import pandas

from bach import SeriesAbstractNumeric, SeriesNumericInterval
from sql_models.util import is_bigquery

if TYPE_CHECKING:
    from bach.dataframe import DataFrame


class PlotHandler(object):
    """
    Preprocesses data needed for plotting and uses Pandas ``DataFrame.plot``.
    """
    df: 'DataFrame'

    def __init__(self, df: 'DataFrame') -> None:
        self.df = df

    def hist(
        self,
        by: Optional[Union[str, List[str]]] = None,
        bins: int = 10,
        **kwargs,
    ):
        """
        Draw a histogram representation of DataFrame's numeric columns.

        :param by: series to group data by. Currently, not supported
        :param bins: number of equal-width histogram bins.
        :param kwargs: additional keyword arguments supported by Pandas ``DataFrame.plot``

        :returns: a histogram plot (matplotlib.AxesSubplot)
        """

        if by:
            raise NotImplementedError('by is currently not supported.')

        from bach.series.series_numeric import SeriesAbstractNumeric
        numeric_columns = [s.name for s in self.df.data.values() if isinstance(s, SeriesAbstractNumeric)]

        if not numeric_columns:
            raise ValueError(
                "hist method requires numerical columns, nothing to plot."
            )

        freq_df = self._calculate_hist_frequencies(bins, numeric_columns)

        # prepare results for Pandas hist compatibility
        freq_df['lower_edge'] = cast(SeriesNumericInterval, freq_df['range']).lower
        freq_pdf = freq_df.to_pandas()
        freq_pdf = freq_pdf.pivot_table(
            columns='column_label',
            values='frequency',
            index='lower_edge',
            dropna=False,
            fill_value=0,
        )
        freq_pdf = freq_pdf.reset_index(level=-1, drop=False)

        # get lower bounds per range and add the last upper bound (last_bin + bin_width)
        bin_edges = freq_pdf['lower_edge'].to_numpy()
        bin_width = numpy.ediff1d(bin_edges)[-1]
        bin_edges = numpy.append(bin_edges, bin_edges[-1] + bin_width)

        # use calculated frequencies as weights, since Pandas will try to recalculate frequencies
        hist_data = pandas.DataFrame(data={col: freq_pdf['lower_edge'] for col in numeric_columns})
        weights = freq_pdf[numeric_columns].to_numpy()
        return hist_data.plot.hist(bins=bin_edges, weights=weights, **kwargs)

    def _calculate_hist_frequencies(self, bins: int, numeric_columns: List[str]) -> 'DataFrame':
        """
        Helper for creating histogram's value frequencies per bin.

        returns a DataFrame containing the following data columns:
            * column_label (names of numeric columns)
            * range (range of each bin)
            * frequency (number of values the range contains for the column label)
        """
        from bach.operations.cut import CutOperation

        df = self.df[numeric_columns].reset_index(drop=True)
        # stack the df in order to have all numeric values in a single series
        label_values_series = cast(SeriesAbstractNumeric, df.stack())
        bins_per_col_df = CutOperation(
            label_values_series,
            bins=bins,
            method='bach',
            include_empty_bins=True,
            ignore_index=False,
        )().to_frame().reset_index(drop=False)

        # create frequency distribution dataframe per label (numeric column)
        # labels are contained in __stacked_index series (result from DataFrame.stack)
        frequencies = bins_per_col_df.reset_index().groupby(by=['__stacked_index', 'range']).count()
        frequencies = frequencies.reset_index(drop=False)

        # rename columns to meaningful names
        frequencies = frequencies.rename(
            columns={'__stacked_index': 'column_label', '__stacked_count': 'frequency'},
        )
        frequencies['column_label'] = frequencies['column_label'].fillna('empty_bins')
        return frequencies[['column_label', 'frequency', 'range']]
