ping -n 1 www.google.com >nul
if errorlevel 1 (
	cls
	echo msgbox "No internet connection! Please try again!" > %tmp%\tmp.vbs
	wscript %tmp%\tmp.vbs
	del %tmp%\tmp.vbs
	exit /b
)
git clone https://github.com/glosoftgroup/app.git
ren app app