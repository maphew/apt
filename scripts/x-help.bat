@pushd %~dp0
@if "%1"=="" call :everything
@if not "%1"=="" call :search %*
@popd
@goto :eof

:everything
  @echo.
  @echo.--- %~n0: Local project commands (%~dp0) ---
  @echo.
  @dir /w/b *.bat *.cmd *.sh1 *.py *.com *.exe
  @REM todo: use PATHEXT instead of hardcode types.
  @echo.
  @echo --- There's also: x-help [search text]
  @goto :eof

:search
  @echo.
  @dir /w/b *.bat *.cmd *.sh1 *.py *.com *.exe | findstr -i "%*"
  @goto :eof
  