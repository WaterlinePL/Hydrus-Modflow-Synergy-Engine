
import csv
from collections import defaultdict


def read_weather_csv(filepath: str):
    """
    Reads the data from a SWAT weather data .csv file. Returns the data as a dict.

    :param filepath: the path to the file we want to read from
    :return: a dictionary of {str: list}, a mapping of column names to lists of values in said columns
    """

    data = defaultdict(list)
    file = open(filepath)
    reader = csv.DictReader(file)

    for line in reader:
        for column, value in line.items():

            # a None pops up among the keys for some reason, ignore it
            if column is None:
                continue

            # for everything except date cast the numeric string to a true float
            if column != "Date":
                value = float(value)

            data[column].append(value)

    return data


def adapt_data(data: dict, hydrus_dist_unit: str):
    """
    Adapts the raw weather file data for use with hydrus - changes wind speed from m/s to km/day,
    humidity from fractions to percentages (0-100) and scales daily rainfall to the appropriate unit

    :param data: the data we want to adapt
    :param hydrus_dist_unit: the unit of distance used in the hydrus model we'll be modifying - "m", "cm" or "mm"
    :return: the modified data
    """
    #                   to  min  hr   day  km
    data["Wind"] = [speed * 60 * 60 * 24 / 1000 for speed in data["Wind"]]

    data["Relative Humidity"] = [value * 100 for value in data["Relative Humidity"]]

    if hydrus_dist_unit == "m":
        data["Precipitation"] = [value/1000 for value in data["Precipitation"]]
    elif hydrus_dist_unit == "cm":
        data["Precipitation"] = [value/10 for value in data["Precipitation"]]
    elif hydrus_dist_unit == "mm":
        pass

    return data

