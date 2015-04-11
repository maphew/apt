@echo off
:: /etc/postinstall/apt-upgrade-apt.bat
:: Stub, to work through how apt-exe might update itself.
:: Works from cmd shell, but what about when called from within apt?

:: In testing it seems the path manipulation isn't necessary, but...
call :clean_path

@echo on
set _dir="%TEMP%\apt-old"
mkdir %_dir%
pushd %_dir%
xcopy /s "%OSGEO4W_ROOT%\apps\apt" .
.\apt.exe uninstall apt
.\apt.exe install apt
popd
rmdir /s/q %_dir%
@echo off

call :restore_path
goto :eof
:: ---------------------------------------------------------------------
:clean_path
    set _path=%PATH%
    set _pythonpath=%PYTHONPATH%
    set PYTHONPATH=
    set PATH=
    goto :eof

:restore_path
    set PATH=%_path%
    set PYTHONPATH=%_pythonpath%
    set _pythonpath=
    set _path=
    goto :eof
