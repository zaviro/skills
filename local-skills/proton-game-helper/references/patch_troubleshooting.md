# Proton 游戏汉化补丁与存档迁移排障指南

本指南用于解决在 Proton 容器下运行汉化补丁时，遇到的汉化未生效、路径无写入权限或存档丢失的问题。

## 1. 汉化专用启动器缺失（如 `*_cn.exe`）
许多免修改原版 EXE 的汉化补丁是基于 DLL 隐式加载的（例如检测自身文件名是否为 `*_cn.exe`，进而加载同目录的汉化 DLL）。
* **现象**：游戏能正常打开，但仍然是日文。
* **排查方法**：
  - 检查游戏根目录下是否存在带有 `_cn` 或者是 `_Chs` 等后缀的汉化专用启动器 `.exe`（例如 `haison_cn.exe`）。
  - **注意**：原版主程序（如 `haison.exe`）哪怕重命名为 `haison_cn.exe` 也是无用的。因为真正的汉化启动器二进制是经过修改或内嵌注入逻辑的。
  - 若用户目录中确实缺失它，应排查是否解压时被杀毒软件删除、或者用户漏拷贝了它。可在系统中搜索 `_wm` 或 `_Chs` 等变体备份目录以找回该文件。
* **修复方法**：
  - 指导用户在 Steam 客户端的游戏属性中，将**“目标”**和**“起始目录”**修改为指向这个专用的 `haison_cn.exe`。

## 2. 汉化安装程序提示“找不到原版游戏”或“无法写入 Z:\ 盘”
由于 Steam Runtime 的 `pressure-vessel` 沙箱环境限制，运行在 Proton 容器内的 Windows 安装程序往往无法写入主机的真实 `Z:\` 盘，且默认的 `C:\Program Files\` 中由于没有游戏本体，安装包会校验失败。
* **【解决方案】—— C 盘软链接桥梁：**
  In the virtual `C:` drive, create a symbolic link pointing to the real game folder on host:
  ```bash
  ln -sf "$HOME/games/<game-subdir>" "$HOME/.steam/debian-installation/steamapps/compatdata/<appid>/pfx/drive_c/<link-name>"
  ```
  之后启动汉化安装包，在弹出的窗口中将安装路径直接选择或手动填入：
  ```
  C:\<link-name>
  ```
  补丁会顺利通过沙箱写权限，并实时回写覆盖到主机的游戏本体中。

## 3. 汉化后的存档迁移
* **现象**：游戏成功汉化运行，但之前的历史游玩存档丢失了。
* **原因**：很多游戏在成功加载汉化补丁后，其存档目录名也会发生变化（例如从原版的 `Haison` 变为汉化版的 `Haison_cn`），导致游戏找不到之前的存档。
* **解决方法**：
  - 定位到新旧 Proton 容器对应的虚拟 C 盘路径：
    `~/.steam/debian-installation/steamapps/compatdata/<appid>/pfx/drive_c/users/steamuser/Documents/ESCUDE/`
  - 将原有的实际游玩存档文件（通常在旧游戏目录下或旧容器内，包含 `save_*.dat` 进度数据）复制到新容器的对应汉化存档文件夹（如 `Haison_cn/save/`）下。
