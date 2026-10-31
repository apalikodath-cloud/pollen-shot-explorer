@echo off
rem PM-012: build the own LBM solver (pm012_lbm.cpp) with MSVC x64. Output outside the repo (%PM012_CFD_ROOT%\pm012_lbm\bin; PM012_CFD_ROOT = a folder outside the repo).
rem Usage: build.cmd [output folder]. Needs Visual Studio with the C++ workload; edit VCVARS if it lives elsewhere.
setlocal
set "OUT=%PM012_CFD_ROOT%\pm012_lbm\bin"
if not "%~1"=="" set "OUT=%~1"
set "VCVARS=C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
call "%VCVARS%" >nul
if errorlevel 1 exit /b 1
if not exist "%OUT%" mkdir "%OUT%"
cl /nologo /O2 /EHsc /W3 /std:c++17 /D_CRT_SECURE_NO_WARNINGS "%~dp0pm012_lbm.cpp" /Fo"%OUT%\pm012_lbm.obj" /Fe"%OUT%\pm012_lbm.exe"
if errorlevel 1 exit /b 1
copy /y "%~dp0pm012_lbm.cl" "%OUT%\pm012_lbm.cl" >nul
echo build ok: %OUT%\pm012_lbm.exe
exit /b 0
