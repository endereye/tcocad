from PyQt5 import QtWidgets

import qtui.data_ui


class Data(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.__ui = qtui.data_ui.Ui_data()
        self.__ui.setupUi(self)

        self.__ui.btn_cat_load.clicked.connect(lambda: self.__load('cat'))
        self.__ui.btn_dog_load.clicked.connect(lambda: self.__load('dog'))

        self.cat_path = None
        self.dog_path = None

        self.__ui.buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.__ui.buttons.accepted.connect(self.accept)
        self.__ui.buttons.rejected.connect(self.reject)

    def __load(self, category: str):
        assert category == 'cat' or category == 'dog'

        _path = QtWidgets.QFileDialog.getExistingDirectory(caption='选择数据路径')
        if _path != '':
            if category == 'cat':
                self.cat_path = _path
                self.__ui.txt_cat_path.setText(_path)
            else:
                self.dog_path = _path
                self.__ui.txt_dog_path.setText(_path)

        if self.cat_path is not None and self.dog_path is not None:
            self.__ui.buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(True)
