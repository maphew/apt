@echo off
setlocal EnableDelayedExpansion
set osgeo4w_root=%TEMP%\apt-%RANDOM%
call :arch
call :Diff
set osgeo4w_root=
goto :eof

:arch
    echo.   Testing --bit CPU Architecture flag...
    
    :: bare setup, no bits
    set _x=setup
    call apt.bat !_x! "current\apt-!_x!.stdout" 2> "current\apt-!_x!.stderr"
    rd /s/q "!osgeo4w_root!"

    :: 32 bit
    set _x=--bits=32 setup
    call apt.bat !_x! "current\apt-!_x!.stdout" 2> "current\apt-!_x!.stderr"
    rd /s/q "!osgeo4w_root!"
    
    :: 64 bit
    set _x=--bits=64 setup
    call apt.bat !_x! "current\apt-!_x!.stdout" 2> "current\apt-!_x!.stderr"
    rd /s/q "!osgeo4w_root!"
    goto :eof

:Diff
    call winmergeu /s /xq expected current
    goto :eof