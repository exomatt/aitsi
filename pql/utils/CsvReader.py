import pandas as pd


class CsvReader:

    @staticmethod
    def read_csv_from_file(path: str) -> pd.DataFrame:
        return pd.read_csv(path, index_col=0)
