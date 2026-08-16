# Proton 游戏注册表修复与防乱码导入指南

老旧游戏引擎常依赖系统 ANSI 代码页，也可能在启动时校验安装路径注册表。优先用进程 Locale 修复代码页，只在无效时改注册表。

## 1. 界面正常，剧情/对话全是问号

这种分层异常通常不是界面字体问题：界面可能是图像或 Unicode 资源，剧情脚本则依赖简体中文 ANSI 代码页。字符在解码阶段被替换后会显示为 `?`；缺失字形则更常见于方框、空白或字形错乱。

按以下顺序排查：

1. 用 `scripts/get_appid.py --name "<关键字>"` 确认 AppID 和当前启动项。
2. 运行 `locale -a | rg -i 'zh_CN.*utf'` 确认主机提供简体中文 UTF-8 Locale。
3. 在 Steam 的游戏属性中手动设置启动项：

   ```bash
   LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 %command%
   ```

   如果已有其他环境变量或参数，将上述两个变量合并到原启动项中，只保留一个 `%command%`。
4. 完全退出游戏后重新启动并测试新对话。不要先重建前缀、安装字体或运行转区工具。
5. 只有启动项无效时，再检查 `pfx/user.reg` 中 `[Control Panel\\International]` 的 `Locale`/`LocaleName`，并考虑执行第 3 节的注册表修复。

> 已验证案例：某中文 ANSI 汉化 Galgame 在 `GE-Proton9-27` 下界面正常、剧情全为问号；其 Steam 启动项为空，加入上述 Locale 变量后恢复正常。

## 2. 注册表修复与防乱码导入
使用管道 `echo ""` 传给 `proton run`，在终端以静默方式拉起游戏自带的注册表修复批处理（如 `.bat` 恢复工具），可直接跳过 `pause` 挂起：
```bash
export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.steam/debian-installation"
export STEAM_COMPAT_DATA_PATH="$HOME/.steam/debian-installation/steamapps/compatdata/<appid>"
echo "" | ~/.steam/debian-installation/compatibilitytools.d/GE-Proton9-27/proton run "$HOME/games/<game-subdir>/注册表恢复(首次运行).bat"
```
这能让 Wine 内置环境生成 100% 格式吻合的注册表项目，完美通过检测。

## 3. 强制修改 Wine 容器的 Locale 注册表（简体中文）
当游戏引擎依赖系统 Locale 来决定语言加载或字符集展示时，若需要强制将整个容器重置为简体中文区域，可将以下内容写入临时 `.reg` 文件并导入容器：
```reg
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Control Panel\International]
"Locale"="00000804"
"LocaleName"="zh-CN"
"sCountry"="China"
"sLanguage"="CHS"

[HKEY_CURRENT_USER\Control Panel\International\User Profile\zh-CN]
"0804:00000804"=dword:00000001
```
导入命令：
```bash
export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.steam/debian-installation"
export STEAM_COMPAT_DATA_PATH="$HOME/.steam/debian-installation/steamapps/compatdata/<appid>"
~/.steam/debian-installation/compatibilitytools.d/GE-Proton9-27/proton run reg import <path_to_reg_file>
```

导入前确认游戏已退出，并备份该前缀的 `user.reg`。不要在未确认 AppID 时修改注册表。
