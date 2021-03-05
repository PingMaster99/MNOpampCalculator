# encoding: utf-8
"""
    DatabaseConnection.py
    Author: Dario Marroquin 18269   (dariomarroquin)
    Author: Pablo Ruiz 18259        (PingMaster99)
    Version 1.0
    Updated March 4, 2021

    Connection to the Excel database
"""
import pandas as pd
import openpyxl


class Data:
    """
        Class for the database connection
    """
    def __init__(self):
        self.data = self.fetch_data()

    def fetch_data(self, filename='opamp.xlsx'):
        """
        Gets the initial data from the Excel
        :param filename: name of the file
        :return: vin, vout coordinates
        """
        data = pd.read_excel(filename, engine="openpyxl")
        return [list(a) for a in zip(data["Vin"].tolist(), data["Vout"].tolist())], data[['R']].dropna()["R"].tolist()

    def set_data(self, filename):
        """
        Sets new data on the database
        :param filename: name of the file
        """
        data = pd.read_excel(filename, engine="openpyxl")
        self.data = [list(a) for a in zip(data["Vin"].tolist(), data["Vout"].tolist())], data[['R']].dropna()["R"].tolist()

    def get_data(self):
        """
        Returns the data contained in the database
        :return: data
        """
        return self.data


