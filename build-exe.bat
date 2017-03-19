pyinstaller ^
  --distpath=%TEMP%\dev\dist ^
  --workpath=%TEMP%\dev\build ^
  --noconfirm ^
  --onedir ^
  apt.py

pyinstaller ^
  --distpath=%TEMP%\dev\dist ^
  --workpath=%TEMP%\dev\build ^
  --noconfirm ^
  --onefile ^
  apt.py
  
start %TEMP%\dev
