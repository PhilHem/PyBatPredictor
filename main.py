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


def get_voltage_column_list(df: DataFrame) -> List[str]:
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
    """Returns the number of columns in DataFrame that show cell voltage

    Args:
        df (DataFrame): DataFrame with "Aux_Voltage" columns.

    Returns:
        int: number of "Aux_Voltage" columns.
    """
    voltage_col_name_len = len(get_voltage_column_list(df))
    return voltage_col_name_len


def trim_to_cutoff_voltage(df: DataFrame, cutoff_voltage: float) -> DataFrame:
    """Trims a DataFrame up to a specific "Aux_Voltage". Useful for
    isolating a specific voltage range in a battey capacity test

    Args:
        df (DataFrame): battery test time series data
        cutoff_voltage (float): voltage past which the data should be
            trimmed

    Returns:
        DataFrame: Trimmed DataFrame
    """
    voltage_column_list = get_voltage_column_list(df)
    for col in voltage_column_list:
        df = df[df[col] >= 1.8]
    return df


def plot_cell_voltages(df: DataFrame) -> None:
    """Plots all the cell voltages from a given DataFrame
    containing battery time series data.

    Args:
        df (DataFrame): battery time series data
    """
    voltage_column_list = get_voltage_column_list(df)
    ax = df.plot(y=voltage_column_list[0], legend=True)  # type: ignore
    voltage_column_list = voltage_column_list[1::]
    for col in voltage_column_list:
        df.plot(y=col, ax=ax, legend=True, grid=True,  # type:ignore
                title="Cell Voltages", figsize=(10, 10))  # type:ignore
