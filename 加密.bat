@echo off
set PYTHON_EXEC="C:\Program Files\Autodesk\3ds Max 2022\Python37\python.exe"
set CODE_DIR="D:\AITest\MAXsd"

%PYTHON_EXEC% -m compileall %CODE_DIR%
