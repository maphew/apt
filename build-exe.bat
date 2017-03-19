pyinstaller ^
  --distpath=%TEMP%\dev\dist ^
  --workpath=%TEMP%\dev\build ^
  --noconfirm ^
  apt-onedir-excludes.spec

pyinstaller ^
  --distpath=%TEMP%\dev\dist ^
  --workpath=%TEMP%\dev\build ^
  --noconfirm ^
  apt-onefile-excludes.spec
  
start %TEMP%\dev
