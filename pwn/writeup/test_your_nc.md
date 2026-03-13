# test_your_nc

## 题目说明

这是一道入门级 pwn 签到题，核心是会使用 `nc` 连接远程靶机并进行基础命令交互。
连接后可直接在根目录看到 `flag` 文件，读取即可拿到答案。

## 解题步骤

1. 使用 `nc` 连接远程服务。

```bash
nc node5.buuoj.cn 29500
```

2. 查看当前目录文件。

```bash
ls
```

示例交互如下：

```text
daydream@dayDReam:~$ nc node5.buuoj.cn 29500
ls
bin
boot
dev
etc
flag
home
lib
lib32
lib64
media
mnt
opt
proc
pwn
root
run
sbin
srv
sys
tmp
usr
var
```

3. 读取 `flag` 文件。

```bash
cat flag
```

## 总结

本题没有利用点，重点在于熟悉远程交互和基础命令：

- `nc`：连接远程服务
- `ls`：查看文件
- `cat`：读取目标文件