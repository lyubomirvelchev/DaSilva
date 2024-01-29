import pandas as pd

# ignore all warnings
pd.options.mode.chained_assignment = None  # default='warn'

MAIN_TABLE_PATH = r'first_table.csv'
SECOND_TABLE_PATH = r'second_table.csv'
NSEM_TABLE_PATH = r'nsem.csv'
TSEM_TABLE_PATH = r'tsem.csv'


def read_csv_file(file_path):
    df = pd.read_csv(file_path)
    return df


a = read_csv_file(MAIN_TABLE_PATH)
b = read_csv_file(SECOND_TABLE_PATH)
c = read_csv_file(NSEM_TABLE_PATH)
d = read_csv_file(TSEM_TABLE_PATH)
e = 0