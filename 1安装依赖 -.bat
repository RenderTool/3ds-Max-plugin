@echo off
cd "C:\Program Files\Autodesk\3ds Max 2022\Python37"

REM 升级pip包
python.exe -m ensurepip --upgrade --user

REM 安装第三方包
python.exe -m pip install requests clipboard

REM 提示安装完成
echo Packages installed successfully!
pause
