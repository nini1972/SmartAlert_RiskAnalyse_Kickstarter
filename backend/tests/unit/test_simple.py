import os
print('Current directory:', os.getcwd())
print('Files in current directory:', os.listdir('.'))
print('Testing if config directory exists:', os.path.isdir('config'))
print('Testing if settings.py exists:', os.path.isfile('config/settings.py'))

