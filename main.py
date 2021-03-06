from pandas import DataFrame, Series
from typing import List
import numpy as np


def isolate_timeinterval(
        df: DataFrame,
        start_date: str,
        stop_date: str) -> DataFrame:
    """Isolates a time interval within a time series and returns a 
    new pandas DataFrame that represents the time interval.

    For this to work, the DataFrame must have an index column in with the DateTime type.
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
    step index as a column. This only works if there is a column that 
    represents the Step Index within the dataframe.


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
        step_index: int,
        step_col_name: str = "Step_Index") -> DataFrame:
    """Isolates a time interval within time series data,
    as well as a specific step index. For this to work, the DataFrame needs an index column that has the DateTime type, as well as a column that represents the step index

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


def calculate_testtime(df: DataFrame) -> Series:  # type: ignore
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
        df = df[df[col] >= cutoff_voltage]
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
                title="Cell Voltages", figsize=(10, 9), ylim=(1.8, 2.1))  # type:ignore


def get_smallest_voltage_cell(df: DataFrame) -> str:
    """Returns the voltage cell column name with the lowest
    voltage at the end of the time series data.

    Args:
        df (DataFrame): DataFrame with battery time series data

    Returns:
        str: cell column name with lowest voltage
    """
    voltage_column_list = get_voltage_column_list(df)
    smallest_voltage_cell = voltage_column_list[0]
    for cell in voltage_column_list:
        if df[cell][-1] < df[smallest_voltage_cell][-1]:
            smallest_voltage_cell = cell
    return smallest_voltage_cell


def get_SOC_reference(df: DataFrame) -> DataFrame:
    """Returns a dataframe that isolates the voltage of the first cell
    that reaches the cutoff voltage within a capacity test and maps a
    corresponding SOC-Value to each voltage measurement.
    This can later be used a lookup table other cells to determine the
    last SOC value before ending the test.

    Args:
        df (DataFrame): Dataframe that represents a capacity
        test with multiple cells.

    Returns:
        DataFrame: Dataframe that shows the SOC of each cell in
        the stack at the end of the capacity test.
    """

    newdf = DataFrame()  # Generate new dataframe as the basis for new lookup table
    newdf["Test_Time(s)"] = calculate_testtime(df)  # type: ignore -- generate time index for new dataframe
    smallest_cell = get_smallest_voltage_cell(df)  # isolate the cell that first reaches cutoff voltage
    newdf[f"{smallest_cell}(REF)"] = df[smallest_cell]  # generating column that is named with respective cell name and voltage
    newdf["SOC_Ref"] = np.linspace(100, 0, len(df), endpoint=True).round(3)  # type: ignore -- generate SOC column
    newdf = newdf.set_index("Test_Time(s)")  # type: ignore
    return newdf


def soc_from_lut(refdf: DataFrame, voltage: float) -> float:
    """Calculates the SOC in percent at a given voltage by comparison
    with a soc lookup table.

    Args:
        refdf (DataFrame): dataframe containing a SOC lookup
            table (use get_SOC_reference())
        voltage (float): given voltage to be compared

    Returns:
        float: SOC value derived from comparison with lookup table
    """
    return refdf.iloc[np.argmin(abs(refdf[refdf.columns[0]]-voltage))][1]  # type: ignore


def get_final_SOC(df: DataFrame) -> DataFrame:
    """Returns a DataFrame that represents the SOC of each cell of a cell stack
    at the end of a capacity test. This requires a capacity test dataframe with 

    Args:
        df (DataFrame): dataframe containing a capacity test.

    Returns:
        DataFrame: dataframe representing the SOC at the end of capacity test.
    """

    refdf = get_SOC_reference(df)                               # * generate lookup table for SOC

    smallest_cap = get_smallest_cap_cell(df)                    # * isolate the cell that first reaches cutoff voltage

    output_df = DataFrame()                                     # * generate new dataframe for final output dataframe

    soc_list = []                                               # * generate list for SOC values in percent
    capacity_list = []                                          # * generate list for capacity values in mAh
    voltage_cols = get_voltage_column_list(df)                  # * generate list of cell voltage columns

    for col in voltage_cols:                                    # * iterate over cell voltage columns
        soc = soc_from_lut(refdf, df[col][-1])  # type: ignore  # * calculate SOC value for each cell voltage column
        cap = smallest_cap + smallest_cap*soc/100               # * calculate capacity value for each cell voltage column
        soc_list.append(soc)  # type: ignore                    # * append SOC value to SOC value list
        capacity_list.append(cap)  # type:ignore                # * append capacity value to capacity value list

    output_df["SOC (%)"] = soc_list                             # * generate SOC column in output dataframe
    output_df["Capacity (Ah)"] = capacity_list                  # * generate capacity column in output dataframe

    # * change the name of the voltage columns to the respective cell names
    for idx, cell in enumerate(voltage_cols):
        voltage_cols[idx] = cell.replace("Aux_Voltage_", "Cell ")
        voltage_cols[idx] = voltage_cols[idx].replace("(V)", "")

    output_df["Cell ID"] = voltage_cols                         # * generate cell ID column in output dataframe
    output_df = output_df.set_index("Cell ID")  # type: ignore  # * set index to cell ID column
    return output_df


def get_smallest_cap_cell(df: DataFrame) -> float:
    """Calculates the capacity of the cell that reaches the cutoff voltage first
    by trapezoidal integration of the current.

    The other cells in the test deliver at least that amount of current, but their
    capacity has to be derived from the SOC at the end of the test.

    Args:
        df (DataFrame): Dataframe containing a capacity test of at least one cell.

    Returns:
        float: Capacity value in Ah of that cell. 
    """
    cap: float = -np.trapz(df["Current(A)"], df["Test_Time(s)"])/3600  # type:ignore
    return cap


def get_capacity_list(df_list: List[DataFrame]) -> DataFrame:
    return_df = DataFrame()
    for idx, df in enumerate(df_list):
        soc_df = get_final_SOC(df)
        #return_df[f"SOC_{idx+1} (%)"] = soc_df["SOC (%)"]
        return_df[f"Capacity_{idx+1} (Ah)"] = soc_df["Capacity (Ah)"]

    return return_df


def get_soh_list(df_list: List[DataFrame]) -> DataFrame:
    capacity_df = get_capacity_list(df_list)
