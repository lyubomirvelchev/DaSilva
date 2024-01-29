import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QLineEdit, QLabel, QGridLayout, QTableWidget, QTableWidgetItem, QAbstractItemView,
                             QHBoxLayout, QMessageBox)

NUMBER_OF_COLUMNS = 4
FIRST_TABLE_PATH = r'first_table.csv'
SECOND_TABLE_PATH = r'second_table.csv'
FIRST_TABLE_NUM_COLUMNS = ["IDEN", "PKOD", "EDUC"]
SECOND_TABLE_NUM_COLUMNS = ["PRIM", "IDEN", "PKOD", "EDUC", "COST", "FCOS", "FOTO"]


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.dfs = {FIRST_TABLE_PATH: pd.read_csv(FIRST_TABLE_PATH), SECOND_TABLE_PATH: pd.read_csv(SECOND_TABLE_PATH)}
        self.current_table = FIRST_TABLE_PATH
        self.last_row = -1

        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()

        self.grid = QGridLayout()
        vbox.addLayout(self.grid)
        self.message_label = QLabel("Таблица 1")
        vbox.addWidget(self.message_label)

        hbox = QHBoxLayout()

        self.add_button = QPushButton('Добави ред', self)
        self.add_button.clicked.connect(self.add_data)
        hbox.addWidget(self.add_button)

        self.update_button = QPushButton('Промени ред', self)
        self.update_button.clicked.connect(self.update_row)
        hbox.addWidget(self.update_button)

        self.delete_button = QPushButton('Изтрий ред', self)
        self.delete_button.clicked.connect(self.delete_row)
        hbox.addWidget(self.delete_button)

        self.check_button = QPushButton('Търсене', self)
        self.check_button.clicked.connect(self.read_data)
        hbox.addWidget(self.check_button)

        self.clear_button = QPushButton('Изчисти', self)
        self.clear_button.clicked.connect(self.clear_fields)
        hbox.addWidget(self.clear_button)

        self.toggle_button = QPushButton('Смени таблица', self)
        self.toggle_button.clicked.connect(self.toggle_table)
        hbox.addWidget(self.toggle_button)

        vbox.addLayout(hbox)

        self.table_widget = QTableWidget()
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        vbox.addWidget(self.table_widget)

        widget = QWidget()
        widget.setLayout(vbox)

        self.setCentralWidget(widget)

        self.update_grid()

    def get_fields_data(self):
        row_data = []
        for line_edit in self.line_edits:
            row_data.append(line_edit.text())
        return row_data

    def ask_user(self, question):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText(question)
        msgBox.setWindowTitle("Confirmation")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            print('Yes clicked')
            return True
        else:
            print('No clicked')
            return False

    def delete_row(self):
        row_data = self.get_fields_data()
        if not row_data:
            self.message_label.setText("Моля, въведете IDEN на реда, който искате да изтриете.")
            return

        iden_num = int(row_data[0])

        if not self.ask_user(f"Наистина ли искате да изтриете ред: {iden_num}?"):
            return

        df = self.dfs[self.current_table]
        if self.current_table == FIRST_TABLE_PATH:
            df['IDEN'] = df['IDEN'].astype(int)
            df = df[df['IDEN'] != iden_num]
        elif self.current_table == SECOND_TABLE_PATH:
            df['PRIM'] = df['PRIM'].astype(int)
            df = df[df['PRIM'] != iden_num]
        df.to_csv(self.current_table, index=False)

        self.dfs[self.current_table] = df
        self.clear_fields()
        self.message_label.setText(f"Успешно изтрихте ред: {iden_num}")

    def transform_df_columns(self, df):
        df = df.astype(str)
        for i in range(len(df)):
            for j in range(len(df.columns)):
                val = df.iloc[i, j]
                if val.isdigit() and df.columns[j] not in ["IDEN", "PRIM"]:
                    df.iloc[i, j] = str(float(val))
        df['IDEN'] = df['IDEN'].astype(int)
        if 'PRIM' in df.columns:
            df['PRIM'] = df['PRIM'].astype(int)
        return df

    def update_grid(self):
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        self.line_edits = []
        df = self.dfs[self.current_table]
        for i in range(df.shape[1]):
            row = i // NUMBER_OF_COLUMNS
            col = i % NUMBER_OF_COLUMNS

            label = QLabel(df.columns[i])
            line_edit = QLineEdit(self)

            self.grid.addWidget(label, row * 2, col)
            self.grid.addWidget(line_edit, row * 2 + 1, col)

            self.line_edits.append(line_edit)

    def toggle_table(self):
        self.current_table = FIRST_TABLE_PATH if self.current_table == SECOND_TABLE_PATH else SECOND_TABLE_PATH
        if self.current_table == FIRST_TABLE_PATH:
            self.message_label.setText("Таблица 1")
        else:
            self.message_label.setText("Таблица 2")
        self.update_grid()

    def add_data(self):
        row_data = self.get_fields_data()
        if not row_data:
            return

        try:
            primary_key = int(row_data[0])
        except ValueError:
            self.message_label.setText("Primary key must be integer")
            return

        df = self.dfs[self.current_table]
        df = self.transform_df_columns(df)
        if self.current_table == FIRST_TABLE_PATH:
            if primary_key in df["IDEN"].values:
                self.message_label.setText(f"Primary key {primary_key} already exists")
                return
        elif self.current_table == SECOND_TABLE_PATH:
            if primary_key in df["PRIM"].values:
                self.message_label.setText(f"Primary key {primary_key} already exists")
                return
            try:
                foreign_key = int(row_data[4])
            except ValueError:
                self.message_label.setText("Foreign key must be integer")
                return
            first_df = self.dfs[FIRST_TABLE_PATH]
            first_df = self.transform_df_columns(first_df)
            if foreign_key not in first_df['IDEN'].values:
                self.message_label.setText("Foreign key does not exist")
                return
            row_data[1] = first_df.loc[first_df['IDEN'] == foreign_key, 'NAME'].iloc[0]
            row_data[2] = first_df.loc[first_df['IDEN'] == foreign_key, 'FATH'].iloc[0]
            row_data[3] = first_df.loc[first_df['IDEN'] == foreign_key, 'FAMI'].iloc[0]

        df = self.dfs[self.current_table]
        df.loc[len(df)] = row_data
        df.to_csv(self.current_table, index=False)

        self.message_label.setText("Успешно добавен ред")
        self.last_row = len(df) - 1
        self.clear_fields()

    def find_row_by_id(self, iden_num):
        df = self.dfs[self.current_table]
        if self.current_table == FIRST_TABLE_PATH:
            df['IDEN'] = df['IDEN'].astype(int)
            match = df[df['IDEN'] == iden_num]
        elif self.current_table == SECOND_TABLE_PATH:
            df['PRIM'] = df['PRIM'].astype(int)
            match = df[df['PRIM'] == iden_num]

        if not match.empty:
            return match.index[0]  # Return the index of the matched row
        else:
            return None

    def update_row(self):
        row_data = self.get_fields_data()
        if not row_data:
            return

        try:
            primary_key = int(row_data[0])
        except ValueError:
            self.message_label.setText("Primary key must be integer")
            return

        row_index = self.find_row_by_id(primary_key)
        if row_index is None:
            self.message_label.setText(f"No row found with primary key: {primary_key}")
            return

        if self.ask_user(f"Сигурни ли сте, че искате да обновите ред {primary_key}?") == QMessageBox.No:
            return

        df = self.dfs[self.current_table]
        df.loc[row_index] = row_data
        df.to_csv(self.current_table, index=False)

        self.message_label.setText("Успешно обновен ред")


    def populate_line_edits(self, data):
        for line_edit, data in zip(self.line_edits, data):
            line_edit.setText(str(data))

    def read_data(self):
        row_data = self.get_fields_data()
        if not row_data:
            return

        df = self.dfs[self.current_table]
        df = self.transform_df_columns(df)

        match_values = {}
        for i in range(len(row_data)):
            if i == 0 or (i == 4 and self.current_table == SECOND_TABLE_PATH):
                try:
                    row_data[i] = int(row_data[i]) if row_data[i] != '' else ''
                    if row_data[i] != '':
                        match_values[df.columns[i]] = row_data[i]
                except ValueError:
                    self.message_label.setText("IDEN and PRIM must be integer")
                    return
            elif row_data[i]:
                value = row_data[i]
                if value.isdigit():
                    value = str(float(value))
                match_values[df.columns[i]] = value
        print(match_values)
        result = df
        for column, value in match_values.items():
            if type(value) is not str:
                result = result[result[column] == value]
            else:
                result = result[result[column].apply(lambda x: x.casefold()) == value.casefold()]

        if result.empty:
            self.message_label.setText("Няма резултати")
            self.clear_table()
            return

        self.table_widget.setRowCount(result.shape[0])
        self.table_widget.setColumnCount(result.shape[1])
        self.table_widget.setHorizontalHeaderLabels(result.columns.tolist())

        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(result.iat[i, j])))

        self.populate_line_edits(result.iloc[-1])

    def old_check_row(self):
        row_data = self.get_fields_data()
        if not row_data:
            return
        df = self.dfs[self.current_table]

        mask = pd.Series([True] * len(df))
        for col, data in zip(df.columns, row_data):
            if data:
                mask &= (df[col] == data)

        result = df[mask]
        if result.empty:
            self.message_label.setText("Няма резултати")
            self.clear_table()
            return

        self.table_widget.setRowCount(result.shape[0])
        self.table_widget.setColumnCount(result.shape[1])
        self.table_widget.setHorizontalHeaderLabels(result.columns.tolist())

        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(result.iat[i, j])))

    def clear_fields(self):
        for line_edit in self.line_edits:
            line_edit.clear()

    def clear_table(self):
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
