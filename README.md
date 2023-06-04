# 3ds Max 稳定扩散插件 - Stable Diffusion Plugin for 3ds Max

本插件为 3ds Max 提供Stable Diffusion支持

## 安装 - Installation

### 依赖项 - Dependencies

在安装插件之前，请确保已安装以下依赖项：
- Before installing the plugin, make sure you have the following dependencies installed:

- Autodesk 3ds Max 202x
- Python（已包含在 3ds Max 202x 中

### 安装依赖项 - Installing Dependencies

要安装所需的依赖项，请按照以下步骤进行操作：
- To install the required dependencies, follow these steps:

1. 打开命令提示符或终端。- Open Command Prompt or a terminal.
2. 导航到 3ds Max 安装目录中的 Python 安装目录。默认路径为：`C:\Program Files\Autodesk\3ds Max 2022\Python37`
- Navigate to the Python installation directory in your 3ds Max installation folder. The default path is: `C:\Program Files\Autodesk\3ds Max 2022\Python37`
3. 创建一个新文件，并将以下内容粘贴到文件中：
- Create a new file and paste the following content into it:

```bat
@echo off
cd "C:\Program Files\Autodesk\3ds Max 2022\Python37"

REM 升级 pip 包
python.exe -m ensurepip --upgrade --user

REM 安装第三方包
python.exe -m pip install requests clipboard

REM 提示安装完成
echo 依赖项安装成功！
pause
```

4. 以 `.bat` 扩展名保存该文件，例如 `install_dependencies.bat`。
- Save the file with a `.bat` extension, for example, `install_dependencies.bat`.
5. 双击运行 `.bat` 文件以执行它。这将升级 `pip` 并安装所需的包。
- Double-click the `.bat` file to execute it. This will upgrade `pip` and install the required packages.

> 注意：确保在 `.bat` 脚本中将 Python 安装路径替换为实际的 3ds Max Python 安装路径。
- Note: Make sure to replace the Python installation path in the `.bat` script with your actual 3ds Max Python installation path.

 确保在启动 3ds Max 时开启了 Web UI 并使用 `--api` 参数。
- Ensure that the Web UI is enabled and started with the `--api` parameter when launching 3ds Max.

### 插件安装 - Plugin Installation

要安装稳定扩散插件，请按照以下步骤进行操作：
- To install the Stable Diffusion plugin, follow these steps:
1. 克隆或下载本仓库到本地计算机。
- Clone or download this repository to your local machine.
2. 将插件文件复制到 3ds Max 安装目录中的适当位置。确切的位置可能因你的设置而有所不同。
- Copy the plugin files to the appropriate location within your 3ds Max installation directory. The exact location may vary depending on your setup.
3. 启动 3ds Max 并导航到插件管理器。
- Launch 3ds Max and navigate to the plugin manager.
4. 找到stable diffusion插件并启用它。
- Locate the Stable Diffusion plugin and enable it.

## 使用方法 - Usage

安装并启用插件后，可以在 3ds Max 中访问stable diffusion功能。有关如何使用插件的详细说明，请参阅插件的文档或示例。
[点击这里观看视频](https://www.bilibili.com/video/BV1wz4y1q7YW?t=635.8)
- Once the plugin is installed and enabled, you can access the stable diffusion functionality within 3ds Max. Refer to the plugin documentation or examples for detailed instructions on how to use it.

## 注意事项 - Important Notes

- 确保在 `.bat` 脚本中提供正确的 Python 安装目录路径（`C:\Program Files\Autodesk\3ds Max 2022\Python37`）。
- Ensure that you provide the correct path to the Python installation directory (`C:\Program Files\Autodesk\3ds Max 2022\Python37`) in the `.bat` script.
- 以管理员权限运行 `.bat` 脚本，以确保正确安装依赖项。
- Run the `.bat` script with administrator privileges to ensure proper installation of dependencies.
- 请确保检查插件与你的 3ds Max 版本的兼容性。
- Make sure to check the compatibility of the plugin with your version of 3ds Max.
- 确保在启动 3ds Max 时开启了 Web UI 并使用 `--api` 参数。
- Ensure that the Web UI is enabled and started with the `--api` parameter when launching 3ds Max.
- 如有任何问题或疑问，请参阅文档或在 GitHub 仓库中创建问题。
- For any issues or questions, please refer to the documentation or create an issue in the GitHub repository.