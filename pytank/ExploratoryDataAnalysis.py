import pandas as pd
from pytank.utilities.utilities import days_in_month
from pytank.utilities.utilities import interp_from_dates, interp_dates_row
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

class exploratory_data_analysis:
    def __init__(self, production_file, pressure_file, pvt_file):
        self.df_prod = pd.read_csv(production_file)
        self.df_press = pd.read_csv(pressure_file)
        self.df_pvt = pd.read_csv(pvt_file)

    def production_per_well(self):
        date_col = "START_DATETIME"
        self.df_prod[date_col] = pd.to_datetime(self.df_prod['START_DATETIME'])
        #  Define data frame columns
        # Input
        oil_cum_col = "OIL_CUM"
        water_cum_col = "WATER_CUM"
        gas_cum_col = "GAS_CUM"
        well_name_col = "ITEM_NAME"
        tank_name_col = "Tank"
        # Output
        cal_day_col = "cal_day"
        oil_rate_col = "oil_rate"
        water_rate_col = "water_rate"
        gas_rate_col = "gas_rate"
        liquid_rate_col = "liquid_rate"
        liquid_cum_col = "liquid_cum"
        #  Calculate Rates
        # Calculate the calendar days
        self.df_prod[cal_day_col] = self.df_prod[date_col].map(lambda date: days_in_month(date))

        # Define the input and output columns
        cols_input = [oil_cum_col, water_cum_col, gas_cum_col]
        cols_output = [oil_rate_col, water_rate_col, gas_rate_col]

        # Calculate the rates using the differences between cumulatives
        df_input = self.df_prod[[well_name_col, *cols_input]]
        self.df_prod[cols_output] = (df_input.groupby(well_name_col).diff().fillna(df_input)
                                     .div(self.df_prod[cal_day_col], axis=0))

        # Calculate liquid production rate and cumulative
        self.df_prod[liquid_rate_col] = self.df_prod[oil_rate_col] + self.df_prod[water_rate_col]
        self.df_prod[liquid_cum_col] = self.df_prod[oil_cum_col] + self.df_prod[water_cum_col]

        # Plot oil production from all the wells
        fig_1, (ax_11, ax_12) = plt.subplots(2, 1, sharex=True)

        (self.df_prod.pivot_table(oil_rate_col, date_col, well_name_col)
         .plot(colormap="Greens_r", lw=1, ax=ax_11, legend=False))
        (self.df_prod.pivot_table(water_rate_col, date_col, well_name_col)
         .plot(colormap="Blues_r", lw=1, ax=ax_12, legend=False))

        fig_1.suptitle("Production Rate per Well")
        ax_11.set_ylabel("Oil Rate (STB/D)")
        ax_12.set_ylabel("Water Rate (STB/D)")
        ax_12.set_xlabel("Date")
        plt.show()

    def production_per_tank(self):
        date_col = "START_DATETIME"
        self.df_prod[date_col] = pd.to_datetime(self.df_prod['START_DATETIME'])
        #  Define data frame columns
        # Input
        oil_cum_col = "OIL_CUM"
        water_cum_col = "WATER_CUM"
        gas_cum_col = "GAS_CUM"
        well_name_col = "ITEM_NAME"
        tank_name_col = "Tank"
        # Output
        cal_day_col = "cal_day"
        oil_rate_col = "oil_rate"
        water_rate_col = "water_rate"
        gas_rate_col = "gas_rate"
        liquid_rate_col = "liquid_rate"
        liquid_cum_col = "liquid_cum"

        # Define the input and output columns
        cols_input = [oil_cum_col, water_cum_col, gas_cum_col]
        cols_output = [oil_rate_col, water_rate_col, gas_rate_col]

        # Calculate the rates using the differences between cumulatives
        df_input = self.df_prod[[well_name_col, *cols_input]]
        self.df_prod[cols_output] = (df_input.groupby(well_name_col).diff().fillna(df_input)
                                     .div(self.df_prod[cal_day_col], axis=0))

        #  Plot the Oil and Liquid Production per tank
        fig_2, (ax_21, ax_22) = plt.subplots(2, 1, sharex=True)

        df_prod_tank = (self.df_prod[[date_col, tank_name_col, *cols_output]]
                        .groupby([date_col, tank_name_col])
                        .sum().reset_index())

        df_prod_tank.pivot_table(oil_rate_col, date_col, tank_name_col).plot(lw=1, ax=ax_21)
        df_prod_tank.pivot_table(water_rate_col, date_col, tank_name_col).plot(lw=1, ax=ax_22,
                                                                               legend=False)

        ax_21.legend(fontsize=6)
        fig_2.suptitle("Production Rate per Tank")
        ax_21.set_ylabel("Oil Rate (STB/D)")
        ax_22.set_ylabel("Water Rate (STB/D)")
        ax_22.set_xlabel("Date")
        plt.show()

    def pressure_per_date(self):
        formatter = ticker.EngFormatter()
        date_col = "START_DATETIME"
        self.df_prod[date_col] = pd.to_datetime(self.df_prod['START_DATETIME'])
        #  Define data frame columns
        # Input
        oil_cum_col = "OIL_CUM"
        water_cum_col = "WATER_CUM"
        gas_cum_col = "GAS_CUM"
        well_name_col = "ITEM_NAME"
        tank_name_col = "Tank"
        # Output
        cal_day_col = "cal_day"
        oil_rate_col = "oil_rate"
        water_rate_col = "water_rate"
        gas_rate_col = "gas_rate"
        liquid_rate_col = "liquid_rate"
        liquid_cum_col = "liquid_cum"

        #  Housekeeping of pressure data frame
        # Rename column names for pressure data frame to use the same as the production one
        self.df_press.rename(columns={"WELLBORE": well_name_col, "DATE": date_col}, inplace=True)
        # Make sure the date column is o datetime object
        self.df_press[date_col] = pd.to_datetime(self.df_press[date_col])
        # Specify important columns
        press_col = "PRESSURE_DATUM"
        press_type_col = "TEST_TYPE"

        #  Calculate liquid cumulative in the whole field
        # For that, first calculate the liquid volume per well in each month
        liquid_vol_col = "liquid_vol"
        self.df_prod[liquid_vol_col] = self.df_prod[liquid_rate_col] * self.df_prod[cal_day_col]
        # Then, group by dates and sum the monthly volumes, then accumulate them
        df_field = self.df_prod.groupby(date_col)[liquid_vol_col].sum().cumsum().reset_index()
        # The resulting column is the liquid cumulative, so rename it
        df_field.rename(columns={liquid_vol_col: liquid_cum_col}, inplace=True)

        #  Prepare pressure data for plotting
        self.df_press[liquid_cum_col] = interp_from_dates(self.df_press[date_col],
                                                          df_field[date_col],
                                                          df_field[liquid_cum_col])

        # Plot all pressure data colouring by type, vs date and vs Liq. Cum.
        fig_3, (ax_31, ax_32) = plt.subplots(2, 1)

        self.df_press.pivot_table(press_col, date_col, press_type_col).plot(style="o", ax=ax_31, ms=2)
        self.df_press.pivot_table(press_col, liquid_cum_col, press_type_col).plot(style="o", ax=ax_32,
                                                                                  ms=2, legend=False)
        # Set first axes
        ax_31.set_title("Pressure data vs. Date")
        ax_31.set_xlabel("Date")
        ax_31.set_ylabel("Pressure (psia)")
        ax_31.tick_params(axis="x", labelsize=8)
        ax_31.legend(fontsize=8)
        ax_31.yaxis.set_major_formatter(formatter)
        # Set second axes
        ax_32.set_title("Pressure data vs. Liquid Cumulative")
        ax_32.set_xlabel("Liquid Cumulative (STB)")
        ax_32.set_ylabel("Pressure (psia)")
        ax_32.xaxis.set_major_formatter(formatter)
        ax_32.yaxis.set_major_formatter(formatter)

        plt.tight_layout()
        plt.show()

    def liquid_acumulative_per_tank(self):
        formatter = ticker.EngFormatter()
        date_col = "START_DATETIME"
        self.df_prod[date_col] = pd.to_datetime(self.df_prod['START_DATETIME'])
        #  Define data frame columns
        # Input
        oil_cum_col = "OIL_CUM"
        water_cum_col = "WATER_CUM"
        gas_cum_col = "GAS_CUM"
        well_name_col = "ITEM_NAME"
        tank_name_col = "Tank"
        # Output
        cal_day_col = "cal_day"
        oil_rate_col = "oil_rate"
        water_rate_col = "water_rate"
        gas_rate_col = "gas_rate"
        liquid_rate_col = "liquid_rate"
        liquid_cum_col = "liquid_cum"
        liquid_vol_col = "liquid_vol"

        # Calculate liquid cumulative per tank in the pressure data frame
        cols_group = [date_col, tank_name_col, liquid_vol_col]

        df_tank: pd.DataFrame = (
            self.df_prod[cols_group]
            .groupby(cols_group[:-1]).sum()  # to get monthly volumes per tank
            .groupby(tank_name_col).cumsum()  # to get cumulative vols per tank
            .reset_index())

        # The resulting column is the liquid cumulative, so rename it
        df_tank.rename(columns={liquid_vol_col: liquid_cum_col}, inplace=True)
        # Plot cumulatives to check
        ax_4 = (df_tank.pivot_table(liquid_cum_col, date_col, tank_name_col)
                .fillna(method="ffill")
                .plot())

        ax_4.set_title("Liquid Cumulatives per Tank")
        ax_4.set_ylabel("Liquid Cum (STB/D)")
        ax_4.set_xlabel("Date")
        ax_4.yaxis.set_major_formatter(formatter)
        plt.show()

    def pressure_per_tank(self):
        formatter = ticker.EngFormatter()
        date_col = "START_DATETIME"
        self.df_prod[date_col] = pd.to_datetime(self.df_prod['START_DATETIME'])
        #  Define data frame columns
        # Input
        oil_cum_col = "OIL_CUM"
        water_cum_col = "WATER_CUM"
        gas_cum_col = "GAS_CUM"
        well_name_col = "ITEM_NAME"
        tank_name_col = "Tank"
        # Output
        cal_day_col = "cal_day"
        oil_rate_col = "oil_rate"
        water_rate_col = "water_rate"
        gas_rate_col = "gas_rate"
        liquid_rate_col = "liquid_rate"
        liquid_cum_col = "liquid_cum"
        liquid_vol_col = "liquid_vol"

        # Calculate liquid cumulative per tank in the pressure data frame
        cols_group = [date_col, tank_name_col, liquid_vol_col]

        df_tank: pd.DataFrame = (
            self.df_prod[cols_group]
            .groupby(cols_group[:-1]).sum()  # to get monthly volumes per tank
            .groupby(tank_name_col).cumsum()  # to get cumulative vols per tank
            .reset_index())

        # The resulting column is the liquid cumulative, so rename it
        df_tank.rename(columns={liquid_vol_col: liquid_cum_col}, inplace=True)

        # Get liquid cumulative interpolation per tank into the pressure data frame
        liquid_cum_col_per_tank = liquid_cum_col + "_tank"
        self.df_press[liquid_cum_col_per_tank] = (
            self.df_press.apply(lambda g: interp_dates_row(g, date_col, df_tank, date_col,
                                                           liquid_cum_col, tank_name_col,
                                                           tank_name_col), axis=1)
        )

        # Plot pressure per tank vs. date and vs. liquid cumulative
        fig_5, (ax_51, ax_52) = plt.subplots(2, 1)

        # Specify important columns
        press_col = "PRESSURE_DATUM"
        press_type_col = "TEST_TYPE"

        self.df_press.pivot_table(press_col, date_col, tank_name_col).plot(ax=ax_51, style="o")
        self.df_press.pivot_table(press_col,
                                  liquid_cum_col_per_tank, tank_name_col).plot(ax=ax_52,
                                                                               style="o",
                                                                               legend=False)

        # Set first axes
        ax_51.set_title("Pressure data vs. Date")
        ax_51.set_xlabel("Date")
        ax_51.set_ylabel("Pressure (psia)")
        ax_51.tick_params(axis="x", labelsize=8)
        ax_51.legend(fontsize=8)
        ax_51.yaxis.set_major_formatter(formatter)
        # Set second axes
        ax_52.set_title("Pressure data vs. Liquid Cumulative")
        ax_52.set_xlabel("Liquid Cumulative (STB)")
        ax_52.set_ylabel("Pressure (psia)")
        ax_52.xaxis.set_major_formatter(formatter)
        ax_52.yaxis.set_major_formatter(formatter)

        plt.tight_layout()
        plt.show()



production_file = "../tests/data_for_tests/full_example_1/production.csv"
pressure_file = "../tests/data_for_tests/full_example_1/pressures.csv"
pvt_file = "../tests/data_for_tests/full_example_1/pvt.csv"
grafica = exploratory_data_analysis(production_file,pressure_file,pvt_file).production_per_tank()
print(grafica)