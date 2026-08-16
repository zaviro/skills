#!/usr/bin/env python3
import sys
import os
import struct
import argparse

parser = argparse.ArgumentParser(description="只读检索 Steam 快捷方式以提取非 Steam 游戏的 AppID。")
parser.add_argument("--name", required=True, help="游戏在 Steam 中的名称")
args = parser.parse_args()

steam_dir = os.path.expanduser("~/.steam/debian-installation")
if not os.path.exists(steam_dir):
    steam_dir = os.path.expanduser("~/.steam/steam")
if not os.path.exists(steam_dir):
    print("错误: 找不到 Steam 安装目录！")
    sys.exit(1)

userdata_dir = os.path.join(steam_dir, "userdata")
shortcuts_paths = []
if os.path.exists(userdata_dir):
    for user_id in os.listdir(userdata_dir):
        vdf_path = os.path.join(userdata_dir, user_id, "config/shortcuts.vdf")
        if os.path.exists(vdf_path):
            shortcuts_paths.append(vdf_path)

if not shortcuts_paths:
    print("错误: 找不到 shortcuts.vdf！请确认您登录过 Steam。")
    sys.exit(1)

def parse_binary_vdf(data):
    pos = 0
    length = len(data)
    
    def read_string():
        nonlocal pos
        start = pos
        while pos < length and data[pos] != 0:
            pos += 1
        s = data[start:pos]
        pos += 1
        return s.decode('utf-8', errors='replace')

    def parse_dict():
        nonlocal pos
        res = {}
        while pos < length:
            t = data[pos]
            pos += 1
            if t == 8:
                break
            key = read_string()
            if t == 0:
                res[key] = parse_dict()
            elif t == 1:
                res[key] = read_string()
            elif t == 2:
                val = struct.unpack('<I', data[pos:pos+4])[0]
                pos += 4
                res[key] = val
        return res

    if len(data) > 0 and data[0] == 0:
        pos = 1
        root_key = read_string()
        if root_key == "shortcuts":
            return parse_dict()
    return {}

found = False
for path in shortcuts_paths:
    try:
        with open(path, "rb") as f:
            shortcuts = parse_binary_vdf(f.read())
        for k, v in shortcuts.items():
            app_name = v.get("AppName", "")
            if args.name.lower() in app_name.lower():
                print(f"找到匹配游戏: {app_name}")
                print(f"AppID: {v.get('appid')}")
                launch_options = v.get("LaunchOptions", "")
                print(f"Steam 启动项: {launch_options or '(空)'}")
                found = True
    except Exception as e:
        print(f"读取 {path} 失败: {e}", file=sys.stderr)

if not found:
    print(f"未能在快捷方式中找到游戏: {args.name}")
    sys.exit(1)
