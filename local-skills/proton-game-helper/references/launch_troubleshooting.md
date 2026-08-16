# Proton 游戏启动失败排障指南

当游戏点击"开始游戏"后完全没有窗口出现、进程立即消失、或仅在后台短暂运行后退出（Steam 日志有 `Game process added → removed` 但无窗口）时，按以下顺序排查。

## 1. vkBasalt 配置缺失导致 Vulkan 层初始化崩溃

**现象**：Steam 启动项中含有 `ENABLE_VKBASALT=1`，但游戏启动后进程瞬间退出，无任何错误弹窗。命令行下用 `proton run` 测试表现为退出码 0（干净退出）而非超时被杀。

**原因**：vkBasalt 需要配置文件 `~/.config/vkBasalt/vkBasalt.conf` 才能正常初始化。没有该文件时，Vulkan 层创建失败会导致游戏在创建窗口前直接退出。

**排查**：检查游戏在 Steam 中的启动选项是否包含 `ENABLE_VKBASALT=1`；同时检查 `~/.config/vkBasalt/vkBasalt.conf` 是否存在。

**修复**：
```bash
mkdir -p ~/.config/vkBasalt
cat > ~/.config/vkBasalt/vkBasalt.conf << 'EOF'
effects = cas
casSharpness = 0.4
debug = false
EOF
```
或者从启动选项中移除 `ENABLE_VKBASALT=1`（让用户自己在 Steam 属性中修改）。

## 2. Proton 前缀版本不匹配导致 "Prefix has an invalid version"

**现象**：多次切换游戏的 Proton 兼容工具版本（如在 GE-Proton9、GE-Proton10、官方 Proton 9.0 之间切换），或者批量重新添加非 Steam 游戏脚本改变了兼容层设置后，游戏启动无反应。命令行下会看到 `Prefix has an invalid version?!`。

**原因**：每个 Proton 前缀在 `<compatdata>/<appid>/version` 中记录了创建它的 Proton 版本。当 Steam 用版本 A 启动一个由版本 B 创建的前缀时，Proton 会对前缀进行就地"升级"，跨大版本升级（尤其是 GE ↔ 官方之间）可能产生不一致状态，导致 Wine 进程无法正常创建窗口。

**排查**：
```bash
# 查看前缀创建时使用的 Proton 版本
cat ~/.steam/debian-installation/steamapps/compatdata/<appid>/version
# 对比 Steam 启动日志中实际使用的 Proton 路径
grep "compatibilitytools.d" ~/.steam/debian-installation/logs/console_log.txt | tail -5
```
如果版本文件与你预期游戏应使用的 Proton 版本不一致，说明前缀已被"升级"。

## 3. 安全重建前缀（保留存档）

如果前缀已损坏且明确是版本冲突所致，可以重建。**注意：此操作会丢失容器内安装的额外运行时（如 vcrun、字体等），重建后需要重新配置。**

```bash
# 1. 备份存档
# 存档通常位于 pfx/drive_c/users/steamuser/Documents/ 下与游戏名相关的目录
find ~/.steam/debian-installation/steamapps/compatdata/<appid>/pfx/drive_c/users/steamuser/Documents/ -maxdepth 2 -type d
cp -r <找到的存档目录> /tmp/game_save_backup/

# 2. 删除损坏的前缀
rm -rf ~/.steam/debian-installation/steamapps/compatdata/<appid>/pfx/

# 3. 用正确的 Proton 版本首次启动游戏（重建前缀）
# 在 Steam 客户端中启动，或命令行：
export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.steam/debian-installation"
export STEAM_COMPAT_DATA_PATH="$HOME/.steam/debian-installation/steamapps/compatdata/<appid>"
~/.steam/debian-installation/compatibilitytools.d/<目标Proton版本>/proton run "<游戏exe绝对路径>"

# 4. 重新配置字体和区域注册表（按 font_troubleshooting.md 和 registry_recovery.md）

# 5. 恢复存档
cp -r /tmp/game_save_backup/* "<pfx/drive_c/users/steamuser/Documents/游戏存档目录/>"
```

## 4. 多个游戏同时无法启动：检查批量兼容层变更

如果是一次性大量游戏出问题，很可能是某次批量操作（如重新添加非 Steam 游戏脚本、或一次性在 Steam 中修改了多个游戏的属性）把它们的兼容层统一设为了某个版本，覆盖了原先各自正常工作的版本。

**快速排查**：列出所有非 Steam 游戏前缀的 Proton 版本：
```bash
for dir in ~/.steam/debian-installation/steamapps/compatdata/*/; do
    appid=$(basename "$dir")
    [ "$appid" = "0" ] && continue
    [ -f "$dir/version" ] && echo "AppID $appid: $(cat "$dir/version")"
done
```
观察版本分布：如果大多数正常工作的游戏用 `9.0-203`，而出问题的全是 `GE-Proton9-27`（或反过来），说明批量添加脚本把兼容层设错了。

**修复**：对每个出问题的游戏，在 Steam 客户端中手动将兼容层改回它原先正常使用的版本，然后按第 3 步重建前缀。
