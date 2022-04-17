from pandas import DataFrame, Series


def isolate_timeinterval(
        df: DataFrame,
        start_date: str,
        stop_date: str) -> DataFrame:
    """Isolates a time interval within a time series

    Args:
        df (DataFrame): time series that contains the interval
        start_date (str): start date for interval
        stop_date (str): stop date for interval

    Returns:
        DataFrame: Isolated time interval
    """
    return df[start_date:stop_date]


def isolate_step_index(
        df: DataFrame,
        step_index: int,
        col_name: str = "Step_Index") -> DataFrame:
    """Isolates a time series within a dataframe that has a certain
    step index as a column.


    Args:
        df (DataFrame): DataFrame with time series data,
            containing a "Step_Index" column.
        step_index (int): Step Index Number

    Returns:
        DataFrame: Dataframe with only the data for a specific step index.
    """
    return df[df[col_name] == step_index]


def isolate_step_index_in_timeinterval(
        df: DataFrame,
        start_date: str,
        stop_date: str,
        step_index: int) -> DataFrame:
    """Isolates a time interval within time series data,
    as well as a specific step index

    Args:
        df (DataFrame): DataFrame to be trimmed
        start_date (str): starting date for interval
        stop_date (str): stopping date for interval
        step_index (int): step index for interval

    Returns:
        DataFrame: DataFrame that only contains a specific
        step index within a time interval.
    """
    df_temp = isolate_timeinterval(df, start_date, stop_date)
    df_temp = isolate_step_index(df_temp, step_index)
    return df_temp


def calculate_testtime(df: DataFrame) -> Series[float]:
    """Returns a series that represents the test time in seconds, starting at
    zero. This is useful when an isolated time interval has a starting time
    other than zero. The test time is returned as a series that can be used
    to overwrite an existing time series.

    Args:
        df (DataFrame): DataFrame with a test time that starts from a
        different value than zero

    Returns:
        Series[float]: Series that represents the test time in seconds.
    """
    return df["Test_Time(s)"] - df["Test_Time(s)"][0]  # type: ignore


def isolate_voltage_columns(df: DataFrame) -> list[str]:
    """Returns a list of the names of the columns containing cell voltages.

    Args:
        df (DataFrame): DataFrame with "Aux_Voltage" columns

    Returns:
        list[str]: List of "Aux_Voltage"-Columns
    """
    col_names: list[str] = list(df.columns)
    cell_voltage_list = [name for name in col_names if "Aux_Voltage_" in name]
    return cell_voltage_list


def get_number_voltage_columns(df: DataFrame) -> int:
    voltage_col_name_len = len(isolate_voltage_columns(df))
    return voltage_col_name_len
