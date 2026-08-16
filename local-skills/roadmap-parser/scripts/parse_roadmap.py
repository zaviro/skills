#!/usr/bin/env python3
import sys
import re
import json
import urllib.request
import math

# 中英文映射字典，常见后端、前端、运维及计算机基础词汇翻译，以提升中文输出友好度
TRANSLATION_MAP = {
    # Linux & Operating System Basics
    "Navigation Basics": "命令行导航基础",
    "Basic Commands": "基础导航命令",
    "Moving Files / Directories": "移动文件/目录",
    "Creating & Deleting Files / Dirs": "创建与删除文件/目录",
    "Directory Hierarchy Overview": "文件系统目录层级概览",
    "Editing Files": "文件编辑",
    "Vim / Neovim": "Vim/Neovim 编辑器",
    "Nano": "Nano 编辑器",
    "Emacs": "Emacs 编辑器",
    "Shell and Other Basics": "Shell 及其他基础",
    "Command Path": "命令执行路径",
    "Environment Variables": "环境变量",
    "Command Help": "命令帮助信息",
    "Redirects": "输入输出重定向",
    "Super User": "超级用户权限管理",
    "Working with Files": "文件操作",
    "File Permissions": "文件权限与所有权",
    "Archiving and Compressing": "归档与压缩",
    "Copying and Renaming": "复制与重命名/移动",
    "Soft Links / Hard Links": "软链接与硬链接",
    "Text Processing": "文本处理",
    "stdout / stdin / stderr": "标准输入/输出/错误流",
    "pipe": "管道操作符",
    "tee": "双向重定向",
    "nl": "计算并输出文件行号",
    "wc": "字数与行数统计",
    "cut": "按列切分文本",
    "paste": "合并多文件行",
    "join": "按共有字段合并文件",
    "split": "大文件切分",
    "sort": "文本行排序",
    "uniq": "文本去重",
    "head": "查看文件开头内容",
    "tail": "查看文件结尾内容/动态追踪",
    "tr": "字符替换与翻译",
    "expand / unexpand": "制表符与空格转换",
    "grep": "文件搜索与文本过滤",
    "awk": "流式文本处理语言",
    "sed": "流编辑器/正则替换",
    "Process Management": "进程管理",
    "Background / Foreground Processes": "前台与后台进程管理",
    "Listing / Finding Processes": "进程列表与查找",
    "Process Signals": "进程控制信号",
    "Killing Processes": "进程的强行终止",
    "Process Priorities": "进程优先级配置",
    "Process Forking": "进程分叉与子进程机制",
    "Server Review": "服务器监控与概览",
    "Uptime and Load": "系统运行时间与负载",
    "Authentication Logs": "安全与登录日志分析",
    "Services Running": "运行中的服务列表",
    "Available Memory / Disk": "内存与磁盘空间监控",
    "User Management": "用户管理",
    "Create / Delete / Update": "用户账户管理",
    "Users and Groups": "用户与用户组管理",
    "Managing Permissions": "用户权限分配",
    "Service Management (systemd)": "服务管理 - systemd",
    "Creating New Services": "编写自定义 Service",
    "Checking Service Logs": "检索与诊断服务日志",
    "Starting / Stopping Services": "服务的启动、停止与自启",
    "Checking Service Status": "服务运行状态诊断",
    "Package Management": "包管理器",
    "Package Repositories": "配置与管理软件源",
    "Finding & Installing Packages": "软件包搜索与安装",
    "Listing Installed Packages": "列出已安装软件包",
    "Install / Remove / Upgrade Packages": "软件包安装、卸载与升级",
    "Snap / Flatpak": "沙箱化包管理工具",
    "Disks and Filesystems": "磁盘与文件系统",
    "Inodes": "索引节点",
    "Filesystems": "文件系统类型",
    "Swap": "交换分区管理",
    "Mounts": "磁盘挂载与卸载",
    "Adding Disks": "增加磁盘与分区划分",
    "LVM": "逻辑卷管理器",
    "Booting Linux": "系统启动流程",
    "Boot Loaders": "引导装载程序",
    "Logs": "开机日志",
    "Networking": "网络管理",
    "TCP/IP Stack": "TCP/IP 协议栈",
    "Subnetting": "子网划分",
    "Ethernet & arp/rarp": "以太网与 ARP/RARP 协议",
    "DHCP": "动态主机配置协议",
    "IP Routing": "IP 路由",
    "DNS Resolution": "DNS 域名解析",
    "Netfilter": "防火墙机制/过滤",
    "SSH": "安全外壳协议",
    "File Transfer": "网络文件传输",
    "Shell Programming": "Shell 编程/脚本",
    "Literals": "字面量",
    "Variables": "变量定义",
    "Loops": "循环控制语句",
    "Conditionals": "条件判断语句",
    "Debugging": "脚本调试",
    "Troubleshooting": "故障排查",
    "ICMP": "网际控制报文协议",
    "ping": "网络连通性测试",
    "traceroute": "路由路径追踪",
    "netstat / ss": "网络连接状态查看",
    "Packet Analysis": "数据包拦截与分析",
    "Containerization": "容器化基础",
    "ulimits": "系统资源使用限制",
    "cgroups": "控制组机制",
    "Container Runtime": "容器运行时",
    "Docker": "Docker 容器引擎",

    # Backend General
    "Introduction": "后端介绍/互联网基础",
    "Frontend Basics": "前端基础",
    "Pick a Backend Language": "选择一门后端语言",
    "Version Control Systems": "版本控制系统",
    "Repo Hosting Services": "代码托管服务",
    "Relational Databases": "关系型数据库",
    "Learn about APIs": "API 基础知识",
    "Caching": "缓存",
    "Learn the Basics": "安全与系统基础",
    "Learn about Web Servers": "Web 服务器",
    "AI Assisted Coding": "AI 辅助编码",
    "Applications": "AI 编码应用",
    "Integration Patterns": "AI 集成模式",
    "CI / CD": "持续集成与持续部署",
    "More about Databases": "数据库高级知识",
    "Testing": "测试",
    "Message Brokers": "消息代理",
    "Search Engines": "搜索引擎",
    "Architectural Patterns": "架构模式",
    "Real-Time Data": "实时数据通信",
    "Scaling Databases": "数据库扩容/缩容",
    "NoSQL Databases": "NoSQL 数据库",
    "Building For Scale": "构建高并发与高可用系统",
}

def translate(text):
    if not text:
        return ""
    stripped = text.strip()
    return TRANSLATION_MAP.get(stripped, stripped)

def decode_devalue(data_list):
    """
    解码 React Router / Remix stream 中 devalue/turbo-stream 格式的数组。
    """
    resolved_cache = {}

    def resolve(val):
        if isinstance(val, int):
            if val < 0:
                return None
            if val in resolved_cache:
                return resolved_cache[val]
            if val >= len(data_list):
                return f"OUT_OF_BOUNDS_{val}"
            
            target = data_list[val]
            resolved_cache[val] = f"REF_{val}"
            res = resolve_val(target)
            resolved_cache[val] = res
            return res
        else:
            return resolve_val(val)

    def resolve_val(target):
        if isinstance(target, dict):
            # 判断是否为被压缩的 devalue 字典格式
            is_devalue_dict = True
            for k in target.keys():
                if not (k.startswith("_") and k[1:].isdigit()):
                    is_devalue_dict = False
                    break
            
            if is_devalue_dict and len(target) > 0:
                obj = {}
                for k, v in target.items():
                    k_idx = int(k[1:])
                    real_key = data_list[k_idx]
                    if not isinstance(real_key, str):
                        real_key = str(real_key)
                    obj[real_key] = resolve(v)
                return obj
            else:
                return {k: resolve(v) for k, v in target.items()}
                
        elif isinstance(target, list):
            return [resolve(x) for x in target]
        else:
            return target

    # 还原根节点数据
    return resolve(0)

def fetch_html_from_url(url):
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def parse_roadmap_html(html_content):
    # 提取 reactRouterContext 脚本
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
    target_script = None
    for s in scripts:
        if "reactRouterContext.streamController.enqueue" in s:
            target_script = s
            break
            
    if not target_script:
        raise ValueError("未在页面中找到 reactRouterContext 流式数据，请确认是否为正确的 roadmap.sh 路径。")
        
    enqueues = re.findall(r'enqueue\((.*?)\);', target_script)
    if not enqueues:
        raise ValueError("未能提取出 streamController.enqueue 数据。")
        
    eq = enqueues[0]
    if eq.startswith('"') and eq.endswith('"'):
        decoded = json.loads(eq)
        data_list = json.loads(decoded)
    else:
        # 如果格式不是被双引号包裹的转义字符串，直接解析
        data_list = json.loads(eq)
        
    # 解码 devalue
    decoded_root = decode_devalue(data_list)
    
    # 获取 roadmap 节点
    loader_data = decoded_root.get("loaderData", {})
    if not loader_data:
        raise ValueError("未找到 loaderData。")
        
    route_key = list(loader_data.keys())[0]
    roadmap_data = loader_data[route_key].get("roadmap", {})
    return roadmap_data

def generate_text_roadmap(roadmap_data):
    nodes = roadmap_data.get("nodes", [])
    
    topics = [n for n in nodes if n.get("type") == "topic"]
    subtopics = [n for n in nodes if n.get("type") == "subtopic"]
    
    # 按照 Y 坐标排序主线 topic 节点
    topics.sort(key=lambda x: x.get("position", {}).get("y", 0))
    
    # 建立映射分类
    classification = {t["id"]: [] for t in topics}
    
    # 归属划分算法：对每个 subtopic 节点，寻找距离最近的 topic
    for s in subtopics:
        sx = s.get("position", {}).get("x", 0)
        sy = s.get("position", {}).get("y", 0)
        
        min_dist = float('inf')
        best_t = None
        
        for t in topics:
            tx = t.get("position", {}).get("x", 0)
            ty = t.get("position", {}).get("y", 0)
            
            # 使用改进的加权距离算法（Y轴距离权重更高，以贴合网格分栏规律）
            dist = math.sqrt((sx - tx)**2 + 4 * (sy - ty)**2)
            if dist < min_dist:
                min_dist = dist
                best_t = t
                
        if best_t:
            classification[best_t["id"]].append(s)
            
    # 组装输出文本
    output_lines = []
    
    # 1. 给出带有数字标识的主线节点
    output_lines.append("### 一、 带有数字标识的主线节点\n")
    for idx, t in enumerate(topics, 1):
        t_label = t.get("data", {}).get("label", "")
        zh_label = translate(t_label)
        if zh_label != t_label:
            output_lines.append(f"{idx}. **{t_label}** ({zh_label})")
        else:
            output_lines.append(f"{idx}. **{t_label}**")
            
    output_lines.append("\n---\n")
    
    # 2. 依次给出每个节点对应的分支节点
    output_lines.append("### 二、 每个主线节点对应的分支节点\n")
    for idx, t in enumerate(topics, 1):
        t_label = t.get("data", {}).get("label", "")
        zh_label = translate(t_label)
        
        title = f"**{t_label}** ({zh_label})" if zh_label != t_label else f"**{t_label}**"
        output_lines.append(f"#### {idx}. {title}")
        
        s_list = classification[t["id"]]
        # 按 Y 坐标排序分支节点，保持合理的阅读流向
        s_list.sort(key=lambda x: x.get("position", {}).get("y", 0))
        
        if not s_list:
            output_lines.append("*(暂无细分分支节点)*")
        else:
            for s in s_list:
                s_label = s.get("data", {}).get("label", "")
                zh_s_label = translate(s_label)
                s_title = f"{s_label} ({zh_s_label})" if zh_s_label != s_label else s_label
                output_lines.append(f"*   {s_title}")
        output_lines.append("") # 空行
        
    return "\n".join(output_lines)

def main():
    if len(sys.argv) < 2:
        print("使用说明: python3 parse_roadmap.py <slug_or_url_or_filepath>")
        print("示例:")
        print("  python3 parse_roadmap.py backend")
        print("  python3 parse_roadmap.py https://roadmap.sh/linux")
        print("  python3 parse_roadmap.py /path/to/downloaded.html")
        sys.exit(1)
        
    target = sys.argv[1]
    
    # 判断输入类型
    if target.startswith("http://") or target.startswith("https://"):
        print(f"正在从 URL 抓取数据: {target} ...", file=sys.stderr)
        html = fetch_html_from_url(target)
    elif target.endswith(".html") or target.endswith(".md") or "/" in target or "\\" in target:
        print(f"正在从本地文件读取: {target} ...", file=sys.stderr)
        with open(target, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        # 视作 slug
        url = f"https://roadmap.sh/{target}"
        print(f"正在将 '{target}' 视作 slug 请求: {url} ...", file=sys.stderr)
        html = fetch_html_from_url(url)
        
    try:
        roadmap_data = parse_roadmap_html(html)
        result_text = generate_text_roadmap(roadmap_data)
        print(result_text)
    except Exception as e:
        print(f"解析出错: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
