import joblib
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets

import core.core
import qtui.data_lg
import qtui.main_ui


def _pil_to_qt(img):
    if img.mode == 'RGB':
        _r, _g, _b = img.split()
        img = Image.merge('RGB', (_b, _g, _r))
    if img.mode == 'RGBA':
        _r, _g, _b, _a = img.split()
        img = Image.merge('RGBA', (_a, _b, _g, _r))
    img = img.convert('RGBA')
    img = QtGui.QImage(img.tobytes('raw', 'RGBA'), img.size[0], img.size[1], QtGui.QImage.Format.Format_ARGB32)
    return QtGui.QPixmap.fromImage(img)


class Worker(QtCore.QThread):
    update = QtCore.pyqtSignal(object)
    finish = QtCore.pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()

        self.__func = func
        self.__args = args, kwargs

    def run(self) -> None:
        _result = self.__func(*self.__args[0], **self.__args[1], cb_update=lambda _: self.update.emit(_))
        self.finish.emit(_result)


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.__ui = qtui.main_ui.Ui_main()
        self.__ui.setupUi(self)

        self.__ui.action_train_new.triggered.connect(self._train_new)
        self.__ui.action_train_old.triggered.connect(self._train_old)

        self.__ui.action_predict.triggered.connect(self._predict)
        self.__ui.action_measure.triggered.connect(self._measure)

        self.__model = None
        self.__slave = None

    def resizeEvent(self, _) -> None:
        if self.__ui.view_original.scene() is not None:
            # noinspection PyUnresolvedReferences
            self.__ui.view_original.fitInView(self.__ui.view_original.scene().sceneRect(), QtCore.Qt.KeepAspectRatio)
        if self.__ui.view_features.scene() is not None:
            # noinspection PyUnresolvedReferences
            self.__ui.view_features.fitInView(self.__ui.view_features.scene().sceneRect(), QtCore.Qt.KeepAspectRatio)

    def _set_model_loaded(self, model):
        self.__model = model
        self.__ui.action_predict.setEnabled(True)
        self.__ui.action_measure.setEnabled(True)
        self.__ui.status.setValue(0)
        self.__ui.status.setFormat('就绪')

    def _train_new(self):
        _win = qtui.data_lg.Data()
        _win.exec_()

        if _win.result() == QtWidgets.QDialog.DialogCode.Accepted:
            def _finish(mod):
                _path, _ = QtWidgets.QFileDialog.getSaveFileName(caption='选择保存路径')
                if _path != '':
                    joblib.dump(mod, _path)
                self._set_model_loaded(mod)

            self.__slave = Worker(core.core.train, _win.cat_path, _win.dog_path)
            self.__slave.update.connect(self._update_progress)
            self.__slave.finish.connect(_finish)
            self.__slave.start()

    def _train_old(self):
        _path = QtWidgets.QFileDialog.getOpenFileName(caption='加载预训练数据')[0]
        if _path != '':
            self._set_model_loaded(joblib.load(_path))

    def _predict(self):
        _path = QtWidgets.QFileDialog.getOpenFileName(caption='选择图片')[0]
        if _path != '':
            _original, _features, _result = core.core.predict(self.__model, _path)

            self.__ui.result.setText('分类结果：' + ('猫' if _result < 0 else '狗'))

            _original_scene = QtWidgets.QGraphicsScene()
            _features_scene = QtWidgets.QGraphicsScene()

            _original_scene.addPixmap(_pil_to_qt(_original))
            _features_scene.addPixmap(_pil_to_qt(_features))

            self.__ui.view_original.setScene(_original_scene)
            self.__ui.view_features.setScene(_features_scene)
            self.resizeEvent(None)

    def _measure(self):
        _win = qtui.data_lg.Data()
        _win.exec_()

        if _win.result() == QtWidgets.QDialog.DialogCode.Accepted:
            def _finish(ret):
                _cat_acc, _cat_tot, _dog_acc, _dog_tot = ret
                self._set_model_loaded(self.__model)
                self.__ui.result.setText(
                    '对猫的准确率：%d/%d（%d%%）；对狗的准确率：%d/%d（%d%%）；总准确率：%d/%d（%d%%）' % (
                        _cat_acc,
                        _cat_tot,
                        int(_cat_acc / _cat_tot * 100),
                        _dog_acc,
                        _dog_tot,
                        int(_dog_acc / _dog_tot * 100),
                        _cat_acc + _dog_acc,
                        _cat_tot + _dog_tot,
                        int((_cat_acc + _dog_acc) / (_cat_tot + _dog_tot) * 100)
                    )
                )

            self.__slave = Worker(core.core.measure, self.__model, _win.cat_path, _win.dog_path)
            self.__slave.update.connect(self._update_progress)
            self.__slave.finish.connect(_finish)
            self.__slave.start()

    def _update_progress(self, obj):
        if 'fmt' in obj:
            self.__ui.status.setFormat(obj['fmt'])
        if 'max' in obj:
            self.__ui.status.setMaximum(obj['max'])
        if 'cur' in obj:
            self.__ui.status.setValue(obj['cur'])
