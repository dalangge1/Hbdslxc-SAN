from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc
from QEasyWidgets.Windows import *
from QEasyWidgets.Components import *

from windows.ui.UI_MainWindow import Ui_MainWindow
from windows.ui.UI_ChildWindow_VPR import Ui_ChildWindow_VPR
from windows.ui.UI_ChildWindow_ASR import Ui_ChildWindow_ASR
from windows.ui.UI_ChildWindow_DAT import Ui_ChildWindow_DAT
from windows.ui.UI_ChildWindow_DAT import Ui_ChildWindow_DAT
from windows.ui.UI_ChildWindow_TTS import Ui_ChildWindow_TTS

##############################################################################################################################

class Window_MainWindow(MainWindowBase):
    ui = Ui_MainWindow()

    def __init__(self, parent = None):
        super().__init__(parent, min_width = 1280, min_height = 720)

        self.ui.setupUi(self)

        self.setTitleBar(self.ui.TitleBar)

        self.setCentralWidget(self.ui.CentralWidget)

        self.langChanged.connect(lambda: self.ui.retranslateUi(self))

##############################################################################################################################

class Window_ChildWindow_VPR(ChildWindowBase):
    ui = Ui_ChildWindow_VPR()

    def __init__(self, parent = None):
        super().__init__(parent, min_width = 960, min_height = 540)

        self.ui.setupUi(self)

        self.setTitleBar(self.ui.TitleBar)


class Window_ChildWindow_ASR(ChildWindowBase):
    ui = Ui_ChildWindow_ASR()

    def __init__(self, parent = None):
        super().__init__(parent, min_width = 960, min_height = 540)

        self.ui.setupUi(self)

        self.setTitleBar(self.ui.TitleBar)


class Window_ChildWindow_DAT(ChildWindowBase):
    ui = Ui_ChildWindow_DAT()

    def __init__(self, parent = None):
        super().__init__(parent, min_width = 960, min_height = 540)

        self.ui.setupUi(self)

        self.setTitleBar(self.ui.TitleBar)


class Window_ChildWindow_TTS(ChildWindowBase):
    ui = Ui_ChildWindow_TTS()

    def __init__(self, parent = None):
        super().__init__(parent, min_width = 450, min_height = 300)

        self.ui.setupUi(self)

        self.setTitleBar(self.ui.TitleBar)

##############################################################################################################################

class MessageBox_Stacked(MessageBoxBase):
    '''
    '''
    def __init__(self, parent: QWidget = None):
        super().__init__(parent, min_width = 810, min_height = 480)

        self.layout().setContentsMargins(6, 12, 6, 12)
        self.layout().setSpacing(6)

        self.StackedWidget = QStackedWidget()

        self.ButtonP = QPushButton()
        self.ButtonP.clicked.connect(lambda: self.StackedWidget.setCurrentIndex(self.StackedWidget.currentIndex() - 1))
        self.ButtonP.setFixedWidth(33)
        self.ButtonP.setFixedHeight(66)
        QFunc.Function_SetRetainSizeWhenHidden(self.ButtonP)
        self.ButtonP.setStyleSheet(
            "QPushButton {"
            "   background-color: transparent;"
            "   padding: 12px;"
            "   border-image: url(:/Button_Icon/images/icons/LeftArrow.png);"
            "}"
            "QPushButton:hover {"
            "   background-color: rgba(210, 222, 234, 12);"
            "}"
        )
        self.ButtonP.setToolTip("Prev Page")

        self.ButtonN = QPushButton()
        self.ButtonN.clicked.connect(lambda: self.StackedWidget.setCurrentIndex(self.StackedWidget.currentIndex() + 1))
        self.ButtonN.setFixedWidth(33)
        self.ButtonN.setFixedHeight(66)
        QFunc.Function_SetRetainSizeWhenHidden(self.ButtonN)
        self.ButtonN.setStyleSheet(
            "QPushButton {"
            "   background-color: transparent;"
            "   padding: 12px;"
            "   border-image: url(:/Button_Icon/images/icons/RightArrow.png);"
            "}"
            "QPushButton:hover {"
            "   background-color: rgba(210, 222, 234, 12);"
            "}"
        )
        self.ButtonN.setToolTip("Next Page")

        Layout = QHBoxLayout()
        Layout.setAlignment(Qt.AlignCenter)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.setSpacing(self.layout().spacing())
        Layout.addWidget(self.ButtonP)
        Layout.addWidget(self.StackedWidget)
        Layout.addWidget(self.ButtonN)
        self.Layout.insertLayout(0, Layout)

    def SetContent(self, Images: list, Texts: list):
        QFunc.Function_SetNoContents(self.StackedWidget)

        for Index, Image in enumerate(QFunc.ToIterable(Images)):
            Label = LabelBase()
            QFunc.Function_SetText(Label, QFunc.SetRichText(QFunc.ToIterable(Texts)[Index], 'left', 9.9, 420))

            TextBrowser = QTextBrowser()
            TextBrowser.setStyleSheet(
                "QTextBrowser {"
                f"    background-image: url({QFunc.NormPath(Image, 'Posix')});"
                "    background-repeat: no-repeat;"
                "    background-position: center 0px;"
                "    padding: 0px;"
                "    border: none;"
                "    border-radius: 6px;"
                "}"
            ) if Image is not None else None

            SubLayout = QVBoxLayout()
            SubLayout.setAlignment(Qt.AlignCenter)
            SubLayout.setContentsMargins(0, 0, 0, 0)
            SubLayout.setSpacing(self.layout().spacing())
            SubLayout.addWidget(Label)
            SubLayout.addWidget(TextBrowser)

            Widget = QWidget()
            Widget.setLayout(SubLayout)
            self.StackedWidget.addWidget(Widget)
    
        self.StackedWidget.currentChanged.connect(lambda: self.ButtonP.setVisible(False) if self.StackedWidget.currentIndex() == 0 else self.ButtonP.setVisible(True))
        self.ButtonP.setVisible(False)
        self.StackedWidget.currentChanged.connect(lambda: self.ButtonN.setVisible(False) if self.StackedWidget.currentIndex() == self.StackedWidget.count() - 1 else self.ButtonN.setVisible(True))
        self.ButtonN.setVisible(True)

        self.StackedWidget.currentChanged.connect(lambda: self.setText(f'{self.StackedWidget.currentIndex() + 1} / {self.StackedWidget.count()}'))
        self.setText(f'1 / {self.StackedWidget.count()}')


class MessageBox_Buttons(MessageBoxBase):
    '''
    '''
    def __init__(self, parent: QWidget = None):
        super().__init__(parent, min_width = 240, min_height = 120)

        self.layout().setContentsMargins(6, 12, 6, 12)
        self.layout().setSpacing(6)

        self.Button1 = HollowButton()
        #self.Button1.setFixedHeight(33)

        self.Button2 = HollowButton()
        #self.Button2.setFixedHeight(33)

        Layout = QGridLayout()
        Layout.setAlignment(Qt.AlignCenter)
        Layout.setContentsMargins(21, 12, 21, 12)
        Layout.setSpacing(21)
        Layout.addWidget(self.Button1, 1, 0, 1, 2)
        Layout.addWidget(self.Button2, 2, 0, 1, 2)
        self.Layout.insertLayout(2, Layout)

##############################################################################################################################