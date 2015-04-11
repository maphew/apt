@echo off
call build-exe.bat
setlocal enabledelayedexpansion
set ver=0.3-3
set pkgdir=\o4w-packages\apt\apt-%ver%

call :make_exe !pkgdir!
call :archive !pkgdir! exe
call :archive !pkgdir! lib

explorer "%pkgdir%"
goto :eof
:: ---------------------------------------------------------------------
:make_exe 
    :: Copy apt distribution files (from pyinstaller) into o4w structure
    :: then move apt.exe into it's own container.
    :: Finally wrap up each into archives ready for uploading to package mirror.
    ::    
    set pkgdir=%1
    if not exist "%pkgdir%" mkdir "%pkgdir%"
    pushd "%pkgdir%"
    
    call :make_skeleton lib
    xcopy /s \dist\apt\* lib\apps\apt

    call :make_skeleton exe
    move lib\apps\apt\apt.exe exe\apps\apt    
    echo @^"%%~dp0\..\apps\apt\apt.exe^" %%* > exe\bin\apt.bat
    
    popd
    goto :eof

:make_skeleton
    :: Create "as installed" folder structure
    mkdir "%1" & pushd "%1"
    mkdir bin
    mkdir apps\apt
    popd
    goto :eof


:archive
    :: create distribution archive
    pushd "%1\%2"
    set type=%2
    tar --exclude=setup.hint -cvjf ../apt-%type%-%ver%.tar.bz2 *
    popd
    goto :eof
    
:: upload to /osgeo/download/osgeo4w/x86/release/apt
:: run http://upload.osgeo.org/cgi-bin/osgeo4w-regen.sh

:: test install/upgrade using setup-test.bat and/or apt iteself (might break 'cause of in use files).
::      wget http://download.osgeo.org/osgeo4w/x86/setup_test.ini
::      apt -i setup_test.ini new
::      apt -i setup_test.ini upgrade

:: Generate ini for specific day (useful for testing upgrades)
:: must be run in remote shell
REM  /osgeo/download/osgeo4w/genini --date=2015-01-01 --arch=x86 --recursive --output=old.ini /osgeo/download/osgeo4w/x86/release

REM  pushd ..
REM  if not exist setup.hint wget http://download.osgeo.org/osgeo4w/x86/release/apt/setup.hint
REM  popd
