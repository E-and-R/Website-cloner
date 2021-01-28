import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from os.path import expanduser
from PyQt5 import QtCore, QtGui, QtWidgets
import time 



class progressGUI(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        self.setGeometry(10, 10, 800, 800)
        self.showMaximized() 
        self.setWindowTitle('CMS Converter')
        
        self.status = QLabel('In Progress.....')
        self.status.setAlignment(Qt.AlignCenter)
        
        information = QLabel("Information")
        
        self.timer = QTimer()
        self.timeQT = QTime(0, 0, 0)
        time_label = QLabel("Time:")
        self.time= QLabel(self.timeQT.toString("hh:mm:ss"))

        self.type_message = QLabel("Type of CMS: ")
        self.type_name = QLabel('None')
        
        pages_label = QLabel("Number of Pages converted:")
        self.num_pages = QLabel("0")
        
        contents_label = QLabel("Number of Contents Downloaded:")
        self.contents_num = QLabel("0")
        
        status_title = QLabel('Number of pages being converted:')
        self.num_status_pages = QLabel('0')
        
        self.progress_output = LogTextEdit(readOnly=True)
        
        grid1 = QGridLayout()
        grid1.addWidget(time_label,0,0)
        grid1.addWidget(self.time,0,1)
        grid1.addWidget(self.type_message,1,0)
        grid1.addWidget(self.type_name,1,1)
        grid1.addWidget(pages_label,2,0)
        grid1.addWidget(self.num_pages,2,1)
        grid1.addWidget(contents_label,3,0)
        grid1.addWidget(self.contents_num,3,1)
        grid1.addWidget(status_title,4,0)
        grid1.addWidget(self.num_status_pages,4,1)
        
        grid1_widget = QWidget()
        grid1_widget.setLayout(grid1)
        grid1_widget.setStyleSheet("""
                            .QWidget {
                                border-color: white;
                                border-width: 0px;
                                border-style: solid;
                                border-radius: 0px
                                
                                }
                         """)
        
        hbox = QHBoxLayout()
        hbox.addWidget(grid1_widget)
        
        hbox_widget = QWidget()
        hbox_widget.setLayout(hbox)
        hbox_widget.setStyleSheet("""
                            .QWidget {
                                border-color: white;
                                border-width: 2px;
                                border-style: solid;
                                border-radius: 3px
                                
                                }
                         """)
       
        urls_title = QLabel('URL')
        progress_title = QLabel('Progress')
        
        
        grid3 = QGridLayout()
        grid3.addWidget(QLabel("Progress Information"),0,0)
        grid3.addWidget(self.progress_output,1,0)
       
        grid3_widget = QWidget()
        grid3_widget.setStyleSheet("""
                            .QWidget {
                                border-color: white;
                                border-width: 2px;
                                border-style: solid;
                                border-radius: 3px
                                
                                }
                         """)
        
        grid3_widget.setLayout(grid3)
        
        #main layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.status)
        vbox.addWidget(hbox_widget)
        vbox.addWidget(grid3_widget)
        
        self.setLayout(vbox)
        
    
    def progress_update(self,message):
        self.status.setText(message)
    
    def set_cms(self,cms_names):
        message = " , "
        message = message.join(cms_names)
        if message.strip() == "":
            message = "Not a CMS website"
        self.type_name.setText(message)
        
    ''' Update the total number of pages executed in parallel '''   
    def update_num_active_pages(self,num):
        self.num_status_pages.setText(str(num))
    
    ''' Update the total number of website content downloaded '''
    def update_num_downloaded_contents(self,num):
        self.contents_num.setText(str(num))
        
    ''' update the total number of pages saved '''
    def update_pages(self,num_pages):
        num = int(self.num_pages.text()) + num_pages
        self.num_pages.setText(str(num))
    
    ''' Update timer'''
    def update_timer(self):    
        self.timeQT = self.timeQT.addSecs(1)
        self.time.setText(self.timeQT.toString("hh:mm:ss"))
    
    ''' Starts the timer '''
    def start_timer(self):    
        self.timer.timeout.connect(lambda: self.update_timer())
        self.timer.start(1000)
    
    ''' Stops the timer'''
    def stop_timer(self):
        self.timer.stop()

''' Custom widget for displaying the progress bar'''
class LogTextEdit(QtWidgets.QPlainTextEdit):
    def write(self, message):
        if not hasattr(self, "flag"):
            self.flag = False
        message = message.replace('\r', '').rstrip()
        if message:
            method = "replace_last_line" if self.flag else "appendPlainText"
            QtCore.QMetaObject.invokeMethod(self,
                method,
                QtCore.Qt.QueuedConnection, 
                QtCore.Q_ARG(str, message))
            self.flag = True
        else:
            self.flag = False

    @QtCore.pyqtSlot(str)
    def replace_last_line(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.select(QtGui.QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.insertBlock()
        self.setTextCursor(cursor)
        self.insertPlainText(text)
    
    ''' Enables scroll view '''
    def flush(self):
        pass
