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

pushd %TEMP%\dev\dist
7z.exe a -sfx7z.sfx apt-exe-full.exe apt\*
@rem exclude all MS dlls except 'msvcr90.dll'
7z.exe a -sfx7z.sfx apt-exe-skinny.exe apt\* -r -x!mf*.dll -x!msvcp90.dll -x!msvcm90.dll
popd
  
start %TEMP%\dev

@goto :EOF

:: --- Notes ---

Requirements:

osgeo4w: python-core
pip: requests pyinstaller

7zip
