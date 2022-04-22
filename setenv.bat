@echo.
@echo.=== Setting environment for (%~dp0) ===
@path=%path%;%~dp0\scripts
@echo.
@REM @set gdal_cachemax=30%%
@REM @set GDAL_TIFF_INTERNAL_MASK=NO
@REM @set gdal
@call x-help
@echo.
@REM @set prompt=(%~p0) $E[m$E[32m$E]9;8;"USERNAME"$E\@$E]9;8;"COMPUTERNAME"$E\$S$E[92m$P$E[90m$_$E[90m$$$E[m$S$E]9;12$E\

call conda activate apt

@REM Remove all quotes from string (see https://ss64.com/nt/syntax-dequote.html)
@REM   Without this CMDCMDLINE is: "C:\WINDOWS\system32\cmd.exe" /C ""T:\ENV.558\setenv.bat" "
@REM   which causes error: /C was unexpected at this time.
@rem   when used with IF.
@set _=%CMDCMDLINE:"=%

@REM If the CMD command line does not equal "cmd  /k" we  assume script was 
@REM started from Explorer, so initialise command shell and keep it open, 
@REM otherwise return to calling shell.
@if "%_%" equ "cmd  /k" (
  @echo "Matched, returning to source shell"
  ) else (
  cmd /k
  )

