from main import *
import pandas as pd


df1: pd.DataFrame = pd.read_csv(
    "/Users/philipphematty/Downloads/Philipp/Messdaten/BMS/Gel_noBMS_Cycle_01_Summer_01.CSV", parse_dates=True)
df1["Date_Time"] = pd.to_datetime(df1["Date_Time"], utc=True)

df2 = pd.read_csv(
    "/Users/philipphematty/Downloads/Philipp/Messdaten/BMS/Gel_noBMS_Cycle_01_Winter_Channel_3_Wb_1.CSV", parse_dates=True)
df2["Date_Time"] = pd.to_datetime(df2["Date_Time"], utc=True)

df3 = pd.read_csv(
    "/Users/philipphematty/Downloads/Philipp/Messdaten/BMS/Gel_noBMS_Cycle_02_Summer_Channel_3_Wb_1.CSV", parse_dates=True)
df3["Date_Time"] = pd.to_datetime(df3["Date_Time"], utc=True)
dfx = df1.append(df2).append(df3).sort_values(by="Date_Time")
dfx = dfx.set_index(["Date_Time"])

dfx2 = dfx

df1 = isolate_step_index_in_timeinterval(dfx, "2021-01-22", "2021-01-28", 13)
trim_to_cutoff_voltage(df1, 2)
