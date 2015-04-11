call build-exe.bat

setlocal enabledelayedexpansion
set ver=0.3-2
set pkgdir=\o4w-packages\apt\apt-%ver%

call :Structure !pkgdir!
call :make_exe !pkgdir!

goto :eof

:make_exe 
    :: Copy apt distribution files (from pyinstaller) into o4w structure
    :: then move apt.exe into it's own container.
    :: Finally wrap up each into archives ready for uploading to package mirror.
    ::
    set pkgdir=%1
    if not exist "%pkgdir%" mkdir "%pkgdir%"
    pushd "%pkgdir%"
    
    xcopy /s \dist\apt\* "lib\apps\apt"
    mkdir exe\apps\apt
    move lib\apps\apt\apt.exe exe\apps\apt
    
    popd
    goto :eof

:Structure
    set pkgdir=%1
    if not exist "%pkgdir%" mkdir "%pkgdir%"
    pushd "%pkgdir%"
    
    xcopy /s/e ..\apt-skeleton .
        :: contains pre/posinstall actions, update as needed.
        
    mkdir bin
    mkdir apps\apt
    
    xcopy /s \dist\apt\* "%pkgdir%\apps\apt"
    
    
    echo @^"%%~dp0\..\apps\apt\apt.exe^" %%* > "%pkgdir%"\bin\apt.bat
    
    explorer "%pkgdir%"
    
:: create distribution archive
tar --exclude=setup.hint cvjf ../apt-%ver%.tar.bz2 ./

:: upload to /osgeo/download/osgeo4w/x86/release/apt
:: run http://upload.osgeo.org/cgi-bin/osgeo4w-regen.sh

:: test install/upgrade using setup-test.bat and/or apt iteself (might break 'cause of in use files).
::      wget http://download.osgeo.org/osgeo4w/x86/setup_test.ini
::      apt -i setup_test.ini new
::      apt -i setup_test.ini upgrade


REM  pushd ..
REM  if not exist setup.hint wget http://download.osgeo.org/osgeo4w/x86/release/apt/setup.hint
REM  popd
