# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QHeaderView, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QTableView, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(419, 480)
        self.actionExport_setting_file = QAction(MainWindow)
        self.actionExport_setting_file.setObjectName(u"actionExport_setting_file")
        self.actionImport_setting_file = QAction(MainWindow)
        self.actionImport_setting_file.setObjectName(u"actionImport_setting_file")
        self.manual_action = QAction(MainWindow)
        self.manual_action.setObjectName(u"manual_action")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.match_button = QPushButton(self.centralwidget)
        self.match_button.setObjectName(u"match_button")
        self.match_button.setMinimumSize(QSize(0, 50))

        self.verticalLayout.addWidget(self.match_button)

        self.add_button = QPushButton(self.centralwidget)
        self.add_button.setObjectName(u"add_button")

        self.verticalLayout.addWidget(self.add_button)

        self.match_info_table_view = QTableView(self.centralwidget)
        self.match_info_table_view.setObjectName(u"match_info_table_view")
        self.match_info_table_view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.match_info_table_view.horizontalHeader().setCascadingSectionResizes(False)

        self.verticalLayout.addWidget(self.match_info_table_view)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 419, 22))
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuHelp.addAction(self.manual_action)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionExport_setting_file.setText(QCoreApplication.translate("MainWindow", u"Export setting file", None))
        self.actionImport_setting_file.setText(QCoreApplication.translate("MainWindow", u"Import setting file", None))
        self.manual_action.setText(QCoreApplication.translate("MainWindow", u"Manual", None))
        self.match_button.setText(QCoreApplication.translate("MainWindow", u"Match", None))
        self.add_button.setText(QCoreApplication.translate("MainWindow", u"Add FK and Joint", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

