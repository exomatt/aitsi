import pandas as pd


class CsvReader:

    @staticmethod
    def read_csv_from_file(path: str, column_is_int: bool = False) -> pd.DataFrame:
        if column_is_int:
            temporary_dataframe: pd.DataFrame = pd.read_csv(path, index_col=0)
            temporary_dataframe = temporary_dataframe.rename(int, axis='columns')
            return temporary_dataframe
        return pd.read_csv(path, index_col=0)
