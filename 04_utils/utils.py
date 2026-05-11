import pandas as pd
import polars as pl
import numpy as np

def continuity_fix(ts_df, min_date, max_date, freq, uid_col, date_col = 'ds', y_col = 'y', fill_value = 0.):
    """
    This function checks a dataframe containing a single time-series to see if there's any missing
    dates between the min and max dates according to the frequency of the time-series. If any are found
    then then they are filled with the specified fill_value.

    Input:
    -ts_df (polars DataFrame): Dataframe containing a single time-series
    -min_date (datetime): Earliest date point of your time series
    -max_date (datetime): Latest date point of your time series
    -freq (str): Frequency of your time series, valid values in here 
                (https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases)
    -uid_col (str): Name of the unique_id column in ts_df
    -date_col (str): Name of the date column in ts_df
    -y_col (str): Name of the target column in ts_df
    -fill_value (int/float): Value to be input in any found holes.

    Output:
    """
    # Save original column structure of ts_df for consistency of the output.
    column_order = ts_df.columns + ['hole']

    # Generate the date range index to check for missing values. For this project we are going to manually set
    # the type to date, for other projects you might need to adjust the type according to your needs.
    date_idx_df = pl.from_pandas(pd.DataFrame({date_col:pd.date_range(start=min_date, end=max_date, freq=freq)}))\
                    .with_columns(pl.col(date_col).dt.date())

    # Perform a left join of ts_df on date_idx_df to look for null values.
    check_df = date_idx_df.join(ts_df, on= date_col, how= 'left')

    # Mark any found holes and fill the null values in uid_col and y_col
    check_df = check_df.with_columns(pl.when(pl.col(y_col).is_null())
                                     .then(pl.lit(1))
                                     .otherwise(pl.lit(0))
                                     .alias('hole'))\
                       .with_columns(pl.col(uid_col).fill_null(strategy='forward'))\
                       .with_columns(pl.col(y_col).fill_null(value=fill_value))
    
    return check_df[column_order]
    