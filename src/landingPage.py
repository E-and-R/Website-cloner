import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from os.path import expanduser
import time 
from WebsiteDownloader import startProceedings


class landingPage(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        
        self.setGeometry(10, 10, 430, 300)
        self.setWindowTitle('Website Cloner')

        title = QLabel('Website cloner built with python')
        title.setAlignment(Qt.AlignCenter)
        
        self.url = QLabel('Enter website URL:')
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText('http://www.example.com')
        self.url_edit.setMaximumSize(300,50)
        
        self.allow_domains = QLabel('Allowed domains:')
        self.allow_domains_edit = QTextEdit()
        self.allow_domains_edit.setPlaceholderText('http://www.text.com')
        self.allow_domains_edit.setMaximumSize(300,300)
        
        grid = QGridLayout() 
        grid.addWidget(self.url, 0, 0)  
        grid.addWidget(self.url_edit, 0, 1)  
        
        
        grid_widget = QWidget()
        grid_widget.setLayout(grid)
        
        download = QPushButton("Download")
        
        vbox = QVBoxLayout()
        vbox.addWidget(title)
        vbox.addWidget(grid_widget)
        vbox.addWidget(download)

        self.setLayout(vbox)
        download.clicked.connect(self.download_clicked) 
        
    ''' Select download directory and start conversion '''
    def download_clicked(self):
        my_dir = QFileDialog.getExistingDirectory(self,"Open a folder",expanduser("~"), QFileDialog.ShowDirsOnly)
        if my_dir:  
            website_url = self.url_edit .displayText()
            allowed_domains = self.allow_domains_edit.toPlainText().split('\n')
            directory = my_dir
            cms_converter = startProceedings(website_url,allowed_domains,directory)

        
def main():
    app = QApplication(sys.argv)
    abs_widget = landingPage()
    abs_widget.show()
    sys.exit(app.exec_())

main()
