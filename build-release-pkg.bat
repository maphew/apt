call build-exe.bat

setlocal
set ver=0.3-1
set pkgdir=\o4w-packages\apt\apt-%ver%

if not exist "%pkgdir%" mkdir "%pkgdir%"
pushd "%pkgdir%"

mkdir bin
mkdir apps\apt

xcopy /s \dist\apt\* "%pkgdir%\apps\apt"

pushd ..
if not exist setup.hint wget http://download.osgeo.org/osgeo4w/x86/release/apt/setup.hint
popd

echo @^"%%~dp0\..\apps\apt\apt.exe^" %%* > "%pkgdir%"\bin\apt.bat

explorer "%pkgdir%"
