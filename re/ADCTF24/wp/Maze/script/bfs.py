#!/usr/bin/env python3
"""
CTF Maze Solver (pruned DFS)
- maze.bin 结构：连续 5 字节条目 (char + int32 offset)
- 必须刚好走 44 步并精确落到终点
- 使用反向可达性剪枝，只走能到达终点的边
- 找到 MD5 匹配的路径后，反转再 MD5 得到 flag
"""

import struct
import hashlib
from collections import defaultdict, deque

MAZE_FILE = "/home/workdir/attachments/maze.bin"
START     = 0x144DC
END       = 0x1FFFF
MAX_LEN   = 44
TARGET_MD5 = "d69239ff8691e48e2a4d7497a7fb9dbb"


def load_maze(path):
    with open(path, "rb") as f:
        return f.read()


def get_options(data, pos):
    """返回当前位置所有 (char, next_pos) 选项"""
    opts = []
    p = pos
    while p < len(data) and data[p] != 0:
        ch = data[p]
        offset = struct.unpack_from("<i", data, p + 1)[0]
        next_pos = p + offset
        if 0 <= next_pos < len(data):
            opts.append((ch, next_pos))
        p += 5
    return opts


def build_can_reach(data):
    """反向 DP：can[r] = 还能刚好走 r 步到达终点的位置集合"""
    rev = defaultdict(list)
    visited = set([START])
    q = deque([START])
    while q:
        pos = q.popleft()
        for _, np in get_options(data, pos):
            rev[np].append(pos)
            if np not in visited:
                visited.add(np)
                q.append(np)

    can = [set() for _ in range(MAX_LEN + 1)]
    can[0].add(END)
    for r in range(1, MAX_LEN + 1):
        for pos in can[r - 1]:
            for prev in rev[pos]:
                can[r].add(prev)
    return can


def solve(data):
    can = build_can_reach(data)
    assert START in can[MAX_LEN], "起点不可达终点，数据有问题"

    # 预计算所有有用位置的 options
    options = {}
    all_useful = set()
    for s in can:
        all_useful |= s
    for pos in all_useful:
        options[pos] = get_options(data, pos)

    # 迭代 DFS + 剪枝
    # 栈里同时保存当前步要写入的字符，避免兄弟节点互相覆盖 path
    path = bytearray(MAX_LEN)
    stack = [(START, 0, 0)]       # (pos, depth, char_to_write)

    checked = 0
    while stack:
        pos, depth, ch = stack.pop()
        if depth > 0:
            path[depth - 1] = ch

        if depth == MAX_LEN:
            if pos == END:
                checked += 1
                if hashlib.md5(path).hexdigest() == TARGET_MD5:
                    return bytes(path), checked
            continue

        rem = MAX_LEN - depth
        children = [(np, ch) for ch, np in options.get(pos, []) if np in can[rem - 1]]
        for np, ch in reversed(children):
            stack.append((np, depth + 1, ch))

    return None, checked


def main():
    data = load_maze(MAZE_FILE)
    print(f"[*] maze size = {len(data)}")
    print(f"[*] start = 0x{START:x}, end = 0x{END:x}")
    print("[*] searching with reachability pruning ...")

    path, checked = solve(data)

    if path is None:
        print(f"[-] not found (checked {checked} leaves)")
        return

    print(f"[+] found after checking {checked} paths")
    print(f"[+] path = {path}")
    print(f"[+] path (ascii) = {path.decode('latin1')}")
    print(f"[+] md5(path)   = {hashlib.md5(path).hexdigest()}")

    rev = path[::-1]
    flag_md5 = hashlib.md5(rev).hexdigest()
    print(f"[+] reversed    = {rev}")
    print(f"[+] flag        = flag{{{flag_md5}}}")


if __name__ == "__main__":
    main()