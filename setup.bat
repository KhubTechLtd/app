@echo off

call py-dist\scripts\env.bat
cd requirements\
pip install --upgrade pip
pip install cefpython3
pip install rcssmin --install-option="--without-c-extensions"
pip install rjsmin --install-option="--without-c-extensions"
pip install django-compressor --upgrade
easy_install http://www.voidspace.org.uk/python/pycrypto-2.6.1/pycrypto-2.6.1.win32-py2.7.exe
pip install -r setup_requirements.txt
pause