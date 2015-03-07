call build-exe.bat

setlocal
set ver=0.3-1
set pkgdir=\o4w-packages\apt\apt-%ver%

if not exist "%pkgdir%" mkdir "%pkgdir%"
pushd "%pkgdir%"

xcopy /s/e ..\apt-skeleton .
    :: contains pre/postinstall actions, update as needed.
    
mkdir bin
mkdir apps\apt

xcopy /s \dist\apt\* "%pkgdir%\apps\apt"

pushd ..
if not exist setup.hint wget http://download.osgeo.org/osgeo4w/x86/release/apt/setup.hint
popd

:: Write the batch file which will call apt in daily use
echo @^"%%~dp0\..\apps\apt\apt.exe^" %%* > "%pkgdir%"\bin\apt.bat

:: have a look at the package folder and see if everything is ok
explorer "%pkgdir%"

:: create distribution archive
tar cvjf ../apt-0.3-1.tar.bz2

:: upload to /osgeo/download/osgeo4w/x86/release/apt
:: run http://upload.osgeo.org/cgi-bin/osgeo4w-regen.sh

:: test install/upgrade using setup-test.bat and/or apt iteself (might break 'cause of in use files).
::      wget http://download.osgeo.org/osgeo4w/x86/setup_test.ini
::      apt -i setup_test.ini new
::      apt -i setup_test.ini upgrade
