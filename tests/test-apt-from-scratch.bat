@echo off
setlocal
set aptexe=%~dp0\..\..\..\dist\apt\apt.exe
if not exist "%aptexe%" goto :noExe

set odir=osgeo4w_%random%
set osgeo4w_root=%temp%\%odir%

if exist %osgeo4w_root% rmdir /q %osgeo4w_root%
mkdir %osgeo4w_root%
pushd %osgeo4w_root%

call :cleanEnv
call :makeInstall

%SystemRoot%\System32\cmd.exe /k apt-install-test.bat

popd
endlocal
goto :eof
:: ------------------------------------------------
:cleanEnv
    echo.
    echo.   Ensuring clean environment
    echo.
    set path=
    set pythonhome=
    prompt %odir%$G$_
    goto :eof
    
:makeInstall
    echo.
    echo.   Building installer script
    echo.
    echo %aptexe% setup > apt-install-test.bat
    echo %aptexe% update >> apt-install-test.bat
    echo %aptexe% install apt >> apt-install-test.bat
    echo.
    type apt-install-test.bat
    goto :eof
    
:noExe
    echo.
    echo.   Apt.exe not found at %aptexe%
    echo.
    echo.   did you forget to run `build-exe.bat`?
    echo.
    pause
    goto :eof
