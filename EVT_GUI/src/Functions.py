import os
import platform
from typing import Union, Optional
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread, QPoint
from PySide6.QtCore import QCoreApplication as QCA
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox
from QEasyWidgets import QFunctions as QFunc
from QEasyWidgets.Components import *

from components.Components import *
from windows.Windows import *

##############################################################################################################################

# Where to store custom signals
class CustomSignals_Functions(QObject):
    '''
    Set up signals for functions
    '''
    # Run task
    Signal_ExecuteTask = Signal(tuple)

    # Monitor task
    Signal_TaskStatus = Signal(str, str)

    # Force exit
    Signal_ForceQuit = Signal()


    Signal_UpdateMessage = Signal(str)

    Signal_IsUpdateSucceeded = Signal(bool, str)

    Signal_ReadyToUpdate = Signal(str)


FunctionSignals = CustomSignals_Functions()

##############################################################################################################################

def Function_ScrollToWidget(
    Trigger: QWidget,
    TargetWidget: QWidget,
    ScrollArea: Optional[QScrollArea] = None,
    #Alignment: str = 'Top'
):
    '''
    '''
    if ScrollArea is None:
        ScrollArea = QFunc.Function_FindParentUI(TargetWidget, QScrollArea)

    def ScrollToWidget():
        TargetRect = TargetWidget.mapToGlobal(QPoint(0, 0))
        TargetYPos = TargetRect.y() - ScrollArea.widget().mapToGlobal(QPoint(0, 0)).y()

        ScrollArea.verticalScrollBar().setValue(TargetYPos)

    if isinstance(Trigger, QTreeWidgetItem):
        def TreeWidgetEvent(Item, Column):
            ScrollToWidget() if Item == Trigger else None
        Trigger.treeWidget().itemClicked.connect(TreeWidgetEvent)

    if isinstance(Trigger, QAbstractButton):
        Trigger.clicked.connect(ScrollToWidget)


def Function_AddToTreeWidget(
    Widget: QWidget,
    TreeWidget: TreeWidgetBase,
    RootItemText: str,
    ChildItemText: Optional[str] = None,
    ScrollArea: Optional[QScrollArea] = None
):
    '''
    '''
    RootItemTexts = TreeWidget.rootItemTexts()
    if RootItemText in RootItemTexts:
        RootItem = TreeWidget.topLevelItem(RootItemTexts.index(RootItemText))
    else:
        RootItem = QTreeWidgetItem(TreeWidget)
        RootItem.setText(0, RootItemText)
        RootItemTextFont = QFont()
        RootItemTextFont.setPixelSize(15)
        RootItem.setFont(0, RootItemTextFont)
    RootItem.setExpanded(True) if not RootItem.isExpanded() else None

    ChildItemTexts = TreeWidget.childItemTexts(RootItem)
    if ChildItemText is None:
        ChildItem = None
    elif ChildItemText in ChildItemTexts:
        ChildItem = RootItem.child(ChildItemTexts.index(ChildItemText))
    else:
        ChildItem = QTreeWidgetItem(RootItem)
        ChildItem.setText(0, ChildItemText)
        ChildItemTextFont = QFont()
        ChildItemTextFont.setPixelSize(12)
        ChildItem.setFont(0, ChildItemTextFont)

    Function_ScrollToWidget(
        Trigger = ChildItem if ChildItem is not None else RootItem,
        TargetWidget = Widget,
        ScrollArea = ScrollArea
    )


def Function_SetChildWidgetsVisibility(
    Container: QWidget,
    ChildWidgets: list[Optional[QWidget]],
    SetVisible: bool,
    AdjustContainer: bool = True
):
    '''
    Function to set the visibility of child-widgets
    '''
    ChildWidgets = [ChildWidget for ChildWidget in ChildWidgets if ChildWidget is not None]
    for ChildWidget in ChildWidgets:
        ChildWidget.setVisible(SetVisible)
    if AdjustContainer:
        CurrentHeight = Container.height()
        #Container.updateGeometry()
        AdjustedHeight = Container.minimumSizeHint().height()
        Function_AnimateFrame(
            Frame = Container,
            MinHeight = CurrentHeight if SetVisible else AdjustedHeight,
            MaxHeight = AdjustedHeight if SetVisible else CurrentHeight,
            Mode = 'Extend' if SetVisible else 'Reduce'
        )


def Function_ConfigureCheckBox(
    CheckBox: QCheckBox,
    CheckedText: Optional[str] = None,
    CheckedEvents: list = [],
    UncheckedText: Optional[str] = None,
    UncheckedEvents: list = [],
    TakeEffect: bool = False
):
    '''
    Function to configure checkbox
    '''
    if CheckedText is not None:
        CheckedEvents.append(lambda: CheckBox.setText(CheckedText))
    if UncheckedText is not None:
        UncheckedEvents.append(lambda: CheckBox.setText(UncheckedText))

    CheckBox.toggled.connect(
        lambda IsChecked: QFunc.RunEvents(CheckedEvents if IsChecked else UncheckedEvents)
    )

    QFunc.RunEvents(CheckedEvents) if TakeEffect and CheckBox.isChecked() else None
    QFunc.RunEvents(UncheckedEvents) if TakeEffect and not CheckBox.isChecked() else None


def Function_SetURL(
    Button: QAbstractButton,
    URL: Union[str, QWidget, list],
    ButtonTooltip: str = "Open",
    CreateIfNotExist: bool = False
):
    '''
    Function to open URL (through button)
    '''
    Button.clicked.connect(
        lambda: QFunc.Function_OpenURL([(Function_GetParam(URL) if isinstance(URL, QWidget) else URL) for URL in QFunc.ToIterable(URL)], CreateIfNotExist)
    )
    Button.setToolTipDuration(-1)
    Button.setToolTip(ButtonTooltip)

##############################################################################################################################

def Function_GetParam(
    UI: QObject
):
    '''
    Function to get the param of UI
    '''
    if isinstance(UI, (QLineEdit, QTextEdit, QPlainTextEdit)):
        return QFunc.Function_GetText(UI)
    if isinstance(UI, QComboBox):
        return UI.currentText()
    if isinstance(UI, (QAbstractSpinBox, QSlider, Frame_RangeSetting)):
        return UI.value()
    if isinstance(UI, (QCheckBox, QRadioButton)):
        return UI.isChecked()

    if isinstance(UI, Table_EditAudioSpeaker):
        return UI.GetValue()


def Function_SetParam(
    UI: QObject,
    Param: Optional[str]
):
    '''
    Function to set the param of UI
    '''
    if isinstance(UI, (QLineEdit, QTextEdit)):
        UI.setText(Param)
    if isinstance(UI, QPlainTextEdit):
        UI.setPlainText(Param)
    if isinstance(UI, QComboBox):
        UI.setCurrentText(Param)
    if isinstance(UI, (QAbstractSpinBox, QSlider, Frame_RangeSetting)):
        UI.setValue(Param)
    if isinstance(UI, (QCheckBox, QRadioButton)):
        UI.setChecked(Param)

    if isinstance(UI, Table_EditAudioSpeaker):
        UI.SetValue(Param)


def Function_ParamsSynchronizer(
    Trigger: Union[QObject, list],
    FromTo: dict = {},
    Times: Union[int, float] = 1,
    Connection: str = "Connect"
):
    '''
    Function to synchronize params (ParamsFrom.value * Times = ParamsTo.value)
    '''
    @Slot()
    def ParamsSynchronizer():
        for UI_Get, UI_Set in FromTo.items():
            Param_Get = Function_GetParam(UI_Get)
            Param_Get = Param_Get * Times if isinstance(Param_Get, (int, float, complex)) else Param_Get
            for UI_Set in QFunc.ToIterable(UI_Set):
                Function_SetParam(UI_Set, Param_Get)

    TriggerList = QFunc.ToIterable(Trigger)

    for Trigger in TriggerList:
        if isinstance(Trigger, QAbstractButton):
            Trigger.clicked.connect(ParamsSynchronizer) if Connection == "Connect" else Trigger.clicked.disconnect(ParamsSynchronizer)
        if isinstance(Trigger, QAbstractSlider):
            Trigger.sliderMoved.connect(ParamsSynchronizer) if Connection == "Connect" else Trigger.sliderMoved.disconnect(ParamsSynchronizer)
        if isinstance(Trigger, QAbstractSpinBox):
            Trigger.valueChanged.connect(ParamsSynchronizer) if Connection == "Connect" else Trigger.valueChanged.disconnect(ParamsSynchronizer)
        if isinstance(Trigger, (QLineEdit)):
            Trigger.textChanged.connect(ParamsSynchronizer) if Connection == "Connect" else Trigger.textChanged.disconnect(ParamsSynchronizer)


def Function_ParamsChecker(
    ParamsFrom: list = [],
    EmptyAllowed: list = []
):
    '''
    Function to return handled params
    '''
    Params = []

    for UI in ParamsFrom:
        Param = Function_GetParam(UI) if isinstance(UI, QWidget) else UI
        if isinstance(Param, str):
            if Param.strip() == "None" or Param.strip() == "":
                if UI in QFunc.ToIterable(EmptyAllowed):
                    Param = None
                else:
                    MessageBoxBase.pop(
                        MessageType = QMessageBox.Warning,
                        WindowTitle = "Warning",
                        Text = "Empty param detected!\n检测到参数空缺！"
                    )
                    return "Abort"
            else:
                '''
                if "，" in Param or "," in Param:
                    Param = re.split(
                        pattern = '[，,]',
                        string = Param,
                        maxsplit = 0
                    )
                '''
        if isinstance(Param, dict):
            if "None" in list(Param.keys()&Param.values()) or "" in list(Param.keys()&Param.values()):
                if UI in QFunc.ToIterable(EmptyAllowed):
                    Param = None
                else:
                    MessageBoxBase.pop(
                        MessageType = QMessageBox.Warning,
                        WindowTitle = "Warning",
                        Text = "Empty param detected!\n检测到参数空缺！"
                    )
                    return "Abort"
            else:
                pass
        else:
            pass
        Params.append(Param)

    Args = tuple(Params)#if Params != [] else None

    return Args

##############################################################################################################################

def Function_AnimateStackedWidget(
    StackedWidget: QStackedWidget,
    Target: Union[int, QWidget] = 0,
    Duration: int = 99
):
    '''
    Function to animate stackedwidget
    '''
    OriginalWidget = StackedWidget.currentWidget()
    OriginalGeometry = OriginalWidget.geometry()

    if isinstance(Target, int):
        TargetIndex = Target
    if isinstance(Target, QWidget):
        TargetIndex = StackedWidget.indexOf(Target)

    WidgetAnimation = QFunc.Function_SetWidgetPosAnimation(OriginalWidget, Duration)
    WidgetAnimation.finished.connect(
        lambda: StackedWidget.setCurrentIndex(TargetIndex),
        type = Qt.QueuedConnection
    )
    WidgetAnimation.finished.connect(
        lambda: OriginalWidget.setGeometry(OriginalGeometry),
        type = Qt.QueuedConnection
    )
    WidgetAnimation.start() if StackedWidget.currentIndex() != TargetIndex else None


def Function_AnimateFrame(
    Frame: QWidget,
    MinWidth: Optional[int] = None,
    MaxWidth: Optional[int] = None,
    MinHeight: Optional[int] = None,
    MaxHeight: Optional[int] = None,
    Duration: int = 210,
    Mode: str = "Toggle",
    SupportSplitter: bool = False
):
    '''
    Function to animate frame
    '''
    def ExtendFrame():
        QFunc.Function_SetWidgetSizeAnimation(Frame, MaxWidth, None, Duration, SupportSplitter).start() if MaxWidth not in (None, Frame.width()) else None
        QFunc.Function_SetWidgetSizeAnimation(Frame, None, MaxHeight, Duration, SupportSplitter).start() if MaxHeight not in (None, Frame.height()) else None

    def ReduceFrame():
        QFunc.Function_SetWidgetSizeAnimation(Frame, MinWidth, None, Duration, SupportSplitter).start() if MinWidth not in (None, Frame.width()) else None
        QFunc.Function_SetWidgetSizeAnimation(Frame, None, MinHeight, Duration, SupportSplitter).start() if MinHeight not in (None, Frame.height()) else None

    if Mode == "Extend":
        ExtendFrame()
    if Mode == "Reduce":
        ReduceFrame()
    if Mode == "Toggle":
        ExtendFrame() if Frame.width() == MinWidth or Frame.height() == MinHeight else ReduceFrame()


def Function_AnimateProgressBar(
    ProgressBar: QProgressBar,
    MinValue: int = 0,
    MaxValue: int = 100,
    DisplayValue: bool = False,
    IsTaskAlive: bool = False
):
    '''
    Function to animate progressbar
    '''
    ProgressBar.setTextVisible(DisplayValue)
    ProgressBar.setRange(MinValue, MaxValue)
    ProgressBar.setValue(MinValue)

    if IsTaskAlive == True:
        ProgressBar.setRange(0, 0)
        #QApplication.processEvents()
    else:
        ProgressBar.setRange(MinValue, MaxValue)
        ProgressBar.setValue(MaxValue)

##############################################################################################################################

def Function_SetWidgetValue(
    Widget: QWidget,
    Config: QFunc.ManageConfig,
    Section: str = ...,
    Option: str = ...,
    Value = ...,
    Times: Union[int, float] = 1,
    SetPlaceholderText: bool = False,
    PlaceholderText: Optional[str] = None
):
    if isinstance(Widget, (QLineEdit, QTextEdit, QPlainTextEdit)):
        QFunc.Function_SetText(Widget, Value, SetPlaceholderText = SetPlaceholderText, PlaceholderText = PlaceholderText)
        def EditConfig(Value):
            Config.EditConfig(Section, Option, str(Value))
        if Config is not None:
            Widget.textChanged.connect(lambda: EditConfig(Widget.text() if isinstance(Widget, (QLineEdit)) else Widget.toPlainText()))
            EditConfig(Value)

    if isinstance(Widget, (QComboBox)):
        itemTexts = []
        for index in range(Widget.count()):
            itemTexts.append(Widget.itemText(index))
        Widget.setCurrentText(str(Value)) if str(Value) in itemTexts else None
        def EditConfig(Value):
            Config.EditConfig(Section, Option, str(Value))
        if Config is not None:
            Widget.currentTextChanged.connect(EditConfig)
            EditConfig(Value) if str(Value) in itemTexts else None

    if isinstance(Widget, (QSpinBox, QSlider)):
        Widget.setValue(int(eval(str(Value)) * Times))
        def EditConfig(Value):
            Config.EditConfig(Section, Option, str(eval(str(Value)) / Times))
        if Config is not None:
            Widget.valueChanged.connect(EditConfig)
            EditConfig(Value)

    if isinstance(Widget, (QDoubleSpinBox, SliderBase, Frame_RangeSetting)):
        Widget.setValue(float(eval(str(Value)) * Times))
        def EditConfig(Value):
            Config.EditConfig(Section, Option, str(eval(str(Value)) / Times))
        if Config is not None:
            Widget.valueChanged.connect(EditConfig)
            EditConfig(Value)

    if isinstance(Widget, (QCheckBox, QRadioButton)):
        Widget.setChecked(eval(str(Value)))
        def EditConfig(Value):
            Config.EditConfig(Section, Option, str(Value))
        if Config is not None:
            Widget.toggled.connect(EditConfig)
            EditConfig(Value)

    if isinstance(Widget, Table_EditAudioSpeaker):
        Widget.SetValue(eval(str(Value)))
        def EditConfig(Value):
            Config.EditConfig(Section, Option, str(Value))
        if Config is not None:
            Widget.ValueChanged.connect(EditConfig)
            EditConfig(Value)


class ParamsManager:
    def __init__(self,
        ConfigPath: str,
    ):
        self.ConfigPath = ConfigPath
        self.Config = QFunc.ManageConfig(ConfigPath)

        self.RegistratedWidgets = {}

    def Registrate(self, Widget: QWidget, value: tuple):
        self.RegistratedWidgets[Widget] = value

    def SetParam(self,
        Widget: QWidget,
        Section: str = ...,
        Option: str = ...,
        DefaultValue = None,
        Times: Union[int, float] = 1,
        SetPlaceholderText: bool = False,
        PlaceholderText: Optional[str] = None,
        Registrate: bool = True
    ):
        Value = self.Config.GetValue(Section, Option, str(DefaultValue))
        Function_SetWidgetValue(Widget, self.Config, Section, Option, Value, Times, SetPlaceholderText, PlaceholderText)
        self.Registrate(Widget, (Section, Option, DefaultValue, Times, SetPlaceholderText, PlaceholderText)) if Registrate else None

    def ResetParam(self, Widget: QWidget):
        value = self.RegistratedWidgets[Widget]
        Function_SetWidgetValue(Widget, self.Config, *value)

    def ClearSettings(self):
        with open(self.ConfigPath, 'w'):
            pass
        self.Config = QFunc.ManageConfig(self.ConfigPath)

    def ResetSettings(self):
        self.ClearSettings()
        for Widget in list(self.RegistratedWidgets.keys()):
            self.ResetParam(Widget)

    def ImportSettings(self, ReadPath: str):
        ConfigParser = QFunc.ManageConfig(ReadPath).Parser()
        with open(self.ConfigPath, 'w', encoding = 'utf-8') as Config:
            ConfigParser.write(Config)
        for Widget, value in list(self.RegistratedWidgets.items()):
            self.SetParam(Widget, *value)

    def ExportSettings(self, SavePath: str):
        with open(SavePath, 'w', encoding = 'utf-8') as Config:
            self.Config.Parser().write(Config)

##############################################################################################################################

def Function_SetMethodExecutor(
    ParentWindow: Optional[QWidget] = None,
    ExecuteButton: Optional[QAbstractButton] = None,
    TerminateButton: Optional[QAbstractButton] = None,
    ProgressBar: Optional[QProgressBar] = None,
    ConsoleWidget: Optional[QWidget] = None,
    Method: object = ...,
    Params: Optional[tuple] = None,
    ParamsFrom: Optional[list[QObject]] = None,
    EmptyAllowed: Optional[list[QObject]] = None,
    SuccessEvents: Optional[list] = None
):
    '''
    Function to execute outer class methods
    '''
    QualName = str(Method.__qualname__)
    MethodName = QualName.split('.')[1]

    ClassInstance = QFunc.GetClassFromMethod(Method)()
    ClassInstance.started.connect(lambda: FunctionSignals.Signal_TaskStatus.emit(QualName, 'Started')) if hasattr(ClassInstance, 'started') else None
    ClassInstance.errChk.connect(
        lambda Err: (
            QFunc.RunEvents(SuccessEvents) if Err == str(None) else None,
            MessageBoxBase.pop(ParentWindow, QMessageBox.Warning, 'Failure', f'发生异常：\n{Err}') if Err != str(None) else None,
            FunctionSignals.Signal_TaskStatus.emit(QualName, 'Failed') if Err != str(None) else None
        )
    ) if hasattr(ClassInstance, 'errChk') else None
    ClassInstance.finished.connect(lambda: FunctionSignals.Signal_TaskStatus.emit(QualName, 'Finished')) if hasattr(ClassInstance, 'finished') else None

    if not isinstance(ClassInstance, QThread):
        WorkerThread = QThread()
        ClassInstance.moveToThread(WorkerThread)
        ClassInstance.finished.connect(WorkerThread.quit) if hasattr(ClassInstance, 'finished') else None
    else:
        WorkerThread = ClassInstance

    @Slot()
    def ExecuteMethod():
        '''
        Update the attributes for outer class methods and wait to execute with multithreading
        '''
        Args = Params#if Params != () else None
        if ParamsFrom not in ([], None):
            Args = Function_ParamsChecker(ParamsFrom, EmptyAllowed)
            if Args == "Abort":
                return print("Aborted.")
            else:
                pass #print("Continued.\n")

        FunctionSignals = CustomSignals_Functions()
        FunctionSignals.Signal_ExecuteTask.connect(getattr(ClassInstance, MethodName)) #FunctionSignals.Signal_ExecuteTask.connect(lambda Args: getattr(ClassInstance, MethodName)(*Args))

        WorkerThread.started.connect(lambda: Function_AnimateFrame(ConsoleWidget, MinHeight = 0, MaxHeight = 210, Mode = "Extend")) if ConsoleWidget else None
        WorkerThread.started.connect(lambda: Function_AnimateProgressBar(ProgressBar, IsTaskAlive = True)) if ProgressBar else None
        WorkerThread.started.connect(lambda: Function_AnimateStackedWidget(QFunc.Function_FindParentUI(ExecuteButton, QStackedWidget), Target = 1)) if TerminateButton else None
        WorkerThread.finished.connect(lambda: Function_AnimateFrame(ConsoleWidget, MinHeight = 0, MaxHeight = 210, Mode = "Reduce")) if ConsoleWidget else None
        WorkerThread.finished.connect(lambda: Function_AnimateProgressBar(ProgressBar, IsTaskAlive = False)) if ProgressBar else None
        WorkerThread.finished.connect(lambda: Function_AnimateStackedWidget(QFunc.Function_FindParentUI(ExecuteButton, QStackedWidget), Target = 0)) if TerminateButton else None
        #WorkerThread.finished.connect(lambda: FunctionSignals.Signal_ExecuteTask.disconnect(getattr(ClassInstance, MethodName)))

        FunctionSignals.Signal_ExecuteTask.emit(Args)

        WorkerThread.start()

    if ExecuteButton is not None:
        ExecuteButton.clicked.connect(ExecuteMethod)
    else:
        TempButton = QPushButton(ParentWindow)
        TempButton.clicked.connect(ExecuteMethod)
        TempButton.setVisible(False)
        TempButton.click()
        WorkerThread.finished.connect(TempButton.deleteLater)

    @Slot()
    def TerminateMethod():
        '''
        Terminate the running thread
        '''
        if not WorkerThread.isFinished():
            try:
                WorkerThread.terminate()
            except:
                WorkerThread.quit()

        ClassInstance.Terminate() if hasattr(ClassInstance, 'Terminate') else QFunc.ProcessTerminator('python.exe', SearchKeyword = True)

        FunctionSignals.Signal_TaskStatus.emit(QualName, 'Failed') if hasattr(ClassInstance, 'errChk') else None

        ProgressBar.setValue(0) if ProgressBar else None

    if TerminateButton is not None:
        TerminateButton.clicked.connect(
            lambda: MessageBoxBase.pop(ParentWindow,
                MessageType = QMessageBox.Question,
                WindowTitle = "Ask",
                Text = "当前任务仍在执行中，是否确认终止？",
                Buttons = QMessageBox.Yes|QMessageBox.No,
                ButtonEvents = {QMessageBox.Yes: lambda: TerminateMethod()}
            )
        )
        FunctionSignals.Signal_ForceQuit.connect(TerminateMethod)
    else:
        pass

##############################################################################################################################

def Function_UpdateChecker(
    RepoOwner: str,
    RepoName: str,
    FileName: str,
    FileFormat: str,
    CurrentVersion: str = ...,
):
    '''
    '''
    try:
        FunctionSignals.Signal_UpdateMessage.emit("正在检查更新，请稍等...\nChecking for updates, please wait...")
        IsUpdateNeeded, DownloadURL = QFunc.CheckUpdateFromGithub(
            RepoOwner = RepoOwner,
            RepoName = RepoName,
            FileName = FileName,
            FileFormat = FileFormat,
            Version_Current = CurrentVersion
        )

    except:
        #FunctionSignals.Signal_Message.emit("更新检查失败！\nFailed to check for updates!")
        FunctionSignals.Signal_IsUpdateSucceeded.emit(False, "更新检查失败！\nFailed to check for updates!")

    else:
        if IsUpdateNeeded:
            FunctionSignals.Signal_ReadyToUpdate.emit(DownloadURL)
        else:
            FunctionSignals.Signal_UpdateMessage.emit("已是最新版本！\nAlready up to date!")
            FunctionSignals.Signal_IsUpdateSucceeded.emit(False, "")

##############################################################################################################################