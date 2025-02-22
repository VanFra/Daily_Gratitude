import sys
import os

# Add the directory of the WSGI file to the Python path
sys.path.insert(0, '/home/u020/public_html/Chat_Client_homework/Daily_Gratitude')

from channel import app
application = app

