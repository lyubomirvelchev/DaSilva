import datetime
import time
import re
from dbfread import DBF
import pandas as pd
import datetime
from simpledbf import Dbf5

# ignore all warnings
pd.options.mode.chained_assignment = None  # default='warn'

FILE_PATH_MAIN = r"C:\Users\user\Desktop\YOUMUSTORDERYOURSOFTWARE\SemiCopy.dbf"
FILE_PATH_NSEM = r"C:\Users\user\Desktop\YOUMUSTORDERYOURSOFTWARE\nsem.dbf"
FILE_PATH_TSEM = r"C:\Users\user\Desktop\YOUMUSTORDERYOURSOFTWARE\tsem.dbf"
ascii_dict = {
    9474: 'у',
    9488: 'я',
    9508: 'ф',
    9553: 'ъ',
    9557: 'ш',
    9558: 'ч',
    9563: 'ю',
    9565: 'ь',
    9569: 'х',
    9570: 'ц',
    9571: 'щ',
    9617: 'р',
    9618: 'с',
    9619: 'т',
}
second_table_columns = ['NAME', 'FATH', 'FAMI', 'IDEN', 'PKOD', 'EDUC', 'KODS', 'COST', 'FCOS', 'DFCO', 'DCOS', 'FOTO',
                        'LE11',
                        'LE12', 'LE13', 'LE21', 'LE22', 'LE23']
drop_columns_first_table = ['COST', 'FCOS', 'DFCO', 'DCOS', 'FOTO', 'LEFI', 'LE11', 'LE12', 'LE13', 'LE21', 'LE22',
                            'LE23']


def read_dbf_file(file_path):
    start_time = time.time()
    with DBF(file_path, encoding='cp866') as table:
        df = pd.DataFrame(iter(table))
        first_table = df[df['MARK'] == '0']
        first_table = first_table.drop(drop_columns_first_table, axis=1)
        # add new column to first table
        first_table['MAIL'] = ''
        first_table['MAL2'] = ''
        second_table = df[df['MARK'] == '1']
        second_table = second_table[second_table_columns]
        for column in first_table.select_dtypes(include=['object']).columns:
            first_table[column] = first_table[column].apply(
                lambda x: x if x is None else x if type(x) == datetime.date else x.translate(ascii_dict))
        for column in second_table.select_dtypes(include=['object']).columns:
            second_table[column] = second_table[column].apply(
                lambda x: x if x is None else x if type(x) == datetime.date else x.translate(ascii_dict))
        # Iterate through each value in the DataFrame
        for index, row in first_table.iterrows():
            for column in first_table.columns:
                value = row[column]
                # if there is no number in HTEL or DTEL columns, remove the value from the old position and place it in PROF

                # Apply email identifier regex
                email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9._-]+\.[A-Za-z]{2,}\b', str(value))
                # email_matches_1 = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', str(value))
                # email_matches_2 = re.findall(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(value))
                if email_matches:
                    # add emial to first table on MAIL column. If there is already email in this column, add it to MAL2
                    if first_table.at[index, 'MAIL'] == '':
                        first_table.at[index, 'MAIL'] = email_matches[0]
                    else:
                        first_table.at[index, 'MAL2'] = email_matches[0]
                    # remove the value from the old position
                    first_table.at[index, column] = str(value).replace(email_matches[0], '')
        for index, row in first_table.iterrows():
            for column in first_table.columns:
                value = row[column]
                if column == 'HTEL' or column == 'DTEL':
                    if not re.search(r'\d', str(value)) and value != '':
                        if value == '.':
                            first_table.at[index, column] = ''
                        elif first_table.at[index, 'PROF'] == '':
                            first_table.at[index, 'PROF'] = value
                            first_table.at[index, column] = ''
                            a = 0
                # if there is @ symbol in PROF, HTEL, DTEL  column, remove it
                if index == 16521 and column == 'PROF':
                    first_table.at[index, column] = ''  # dirty fix
                if column == 'PROF' or column == 'HTEL' or column == 'DTEL':
                    if '@' in str(value):
                        first_table.at[index, column] = ''

        first_table = first_table.drop('MARK', axis=1)

        # set IDEN column as first column
        cols = list(first_table.columns)
        cols.insert(0, cols.pop(cols.index('IDEN')))
        first_table = first_table.loc[:, cols]

        # add new column to second table with values from one to length of the table as first column
        second_table.insert(0, 'PRIM', range(1, len(second_table) + 1))
        # set PRIM column as first column
        cols = list(second_table.columns)
        cols.insert(0, cols.pop(cols.index('PRIM')))
        second_table = second_table.loc[:, cols]

        # set second table DCOS column as string. change nan to empty string
        second_table['DCOS'] = second_table['DCOS'].astype(str)
        second_table['DCOS'] = second_table['DCOS'].replace('nan', '')

        # sort first table by IDEN column
        first_table = first_table.sort_values(by=['IDEN'])

        for column in first_table.columns:
            uniq = []
            for valu in first_table[column]:
                if type(valu) not in uniq:
                    uniq.append(type(valu))
            print(column, ": ", uniq)
        print('=============================')
        for column in second_table.columns:
            uniq = []
            for valu in second_table[column]:
                if type(valu) not in uniq:
                    uniq.append(type(valu))
            print(column, ": ", uniq)
        # first_table.to_csv('first_table.csv', index=False)
        # second_table.to_csv('second_table.csv', index=False)


        # print(result_df)
        # GOOD ONE - get unique value occurrences per column
        # for column in first_table.columns:
        #     print(first_table[column].replace('', 'hui').value_counts(dropna=False))
        # print('=============================')
        # for column in second_table.columns:
        #     print(second_table[column].replace('', 'hui').value_counts(dropna=False))
        # print(first_table['NAME'].replace('', 'hui').value_counts(dropna=False))

        # for record in table:
        #     count += 1
        #     if count > 7530 and count < 7777:
        #         for field, value in record.items():
        #             if field == "PROF":
        #                 # print([ord(i) for i in value])
        #                 value = value.translate(ascii_dict)
        #                 print(f"{field}: {value}")
        #
        #         # print('Count: ', count)
        #         # print("=====================================")


read_dbf_file(FILE_PATH_MAIN)


# open nsem.dbf and tsem.dbf and save to csv

with DBF(FILE_PATH_NSEM, encoding='cp866') as table:
    df = pd.DataFrame(iter(table))
    for column in df.select_dtypes(include=['object']).columns:
        df[column] = df[column].apply(lambda x: x if x is None else x if type(x) == datetime.date else x.translate(ascii_dict))
    df.to_csv('nsem.csv', index=False)

with DBF(FILE_PATH_TSEM, encoding='cp866') as table:
    df = pd.DataFrame(iter(table))
    for column in df.select_dtypes(include=['object']).columns:
        df[column] = df[column].apply(lambda x: x if x is None else x if type(x) == datetime.date else x.translate(ascii_dict))
    df.to_csv('tsem.csv', index=False)
