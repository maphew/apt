@echo off
setlocal EnableDelayedExpansion
call :arch
call :Diff
goto :eof

:arch
    echo.   Testing --arch Architecture flag...
    set _x=--arch=x86 list
    call apt.bat !_x! "current\apt-!_x!.stdout" 2> "current\apt-!_x!.stderr"
    set _x=--arch=x86_64 list
    call apt.bat !_x! "current\apt-!_x!.stdout" 2> "current\apt-!_x!.stderr"
    goto :eof

:Diff
    call winmergeu /s /xq expected current
    goto :eof