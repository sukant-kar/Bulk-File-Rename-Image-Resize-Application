# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Window(object):
    def setupUi(self, Window):
        Window.setObjectName("Window")
        Window.resize(720, 480)
        # Snip...

    def retranslateUi(self, Window):
        _translate = QtCore.QCoreApplication.translate
        Window.setWindowTitle(_translate("Window", "RP Renamer"))
        # Snip...
        # -*- coding: utf-8 -*-
# rprename/__init__.py

"""This module provides the rprename package."""

__version__ = "0.1.0"
# -*- coding: utf-8 -*-
# rprename/views.py

"""This module provides the RP Renamer main window."""

from PyQt5.QtWidgets import QWidget

from .ui.window import Ui_Window

class Window(QWidget, Ui_Window):
    def __init__(self):
        super().__init__()
        self._setupUI()

    def _setupUI(self):
        self.setupUi(self)
        # rprename/views.py
# Snip...

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Window()
        self._setupUI()

    def _setupUI(self):
        self.ui.setupUi(self)
        # -*- coding: utf-8 -*-
# rprename/app.py

"""This module provides the RP Renamer application."""

import sys

from PyQt5.QtWidgets import QApplication

from .views import Window

def main():
    # Create the application
    app = QApplication(sys.argv)
    # Create and show the main window
    win = Window()
    win.show()
    # Run the event loop
    sys.exit(app.exec())
    #!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rprenamer.py

"""This module provides the RP Renamer entry-point script."""

from rprename.app import main

if __name__ == "__main__":
    main()
    # -*- coding: utf-8 -*-
# rprename/views.py

"""This module provides the RP Renamer main window."""

from collections import deque
from pathlib import Path

from PyQt5.QtWidgets import QFileDialog, QWidget

from .ui.window_ui import Ui_Window

FILTERS = ";;".join(
    (
        "PNG Files (*.png)",
        "JPEG Files (*.jpeg)",
        "JPG Files (*.jpg)",
        "GIF Files (*.gif)",
        "Text Files (*.txt)",
        "Python Files (*.py)",
    )
)

class Window(QWidget, Ui_Window):
    # Snip...
    # rprename/views.py
# Snip...

class Window(QWidget, Ui_Window):
    def __init__(self):
        super().__init__()
        self._files = deque()
        self._filesCount = len(self._files)
        self._setupUI()
        self._connectSignalsSlots()

    def _setupUI(self):
        self.setupUi(self)

    def _connectSignalsSlots(self):
        self.loadFilesButton.clicked.connect(self.loadFiles)

    def loadFiles(self):
        self.dstFileList.clear()
        if self.dirEdit.text():
            initDir = self.dirEdit.text()
        else:
            initDir = str(Path.home())
        files, filter = QFileDialog.getOpenFileNames(
            self, "Choose Files to Rename", initDir, filter=FILTERS
        )
        if len(files) > 0:
            fileExtension = filter[filter.index("*") : -1]
            self.extensionLabel.setText(fileExtension)
            srcDirName = str(Path(files[0]).parent)
            self.dirEdit.setText(srcDirName)
            for file in files:
                self._files.append(Path(file))
                self.srcFileList.addItem(file)
            self._filesCount = len(self._files)
            # -*- coding: utf-8 -*-
# rprename/rename.py

"""This module provides the Renamer class to rename multiple files."""

import time
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal

class Renamer(QObject):
    # Define custom signals
    progressed = pyqtSignal(int)
    renamedFile = pyqtSignal(Path)
    finished = pyqtSignal()

    def __init__(self, files, prefix):
        super().__init__()
        self._files = files
        self._prefix = prefix

    def renameFiles(self):
        for fileNumber, file in enumerate(self._files, 1):
            newFile = file.parent.joinpath(
                f"{self._prefix}{str(fileNumber)}{file.suffix}"
            )
            file.rename(newFile)
            time.sleep(0.1)  # Comment this line to rename files faster.
            self.progressed.emit(fileNumber)
            self.renamedFile.emit(newFile)
        self.progressed.emit(0)  # Reset the progress
        self.finished.emit()
        # rprename/views.py
# Snip...

class Window(QWidget, Ui_Window):
    # Snip...
    def _connectSignalsSlots(self):
        self.loadFilesButton.clicked.connect(self.loadFiles)
        self.renameFilesButton.clicked.connect(self.renameFiles)

    def loadFiles(self):
        # Snip..

    def renameFiles(self):
        self._runRenamerThread()

    def _runRenamerThread(self):
        prefix = self.prefixEdit.text()
        self._thread = QThread()
        self._renamer = Renamer(
            files=tuple(self._files),
            prefix=prefix,
        )
        self._renamer.moveToThread(self._thread)
        # Rename
        self._thread.started.connect(self._renamer.renameFiles)
        # Update state
        self._renamer.renamedFile.connect(self._updateStateWhenFileRenamed)
        # Clean up
        self._renamer.finished.connect(self._thread.quit)
        self._renamer.finished.connect(self._renamer.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        # Run the thread
        self._thread.start()

    def _updateStateWhenFileRenamed(self, newFile):
        self._files.popleft()
        self.srcFileList.takeItem(0)
        self.dstFileList.addItem(str(newFile))
        # rprename/views.py
# Snip...

class Window(QWidget, Ui_Window):
    # Snip...
    def _runRenamerThread(self):
        # Update state
        self._renamer.renamedFile.connect(self._updateStateWhenFileRenamed)
        self._renamer.progressed.connect(self._updateProgressBar)
        # Snip...

    def _updateStateWhenFileRenamed(self, newFile):
        # Snip...

    def _updateProgressBar(self, fileNumber):
        progressPercent = int(fileNumber / self._filesCount * 100)
        self.progressBar.setValue(progressPercent)
        # rprename/views.py
# Snip...

class Window(QWidget, Ui_Window):
    # Snip...
    def _setupUI(self):
        self.setupUi(self)
        self._updateStateWhenNoFiles()

    def _updateStateWhenNoFiles(self):
        self._filesCount = len(self._files)
        self.loadFilesButton.setEnabled(True)
        self.loadFilesButton.setFocus(True)
        self.renameFilesButton.setEnabled(False)
        self.prefixEdit.clear()
        self.prefixEdit.setEnabled(False)

   # Snip...
   def _runRenamerThread(self):
        # Snip...
        self._renamer.progressed.connect(self._updateProgressBar)
        self._renamer.finished.connect(self._updateStateWhenNoFiles)
        # Snip...
