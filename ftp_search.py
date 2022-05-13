from ftplib import FTP
import os


ftp = FTP('ftp.zakupki.gov.ru')
ftp.login('free', 'free')
ftp.set_pasv(True)
print(ftp.dir())
ftp.close()
