rem del /s /q /f /migrations/*.py

for /f %%i in ("C:\Desktop\app\*") do if /i not "%%~nxi"=="userprofile/migrations" del /s /q /f "%%i".py
rem for /d %%i in ("C:\Parent\*") do if /i not "%%~nxi"=="MYFOLDER" del /s /q "%%i"