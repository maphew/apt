@echo off
setlocal
if "%1"=="all" (call :DefaultCmds) else (set cmds=%*)
if "%cmds%"=="" goto :Usage

call :Main %cmds%
call :Diff

goto :EOF
:: ----------------------------------------------------------------------------
:DefaultCmds
    set cmds='' available ball download find help info install list-installed listfiles md5 missing new remove requires search setup update upgrade url version
    goto :eof
:Main
    for %%a in (%cmds%) do (
        if exist "current\apt-%%a.*" del "current\apt-%%a.*"
        echo.   Test: apt %%a
        call apt.bat %%a 1> "current\apt-%%a.stdout" 2> "current\apt-%%a.stderr"
        )
    goto :eof
:Diff
    call winmergeu /s /xq expected current
    goto :eof
:Usage
    echo.
    echo.   Specify apt command to test; use "all" for everything.
    goto :eof
