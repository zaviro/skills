# Proton 游戏字体排障指南

若用户反馈游戏“字形时大时小”、“字体发虚”或“排版错乱”，或者直接由于老旧引擎（如 Caramel Box、Leaf 等）无法识别中文路径而弹窗报错，按以下步骤处理：

## 1. 英文更名规范
若游戏子目录含有中文字符，强烈建议先将游戏根目录重命名为**纯英文名**（例如：`mv "$HOME/games/少女爱上姐姐" "$HOME/games/otoboku"`），以根治老游戏引擎的 ANSI 代码页字符转换失败问题。

## 2. 下载或部署高清微软字体
在纯英文的游戏目录下，通过 `curl` 下载并部署高清微软雅黑字体，并重命名为 `default.ttf`：
```bash
curl -L -o "$HOME/games/<game-subdir>/default.ttf" "https://raw.githubusercontent.com/MeowLove/CentOS-One-click-Installation-of-Desktop-Environment-and-Remote-Desktop-Connection-RDP/master/download/ttf/msyh.ttc"
```

## 3. 重定向容器内字体链接
删除容器下 `pfx/drive_c/windows/Fonts/` 默认的虚拟字体，软链接到下载好的高清字体：
```bash
FONT_DIR="$HOME/.steam/debian-installation/steamapps/compatdata/<appid>/pfx/drive_c/windows/Fonts"
REAL_FONT="$HOME/games/<game-subdir>/default.ttf"
rm -f "$FONT_DIR/msyh.ttf" "$FONT_DIR/msyh.ttc" "$FONT_DIR/simsun.ttc" "$FONT_DIR/msgothic.ttc"
ln -sf "$REAL_FONT" "$FONT_DIR/msyh.ttf"
ln -sf "$REAL_FONT" "$FONT_DIR/msyh.ttc"
ln -sf "$REAL_FONT" "$FONT_DIR/simsun.ttc"
ln -sf "$REAL_FONT" "$FONT_DIR/msgothic.ttc"
```
