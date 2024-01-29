import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QMessageBox, QLineEdit, QLabel, QGridLayout, QTableWidget, QTableWidgetItem,
                             QAbstractItemView, QHBoxLayout)

NUMBER_OF_COLUMNS = 4
FIRST_TABLE_PATH = r'first_table.csv'
SECOND_TABLE_PATH = r'second_table.csv'
FIRST_TABLE_INT_COLUMNS = ["IDEN", "PKOD", "EDUC"]
SECOND_TABLE_INT_COLUMNS = ["PRIM", "IDEN", "PKOD", "EDUC", "COST", "FCOS", "FOTO", ]


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.current_table = 1
        self.dfs = {1: pd.read_csv(FIRST_TABLE_PATH, na_values=''), 2: pd.read_csv(SECOND_TABLE_PATH, na_values='')}
        self.table_paths = {1: FIRST_TABLE_PATH, 2: SECOND_TABLE_PATH}
        self.last_row = -1

        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()

        self.toggle_button = QPushButton('Toggle Table', self)
        self.toggle_button.clicked.connect(self.toggle_table)

        self.grid = QGridLayout()
        vbox.addLayout(self.grid)

        hbox = QHBoxLayout()

        self.add_button = QPushButton('Create row', self)
        self.add_button.clicked.connect(self.add_data)
        hbox.addWidget(self.add_button)

        self.check_button = QPushButton('Read rows', self)
        self.check_button.clicked.connect(self.read_row)
        hbox.addWidget(self.check_button)

        self.update_button = QPushButton('Update Row', self)
        self.update_button.clicked.connect(self.update_row)
        hbox.addWidget(self.update_button)

        self.delete_button = QPushButton('Delete Row', self)
        self.delete_button.clicked.connect(self.delete_row)
        hbox.addWidget(self.delete_button)

        hbox.addWidget(self.toggle_button)

        vbox.addLayout(hbox)

        self.message_label = QLabel("Hello")
        vbox.addWidget(self.message_label)

        self.table_widget = QTableWidget()
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        vbox.addWidget(self.table_widget)

        widget = QWidget()
        widget.setLayout(vbox)

        self.setCentralWidget(widget)

        self.update_grid()

    def confirmation_popup(self, operation):
        msg = QMessageBox()
        msg.setWindowTitle("Confirmation")
        msg.setText(f"Are you sure you want to {operation}?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        return_value = msg.exec()
        if return_value == QMessageBox.Yes:
            return True
        else:
            return False

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
        self.current_table = 1 if self.current_table == 2 else 2
        self.update_grid()

    def add_data(self):
        print("add_data")
        row_data = []
        for line_edit in self.line_edits:
            row_data.append(line_edit.text())

        df = self.dfs[self.current_table]

        if self.current_table == 1:
            print(row_data)
            for i in range(len(row_data)):
                if df.columns[i] in FIRST_TABLE_INT_COLUMNS:
                    value = row_data[i]
                    print(value, type(value), i)
                    value = int(value)
                    print(value, type(value), i)

            iden = row_data[0]
            print(iden)
            # check if IDEN is already in the table
            if iden in df["IDEN"].values:
                self.message_label.setText("IDEN already exists")
                return

            df.loc[len(df)] = row_data
            df.to_csv(self.table_paths[self.current_table], index=False)

            self.last_row = len(df) - 1
            self.clear_fields()

        elif self.table == 2:
            iden = row_data[4]
            ...

    def update_row(self):
        if self.last_row < 0:
            return

        if self.confirmation_popup("update the row"):
            row_data = []
            for line_edit in self.line_edits:
                row_data.append(line_edit.text())

            df = self.dfs[self.current_table]
            df.loc[self.last_row] = row_data
            df.to_csv(self.table_paths[self.current_table], index=False)

            self.clear_fields()

    def delete_row(self):
        if self.last_row < 0:
            return

        if self.confirmation_popup("delete the row"):
            df = self.dfs[self.current_table]
            df = df.drop(self.last_row)
            df = df.reset_index(drop=True)  # Reset the index after dropping a row.
            df.to_csv(self.table_paths[self.current_table], index=False)

            self.dfs[self.current_table] = df  # Update the dataframe stored in memory

            self.last_row = -1  # Reset the last_row index as the row is now deleted
            self.clear_fields()

    def read_row(self):
        row_data = [line_edit.text() for line_edit in self.line_edits]
        df = self.dfs[self.current_table]
        print(row_data)

        mask = pd.Series([True] * len(df))
        for col, data in zip(df.columns, row_data):
            if data:
                mask &= (df[col] == data)

        print(mask)
        result = df[mask]
        print(result)
        if result.shape[0] == 0:
            self.message_label.setText("No rows found")
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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
