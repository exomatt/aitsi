import pandas as pd


class CsvBuilder:

    @staticmethod
    def save_table_to_csv_file(data_frame: pd.DataFrame, path: str):
        data_frame.to_csv(path_or_buf=path)
