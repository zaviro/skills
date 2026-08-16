---
name: proton-game-helper
description: "Use when troubleshooting Proton/Wine non-Steam games on Linux (Galgame, Chinese-patched games, doujin games). Triggers: game won't launch, crash on startup, story/dialogue text becomes question marks, missing/garbled fonts, layout corruption, black video, patch not applied, save data lost, or adding games to Steam with Proton-GE. 用于 Linux 下 Proton/Wine 游戏排障。"
license: MIT
metadata:
  version: 1.1.0
  author: zaviro (adapted for Hermes Agent)
  hermes:
    tags: [proton, wine, gaming, linux, steam, troubleshooting, chinese]
    related_skills: []
---

# Proton Game Helper (Proton 游戏排障与管理指南)

此 Skill 用于指导 Agent 定位并修复非 Steam Windows 游戏在 Proton/Wine 容器内的字体、注册表和汉化兼容性问题。

## 核心约定与默认设置
1. **游戏源目录**：游戏根目录默认位于 `~/games`（即 `/home/zaviro/games/`）。
2. **Proton 版本**：默认强制绑定的 Proton 兼容层版本为 `GE-Proton9-27`。
3. **中文环境配置**：中文 ANSI 汉化优先使用启动项 `LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 %command%`，同时保留用户已有的其他启动参数。

---

## 路由指南 (Decision Flow)
当你触发该 Skill 并排查特定问题时，**优先执行下方的"第一步"以提取 AppID 锁定容器，然后根据排障需求，使用 `read_file` 读取对应的子参考文件，严禁一次性全部读取：**

1. **排查字形大小时大时小 / 字体发虚 / 排版错乱 / 视频黑屏**
   - 决策：使用 `read_file` 读取 `references/font_troubleshooting.md`

2. **排查界面正常但剧情/对话全是问号 / 游戏注册表恢复 / 启动时闪退报错 / 容器语言环境（简体中文）注入**
   - 决策：使用 `read_file` 读取 `references/registry_recovery.md`

3. **排查打开汉化未生效（仍是日文） / 汉化启动器缺失 / 游戏历史存档丢失与迁移**
   - 决策：使用 `read_file` 读取 `references/patch_troubleshooting.md`

4. **排查点击启动没反应 / 启动后立即退出无报错 / 窗口不出现 / 多个非 Steam 游戏同时无法启动**
   - 决策：使用 `read_file` 读取 `references/launch_troubleshooting.md`

---

## 核心排障步骤

### 第一步：添加游戏并提取 AppID 锁定容器 (基础必做)

在进行任何容器内配置前，必须先获取游戏对应的虚拟 AppID 以定位其 Proton 容器。

> [!IMPORTANT]
> **唯一安全且防删库的做法**：
> 1. 指导用户直接在 **Steam 客户端内手动通过"添加非 Steam 游戏"** 将游戏的可执行文件引入，并在该快捷方式游戏的"属性 -> 兼容性"中勾选并指定 `GE-Proton9-27`。
> 2. 指导用户**正常退出 Steam 客户端**（以触发其将新添加的游戏信息持久化写入磁盘文件）。
> 3. **严禁**使用任何自动脚本改写并覆写 `shortcuts.vdf`。因为新版 Steam 文件的私有二进制结构一旦被脚本改坏，Steam 启动时会直接强制将其物理删除，导致用户所有的快捷方式游戏瞬间丢失。

#### 使用只读脚本安全提取 AppID
在用户退出 Steam 且文件写回后，在技能目录下运行此只读脚本提取该游戏的虚拟 AppID：
```bash
python3 ~/.hermes/skills/gaming/proton-game-helper/scripts/get_appid.py --name "<游戏名称中的关键字>"
```
脚本会同时显示当前 Steam 启动项。它只读取 `shortcuts.vdf`，不会改写。

提取到的虚拟 AppID 对应的 Proton 容器路径为：
```
~/.steam/debian-installation/steamapps/compatdata/<appid>/pfx/
```

### 第二步：根据排障类型，路由到对应的参考指南
成功获取 AppID 并锁定容器路径后，根据用户的具体故障现象，转到对应的子参考指南执行修复。
