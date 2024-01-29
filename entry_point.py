import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QLineEdit, QLabel, QGridLayout)

FIRST_TABLE_PATH = r'first_table.csv'
SECOND_TABLE_PATH = r'second_table.csv'
FIRST_TABLE_INT_COLUMNS = ["IDEN", "PKOD", "EDUC", ]
SECOND_TABLE_INT_COLUMNS = ["PRIM", "IDEN", "PKOD", "EDUC", "COST", "FCOS", "FOTO", ]


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.df = pd.read_csv(FIRST_TABLE_PATH)
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()

        self.line_edits = []
        for i in range(self.df.shape[1]):
            row = i // 3
            col = i % 3

            label = QLabel(self.df.columns[i])
            line_edit = QLineEdit(self)

            grid.addWidget(label, row * 2, col)
            grid.addWidget(line_edit, row * 2 + 1, col)

            self.line_edits.append(line_edit)

        add_button = QPushButton('Add Row', self)
        add_button.clicked.connect(self.add_data)
        grid.addWidget(add_button, (self.df.shape[1] // 3) * 2 + 2, 0, 1, 3)

        widget = QWidget()
        widget.setLayout(grid)

        self.setCentralWidget(widget)

    def add_data(self):
        row_data = []
        for line_edit in self.line_edits:
            row_data.append(line_edit.text())

        self.df.loc[len(self.df)] = row_data
        self.df.to_csv('your_file.csv', index=False)  # Writing back to CSV
        self.clear_fields()

    def clear_fields(self):
        for line_edit in self.line_edits:
            line_edit.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
