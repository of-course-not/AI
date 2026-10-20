# 网络设备配置与管理 · 实验二（ACL 与 NAT）Packet Tracer 8.2.2 新手教程

> 本教程对应 `实验2\05-原始资料\实验2题目要求.png` 里的两个小实验，全部在 **Cisco Packet Tracer 8.2.2** 里完成。
> 配套文件：实验报告 `实验2\01-实验报告\90-实验二-ACL与NAT配置-实验报告.docx`；两个现成工程
> `实验2\03-工程文件\90-实验二一-ACL配置.pkt`、`90-实验二二-NAT配置.pkt`；配图在 `实验2\06-图表与截图\`。
>
> 学号后两位按 **90** 计算。如果你不是 90，把所有 `192.168.90.x` 里的 `90`、`200.0.90.x` 里的 `90`
> 换成你自己的两位数即可（后文第 4 章有替换规则）。

---

## 目录

- [0. 读前须知：这个实验到底有几个小实验](#0-读前须知这个实验到底有几个小实验)
- [1. 环境准备与界面速览](#1-环境准备与界面速览)
- [2. 命名规范（照做，报告和工程都不会乱）](#2-命名规范照做报告和工程都不会乱)
- [3. 通用基本功：三层交换机、ACL、NAT](#3-通用基本功三层交换机aclnat)
- [4. 地址规划总表](#4-地址规划总表)
- [5. 实验（一）ACL 的配置：从零搭到能验证](#5-实验一acl-的配置从零搭到能验证)
- [6. 实验（二）NAT 的配置：从零搭到能验证](#6-实验二nat-的配置从零搭到能验证)
- [7. 报告怎么写](#7-报告怎么写)
- [8. 自检清单（做完逐条打勾）](#8-自检清单做完逐条打勾)
- [9. 故障排查速查表](#9-故障排查速查表)
- [10. 附录：四台关键设备的完整配置](#10-附录四台关键设备的完整配置)
- [结尾：做完了怎么交付](#结尾做完了怎么交付)

---

## 0. 读前须知：这个实验到底有几个小实验

题目看起来一大段，实际上是 **两个互相独立的小实验**，各建一个 `.pkt` 工程：

| 序号 | 小实验 | 核心知识点 | 建议学时 | 工程文件名 |
|------|--------|-----------|---------|-----------|
| 实验（一） | **ACL 的配置** | VLAN 划分、三层交换机 SVI 间路由、静态路由、**标准/扩展 ACL** 的四要素过滤 | 3~4 h | `90-实验二一-ACL配置.pkt` |
| 实验（二） | **NAT 的配置** | 与（一）相同的内网结构 + **动态 NAT（地址池）** + **静态 PAT（端口映射）** | 3~4 h | `90-实验二二-NAT配置.pkt` |

两个实验的**内网部分完全一样**（同样的三台 PC 教师、三台学生 PC、两台服务器交换机、一个核心三层交换机），
区别只在出口：

- 实验（一）出口是 `Router0 → Router1`，`Router1` 上用 `Loopback0` 模拟 Internet 上的一台主机，
  然后靠 ACL 控制「谁能访问谁」。
- 实验（二）出口是 `NAT路由器 → Internet路由器 → 外网网络`，`外网网络` 下挂一台外网用户和一台外网服务器，
  然后靠 NAT 把内网地址翻译成公网地址。

**建议顺序**：先做（一），因为它把 VLAN、SVI、静态路由这三样基础全练一遍；
（二）的内网部分可以直接把（一）的核心交换机配置照抄过去，只改出口。

### 0.1 题目要求逐条拆解

**（一）ACL 的四条需求**（题目第 4 条）：

| 编号 | 需求原文 | 用哪张 ACL 实现 | 挂在哪 |
|------|---------|----------------|--------|
| 需求 1 | 服务器属于内部服务器，不可以访问 Internet | ACL 130（拒绝 192.168.90.128/26 → 200.0.90.0/24） | `interface Vlan4` **in** |
| 需求 2 | 学生只能访问 server0 的 web 服务 | ACL 120（只放行到 .138 的 tcp 80，其余到服务器网段的全部拒绝） | `interface Vlan3` **in** |
| 需求 3 | 所有服务器都不允许被 ping | ACL 110 第 3 条（`deny icmp any 192.168.90.128 0.0.0.63 echo`） | `interface Vlan4` **out** |
| 需求 4 | 教师可以访问所有 server，但只有 teacher1 可以 Telnet 到 server0—server2 | ACL 110 第 1、2 条（只 permit host .10 的 tcp 23，其余 tcp 23 全拒） | `interface Vlan4` **out** |

> 题目说「请利用**标准或扩展**访问控制列表完成」。标准 ACL（1—99）只能看**源地址**，
> 做不了「学生只能访问 server0 的 **web 服务**」这种带协议和端口的判断，
> 所以四条需求必须用**扩展 ACL**（100—199）。报告里要明确写这句话，这是评分点。

**（二）NAT 的两条需求**（题目第 4 条）：

| 编号 | 需求原文 | 实现方式 |
|------|---------|---------|
| 需求 5 | teacher 和 stu 用户均通过**动态 NAT** 实现 Internet 上外部服务器的访问 | `ip nat pool` + `access-list 1` + `ip nat inside source list 1 pool PUB` |
| 需求 6 | Web 服务器采用**静态 PAT** 将其 80 端口映射到公有 IP 的 80 端口 | `ip nat inside source static tcp 192.168.90.138 80 200.0.90.30 80` |

> 注意需求 5 说的是「动态 NAT」不是「NAPT」。区别只在一个 `overload` 关键字：
> 不加 `overload` 是「一个内网 IP 占一个公网 IP」，池子用完就失败；
> 加了 `overload` 才是端口复用。本题按字面写**不加 overload**，报告里说明这个差别是加分项。

### 0.2 时间预算

| 阶段 | 内容 | 时间 |
|------|------|------|
| 准备 | 装 PT、认界面、记命名规范 | 20 min |
| 实验（一） | 搭拓扑 15 min + 配内网 40 min + 配出口 20 min + 写 ACL 30 min + 测试 30 min | 2.5 h |
| 实验（二） | 复制内网 20 min + 配 NAT 30 min + 配外网 20 min + 测试 30 min | 1.5 h |
| 报告 | 填模板、贴截图、写结论 | 1.5 h |
| **合计** | | **约 6 h** |

---

## 1. 环境准备与界面速览

### 1.1 软件

| 项目 | 值 |
|------|-----|
| 软件 | Cisco Packet Tracer 8.2.2（本机实测版本号 `8.2.0.0162`） |
| 安装路径（本机） | `E:\Cisco Packet Tracer 8.2.2\` |
| 可执行文件 | `E:\Cisco Packet Tracer 8.2.2\bin\PacketTracer.exe` |
| 文档 | Microsoft Word / WPS（写报告用） |

> 为什么强调 8.2.2？因为不同版本的**设备型号清单不一样**。
> 8.2.2 的路由器只有 13 种：ISR4321 / ISR4331 / 1941 / 2901 / 2911 / 819 / 829 / CGR1240 /
> Router-PT / 1841 / 2620XM / 2621XM / 2811。**没有 2501、没有 2600**，
> 所以老教材上的 2501 拓扑不能照抄（这是实验一遇到过的问题，实验二不涉及）。

### 1.2 本实验要用的设备（都在设备面板里能直接拖）

| 设备 | 在面板的位置 | 本实验用几台 | 说明 |
|------|------------|------------|------|
| **3560-24PS** | Switches → 第 4 个（多层交换机图标带太阳花） | 1 | 核心交换机，唯一的三层交换机 |
| **2960-24TT** | Switches → 第 1 个 | 2（实验一）/ 3（实验二） | 接入交换机，二层 |
| **1841** | Routers → 第 10 个左右 | 2 | 出口路由器，**要加 WIC-2T 才有 Serial 口** |
| **PC-PT** | End Devices → 第 1 个 | 6（教师 3 + 学生 3） | 终端 |
| **Server-PT** | End Devices → 第 3 个（机架式图标） | 3（实验一）/ 2（实验二） | 服务器，自带 HTTP 服务 |

> **怎么快速找到某个型号**：设备面板底部有一排分类图标（Routers、Switches、End Devices…），
> 点进去后把鼠标悬停在设备上会显示型号名。也可以点面板右下角的「设备类型」筛选框直接输入型号。

### 1.3 连线类型对照（拖错线是最常见的低级错误）

| 连接的两端 | 用哪种线 | 在 PT 里的名字 | 线缆颜色 |
|-----------|---------|---------------|---------|
| PC ↔ 交换机 | 直通线 | Copper Straight-Through | 黑色实线 |
| 交换机 ↔ 交换机（不同型号/不同层） | 交叉线 | Copper Cross-Over | 黑色虚线 |
| 交换机 ↔ 路由器 | 直通线 | Copper Straight-Through | 黑色实线 |
| 路由器 ↔ 路由器（串口） | 串行线 | Serial DTE | **红色折线** |
| PC ↔ 路由器/交换机的 Console 口 | 反转线 | Console（浅蓝） | 浅蓝细线 |

> 本实验的所有以太网连线都是「终端/路由器 ↔ 交换机」，所以**全部用直通线**。
> 路由器之间用 **Serial DTE**（红色折线），一端会自动带小时钟图标，那是 DCE 端。

### 1.4 界面速览

打开 PT 后你会看到四个区域：

1. **顶部菜单栏**：File（文件）、Edit（编辑）、Options（选项）、View（视图）、Tools（工具）、
   Extensions（扩展）、Window、Help。汉化版会显示中文。
2. **工具栏**：新建、打开、保存、打印、活动向导、**选择工具（箭头）**、**检查工具（放大镜）**、
   **删除工具（叉）**、**绘图工具（方框/椭圆/直线/铅笔）**、**便签工具（信封图标）**。
3. **逻辑工作区（大白板）**：拖设备、连线都在这。
4. **底部设备面板**：左边是分类，右边是该类下的具体型号。
   面板右下角还有「Scenario 0」下拉框（本实验用不到）和 PDU 列表。

> **一个新手 90% 会踩的坑**：拖完设备后忘记切回「选择工具」（箭头），
> 结果点设备没反应，或者点一下就把设备删了。养成习惯：
> **连完线立刻按 Esc，回到选择工具**。

### 1.5 打开一个 `.pkt` 文件的正确姿势

- 双击 `.pkt` 文件，或者在 PT 里 `File → Open`。
- 打开后**标题栏会显示完整路径**，例如
  `Cisco Packet Tracer - E:\...\90-实验二一-ACL配置.pkt`。
  如果标题栏只显示 `Cisco Packet Tracer`（没有路径），说明**文件没加载成功**，
  这时候去点设备是点不动的，别以为是电脑卡了。

---

## 2. 命名规范（照做，报告和工程都不会乱）

命名这件事看起来无所谓，但报告里要贴配置、要写「在 CoreSW 上执行」，
如果设备名是默认的 `Switch0`、`PC1`、`Router2`，读者根本对不上图。
**下面这套命名和题目原文、和本教程的配图、和两个现成 `.pkt` 完全一致，照着改就行。**

### 2.1 设备命名

| 设备类型 | 命名规则 | 本实验的实际设备名 |
|---------|---------|------------------|
| 核心三层交换机 | `CoreSW` | `CoreSW` |
| 接入交换机 | 按它下面挂什么命名 | `student`（挂学生）、`Server`（挂服务器）、`外网网络`（挂外网设备） |
| 出口路由器 | 按角色命名 | 实验（一）：`Router0`、`Router1`；实验（二）：`NAT路由器`、`Internet路由器` |
| 教师 PC | `teacher1`~`teacher3` | 同左 |
| 学生 PC | `stu1`~`stu3` | 同左 |
| 服务器 | `Server0`~`Server2`（实验一）、`web服务器`（实验二） | 同左 |
| 外网终端 | 按角色 | `外网用户`、`外网服务器` |

> **设备名可以是中文**（`外网网络`、`web服务器`），PT 8.2.2 完全支持，报告里也好读。
> 但**接口名、IP 地址不能写中文**。
>
> 改设备名的方法：单击设备 → 弹出窗口 → 顶部「Config」标签 → 第一行 `Display Name` 改成你要的名字。
> 注意这里改的是**画布上显示的名字**，不是路由器的 `hostname`。
> `hostname` 要在 CLI 里敲 `hostname CoreSW`，两处最好改成一样，否则 `show run` 和画布对不上。

### 2.2 接口写法约定

同一个接口在不同场合有不同写法，报告里要统一：

| 场合 | 写法 | 例子 |
|------|------|------|
| PT 的 CLI 里敲命令 | 全称或简写都可以 | `interface fastEthernet 0/2` 或 `int fa0/2` |
| 报告正文/表格里 | **短写**：`Fa0/2`、`Se0/0/0`、`Gi0/1` | `CoreSW Fa0/2` |
| 配图里 | 短写 | `Fa0/2` |

> 三层交换机的 SVI（VLAN 接口）在报告里写成 `SVI Vlan2` 或 `Vlan2`，
> 不要写成 `VLAN2`（大小写不一致，和 `show run` 里的 `interface Vlan2` 对不上）。

### 2.3 IP 地址书写

- 一律写**点分十进制 + 掩码位数**：`192.168.90.1/26`。
- 报告表格里如果要写掩码，用 `255.255.255.192` 而不是 `/26`，因为老师要看到具体掩码。
- **不要**把 `192.168.90.1/26` 写成 `192.168.90.1/255.255.255.192`（这是错的写法）。

### 2.4 工程文件命名

```
90-实验二一-ACL配置.pkt
90-实验二二-NAT配置.pkt
```

规则：`学号后两位-实验序号-内容.pkt`。
中间的「二一」「二二」表示**实验二的第 1 个小实验、第 2 个小实验**，
这样排序时两个文件挨着，不会和实验一的文件混在一起。

### 2.5 截图与图表编号

- 截图存成 `06-图表与截图\` 下的 `fig_xxx.png`。
- 报告里的图按出现顺序编号：图1、图2、图3…，表按 表1、表2…，
  **正文里必须先引用再出现**（写「拓扑如图 1 所示」，然后才是图）。
- 配图宽度统一 `15 cm`（A4 正文宽 19 cm，留点边距），过宽会被 Word 自动缩，反而糊。

---

## 3. 通用基本功：三层交换机、ACL、NAT

这一章是「做实验之前必须先懂的东西」。如果你已经会了，可以直接跳到第 5 章。
但**强烈建议至少把 3.2 和 3.4 看完**，因为 ACL 和 NAT 的坑几乎全在这两节。

### 3.1 3560 是三层交换机，但它默认不开路由

3560-24PS 有 24 个 FastEthernet + 2 个 GigabitEthernet，全部**默认是二层口**
（`switchport` 模式）。要让它在 VLAN 之间路由，必须做三件事：

```text
CoreSW(config)# ip routing                     ! ① 打开路由功能（默认是关的！）
CoreSW(config)# interface vlan 2               ! ② 给每个 VLAN 建一个 SVI，配网关地址
CoreSW(config-if)# ip address 192.168.90.1 255.255.255.192
CoreSW(config-if)# no shutdown
CoreSW(config-if)# exit
CoreSW(config)# interface fastEthernet 0/1     ! ③ 上联路由器的口改成三层口
CoreSW(config-if)# no switchport               !    关键：把二层口变成三层口
CoreSW(config-if)# ip address 192.168.90.193 255.255.255.252
CoreSW(config-if)# no shutdown
```

**三个必须记住的点**：

1. **`ip routing` 不敲，SVI 之间就是不通的**。这是三层交换机最容易忘的一条，
   现象是「`show ip interface brief` 里 SVI 都是 up/up，IP 也对，但 PC ping 不通网关的另一边」。
2. **SVI 要 up，它对应的 VLAN 里必须至少有一个 up 的物理口**。
   如果你配了 `interface Vlan4` 但 Fa0/6（接服务器交换机那个口）还没起来，
   `show ip interface brief` 里 Vlan4 会显示 `down/down`，IP 配了也没用。
3. **`no switchport` 才能配 IP**。在二层口上直接敲 `ip address` 会报
   `% IP addresses may not be configured on L2 links`。

### 3.2 SVI 上的 `in` 和 `out` 到底是什么意思

这是 ACL 挂载最容易搞反的地方。记住一句话：

> **`in` = 从该 VLAN 里的主机「进入」交换机的流量；`out` = 从交换机「发出」到该 VLAN 主机的流量。**

用图 1 的拓扑举例：

| ACL | 挂载位置 | 抓的是哪些包 | 实现的需求 |
|-----|---------|------------|-----------|
| 110 | `interface Vlan4 out` | **发给服务器**的包（任何源 → 服务器网段） | 需求 3「服务器不能被 ping」、需求 4「只允许 teacher1 Telnet」 |
| 120 | `interface Vlan3 in` | **学生发出的**包（学生 → 任何地方） | 需求 2「学生只能访问 server0 的 web」 |
| 130 | `interface Vlan4 in` | **服务器发出的**包（服务器 → 任何地方） | 需求 1「服务器不能访问 Internet」 |

**为什么 110 挂 out 而不是 in？**
「服务器不能被 ping」限制的是**别人发给服务器**的包，从服务器的视角看是「收到的包」，
在 SVI 上就是 `out` 方向（交换机把包发给 VLAN4 的主机）。

**为什么 130 挂 in？**
「服务器不能访问 Internet」限制的是**服务器发出**的包，即 `in` 方向。

> 一句话记忆法：**限制「某网段能访问别人」挂 in；限制「别人能访问某网段」挂 out。**
> 但这句话只在「限制的是该网段自己」时成立，遇到具体题目还是按上表那样一个个推。

### 3.3 扩展 ACL 的语法与通配符掩码

```text
access-list <100-199> <permit|deny> <协议> <源地址> <源通配符> <目的地址> <目的通配符> [eq <端口>]
```

几个必须记住的写法：

| 写法 | 含义 |
|------|------|
| `any` | 任意地址，等价于 `0.0.0.0 255.255.255.255` |
| `host 192.168.90.10` | 单个主机，等价于 `192.168.90.10 0.0.0.0` |
| `192.168.90.64 0.0.0.63` | 匹配 `192.168.90.64/26` 整个网段 |
| `192.168.90.128 0.0.0.63` | 匹配 `192.168.90.128/26` 整个网段 |
| `eq 80` / `eq www` | 端口 80，两种写法 PT 都认，**但 PT 保存后会把 `eq 80` 规范化成 `eq www`** |
| `eq 23` / `eq telnet` | 端口 23，同上，PT 会存成 `eq telnet` |
| `echo` | ICMP 的 echo 请求，就是 ping 用的那个类型 |

**通配符掩码怎么算**：掩码取反。
`255.255.255.192`（/26）→ 取反 → `0.0.0.63`。
再记一个：`/30` → `255.255.255.252` → 取反 `0.0.0.3`。
`/29` → `255.255.255.248` → `0.0.0.7`。`/28` → `255.255.255.240` → `0.0.0.15`。

> **最常见的错误**：把通配符写成子网掩码（写成 `0.0.0.192`）。
> 后果是规则看起来配上了，但匹配范围完全不对，`show access-lists` 里的计数一直是 0。

### 3.4 ACL 的三条铁律

1. **末尾隐含一条 `deny any`**。所以每张 ACL 的最后都要补一条
   `permit ip any any` 兜底，否则「本来能通的流量」也会被悄悄丢掉。
   ——这是新手做完 ACL 后「全网都不通了」的第一大原因。
2. **自上而下逐条匹配，命中即停**。所以 `permit` 和 `deny` 的**顺序决定结果**。
   如果把 `permit ip any any` 写在最前面，后面的规则永远不会被执行。
3. **ACL 只对「穿越」设备的流量生效，对设备自己产生的流量无效**。
   比如你在 CoreSW 上 `ping 192.168.90.10`，这个包是 CoreSW 自己发的，
   `ip access-group` 管不到它。要限制设备自己的流量得用 `access-class`（针对 Telnet）或本地策略。

### 3.5 NAT 的四个组成部分

一个能工作的 NAT 配置，必须有**四样东西**，缺一样 `show ip nat translations` 就是空的：

| 组成 | 命令 | 作用 |
|------|------|------|
| ① inside / outside 划分 | `ip nat inside` / `ip nat outside` | 告诉路由器哪边是内网、哪边是外网 |
| ② 地址池（动态 NAT 才有） | `ip nat pool PUB 200.0.90.17 200.0.90.22 netmask 255.255.255.240` | 可用的公网地址范围 |
| ③ 匹配规则 | `access-list 1 permit 192.168.90.0 0.0.0.255` | 哪些内网地址允许被转换 |
| ④ 绑定 | `ip nat inside source list 1 pool PUB` | 把 ②③ 绑起来 |

**静态 PAT 是另一条独立的语句**，不需要池也不需要 ACL：

```text
ip nat inside source static tcp 192.168.90.138 80 200.0.90.30 80
```

读法是：`tcp` `<内网地址>` `<内网端口>` `<公网地址>` `<公网端口>`。

### 3.6 动态 NAT、NAPT、静态 PAT 三者的区别

| 类型 | 命令特征 | 一个公网 IP 能供几台内网主机 | 谁发起 |
|------|---------|---------------------------|--------|
| 动态 NAT | `ip nat inside source list 1 pool PUB`（**没有** overload） | **1 台** | 内网发起 |
| NAPT / PAT（地址池 + 端口复用） | 同上 + `overload` | 任意多台 | 内网发起 |
| 静态 PAT（端口映射） | `ip nat inside source static tcp ...` | 1 个端口对应 1 台服务器 | **外网发起也能命中** |

> 题目需求 5 说的是「动态 NAT」，所以**不加 overload**。
> 池里有 6 个地址（.17—.22），最多 6 台内网主机同时上网，第 7 台就失败。
> 这个「限制」正好可以在报告里当作实验现象写出来，说明你真的理解了区别。

### 3.7 关于 Telnet 的一个事实（必须知道，否则测试会懵）

**Packet Tracer 的 Server-PT 没有 Telnet 服务端。**
它的 Services 标签里只有 HTTP / HTTPS / DNS / DHCP / TFTP / NTP / Syslog / AAA / Email / FTP / IoT，
**没有 Telnet**。只有 Cisco 的路由器/交换机才有 Telnet 服务端（`line vty 0 4` 那一套）。

所以题目需求 4「只有 teacher1 可以 Telnet 到 server0—server2」在 PT 里的可观测现象是：

| ACL 结果 | PC 上执行 `telnet 192.168.90.138` 的现象 |
|---------|----------------------------------------|
| **被 permit** | 提示 `Connection refused by remote host`（端口通，但没有服务在听） |
| **被 deny** | 一直卡住，最后 `Connection timed out` 或毫无响应 |

两者现象**明显不同**，所以照样能验证 ACL 是否生效。报告里要把这个事实写清楚
（本教程配套的报告已经写了），不要假装「登录进了服务器」。
如果一定要做「真正登录」的 Telnet 验证，把目标换成一台路由器即可：

```text
Router1(config)# line vty 0 4
Router1(config-line)# password cisco
Router1(config-line)# login
Router1(config-line)# exit
Router1(config)# enable secret class
```

---

## 4. 地址规划总表

### 4.1 规划原则

1. **内网全部落在 `192.168.90.0/24` 内**（90 = 学号后两位），满足题目「IP 地址均为 192.168.XX.0/24 的子网」。
2. **公网全部落在 `200.0.90.0/24` 内**，满足题目「公网 IP 均采用 200.0.XX.0/24 的子网」。
3. 每个 VLAN 一个 `/26`（可用 62 个地址，够 3 台终端，留足扩展余地）。
4. 路由器之间点对点用 `/30`（只浪费 2 个地址）。
5. 公网侧：互联用 `/30`，外网 LAN 用 `/29`，NAT 地址池用 `/28`。

### 4.2 内网（两个实验共用）

| VLAN | 用途 | 网络地址/掩码 | 网关（SVI） | 终端地址 |
|------|------|--------------|------------|---------|
| VLAN2 | teacher | `192.168.90.0/26` | `192.168.90.1` | teacher1 `.10`、teacher2 `.11`、teacher3 `.12` |
| VLAN3 | stu | `192.168.90.64/26` | `192.168.90.65` | stu1 `.74`、stu2 `.75`、stu3 `.76` |
| VLAN4 | server | `192.168.90.128/26` | `192.168.90.129` | Server0 `.138`、Server1 `.139`、Server2 `.140`（实验二只有 web服务器 `.138`） |

> **为什么终端从 .10 / .74 / .138 开始而不是 .2？**
> 留出 `.1~.9` 给以后可能加的网关冗余、管理地址；
> 也让「网关」和「主机」在地址上明显分开，报告里一眼能看出谁是网关。

### 4.3 实验（一）ACL 的出口与公网

| 链路 | 网络地址/掩码 | 本端 | 对端 |
|------|--------------|------|------|
| CoreSW Fa0/1 ↔ Router0 Fa0/0 | `192.168.90.192/30` | CoreSW `.193` | Router0 `.194` |
| Router0 Se0/0/0 ↔ Router1 Se0/0/0 | `200.0.90.0/30` | Router0 `.1`（DCE） | Router1 `.2` |
| Router1 Loopback0 | `200.0.90.100/32` | Router1 `.100` | 模拟 Internet 上的一台主机 |

### 4.4 实验（二）NAT 的公网

| 链路 | 网络地址/掩码 | 本端 | 对端 |
|------|--------------|------|------|
| CoreSW Fa0/1 ↔ NAT路由器 Fa0/0 | `192.168.90.192/30` | CoreSW `.193` | NAT路由器 `.194` |
| NAT路由器 Se0/0/0 ↔ Internet路由器 Se0/0/0 | `200.0.90.0/30` | NAT `.1`（DCE） | Internet `.2` |
| Internet路由器 Fa0/0 ↔ 外网网络 | `200.0.90.8/29` | Internet `.9` | 外网服务器 `.10`、外网用户 `.11` |
| NAT 公网地址池 | `200.0.90.16/28` | `.17`—`.22`（6 个，动态 NAT 用） | — |
| 静态 PAT 公网地址 | `200.0.90.30` | 映射到 `192.168.90.138:80` | — |

> **`.30` 为什么单独拿出来？** 因为它落在 `200.0.90.16/28` 里，会被 `Internet路由器` 上那条
> `ip route 200.0.90.16 255.255.255.240 200.0.90.1` 覆盖，回程天然可达，不用再加明细路由。

### 4.5 端口连接表（严格按原图，报告里要贴）

**实验（一）ACL**：

| 设备 | 本端接口 | 对端设备 | 对端接口 | 线型 |
|------|---------|---------|---------|------|
| CoreSW | Fa0/2 | teacher1 | Fa0 | 直通 |
| CoreSW | Fa0/3 | teacher2 | Fa0 | 直通 |
| CoreSW | Fa0/4 | teacher3 | Fa0 | 直通 |
| CoreSW | Fa0/5 | student | Fa0/24 | 直通（Trunk） |
| CoreSW | Fa0/6 | Server | Fa0/24 | 直通（Trunk） |
| CoreSW | Fa0/1 | Router0 | Fa0/0 | 直通（三层口） |
| student | Fa0/1 | stu1 | Fa0 | 直通 |
| student | Fa0/2 | stu2 | Fa0 | 直通 |
| student | Fa0/3 | stu3 | Fa0 | 直通 |
| Server | Fa0/1 | Server0 | Fa0 | 直通 |
| Server | Fa0/2 | Server1 | Fa0 | 直通 |
| Server | Fa0/3 | Server2 | Fa0 | 直通 |
| Router0 | Se0/0/0 | Router1 | Se0/0/0 | Serial DTE |

**实验（二）NAT**：内网 12 条同上（只是 Server 下只挂 `web服务器` 到 `Server` 的 Fa0/1），另外：

| 设备 | 本端接口 | 对端设备 | 对端接口 | 线型 |
|------|---------|---------|---------|------|
| CoreSW | Fa0/1 | NAT路由器 | Fa0/0 | 直通 |
| NAT路由器 | Se0/0/0 | Internet路由器 | Se0/0/0 | Serial DTE |
| Internet路由器 | Fa0/0 | 外网网络 | Fa0/1 | 直通 |
| 外网网络 | Fa0/2 | 外网用户 | Fa0 | 直通 |
| 外网网络 | Fa0/3 | 外网服务器 | Fa0 | 直通 |

> **端口号不是随便挑的**：原图（`实验2图片1.png`、`实验2图片2.png`）上标的端口就是这些，
> 报告里要能一一对上。端口号本身不影响连通性，但「未严格按图连线」是会被扣分的。

### 4.6 换学号怎么改

如果学号后两位不是 90，把所有地址里的 `90` 换成你的数字，例如 37：

| 原地址 | 改成 |
|--------|------|
| `192.168.90.0/26` | `192.168.37.0/26` |
| `200.0.90.0/30` | `200.0.37.0/30` |
| `200.0.90.16/28` | `200.0.37.16/28` |

**其他都不用动**（子网划分方式、主机位、接口编号全部保持不变）。
这样改的好处是：`/26` 的第 4 段是 0/64/128/192，和 `90` 无关，不用重算子网。

---

## 5. 实验（一）ACL 的配置：从零搭到能验证

这一章从「打开 PT、新建空白工程」开始，一步一步做到「四条 ACL 需求全部验证通过」。
每一步都给出**在哪个设备上、敲什么、应该看到什么**。

### 5.1 第一步：新建工程并摆好设备

1. 打开 PT，`File → New`（或者直接 Ctrl+N），得到一个空白工作区。
2. 从底部设备面板拖出下面 13 台设备，按图 1 的位置摆（位置不要求和图一模一样，但**同类设备放在一起**，报告里截图才好看）：

| 数量 | 设备型号 | 改名为 |
|------|---------|--------|
| 1 | 3560-24PS | `CoreSW` |
| 2 | 2960-24TT | `student`、`Server` |
| 2 | 1841 | `Router0`、`Router1` |
| 6 | PC-PT | `teacher1`、`teacher2`、`teacher3`、`stu1`、`stu2`、`stu3` |
| 3 | Server-PT | `Server0`、`Server1`、`Server2` |

> **改名方法**：单击设备 → 弹窗 → `Config` 标签 → `Display Name`。
> 改完记得点一下别的地方，让名字生效。

3. **给两台 1841 加串口模块**（不加就没有 `Serial0/0/0`，后面串行线连不上）：

   - 单击 `Router0` → 弹窗顶部切到 **`Physical`（物理的）** 标签。
   - **先点一下设备面板上的电源开关图标**（左下角那个圆形按钮），让设备断电（绿色变灰）。
   - 在左侧「模块」列表里选 `WIC-2T`，按住拖到设备图上标着 `WIC` 的空槽里。
   - 再点一次电源开关，通电。
   - 对 `Router1` 重复一遍。

   > **不断电直接插模块**：PT 会提示 `Module cannot be added while the device is on`，
   > 或者插进去不生效。这一步必须断电。

4. 保存：`File → Save`，文件名 `90-实验二一-ACL配置.pkt`，存到 `实验2\03-工程文件\`。

### 5.2 第二步：连线（严格按 4.5 的表）

1. 点底部面板的 **闪电图标**（Connections）。
2. 选 **Copper Straight-Through**（黑色实线）。
3. 依次点两端设备的接口，PT 会自动弹出接口列表让你选：

| 从 | 到 |
|----|----|
| CoreSW Fa0/2 | teacher1 Fa0 |
| CoreSW Fa0/3 | teacher2 Fa0 |
| CoreSW Fa0/4 | teacher3 Fa0 |
| CoreSW Fa0/5 | student Fa0/24 |
| CoreSW Fa0/6 | Server Fa0/24 |
| CoreSW Fa0/1 | Router0 Fa0/0 |
| student Fa0/1 | stu1 Fa0 |
| student Fa0/2 | stu2 Fa0 |
| student Fa0/3 | stu3 Fa0 |
| Server Fa0/1 | Server0 Fa0 |
| Server Fa0/2 | Server1 Fa0 |
| Server Fa0/3 | Server2 Fa0 |

4. 换成 **Serial DTE**（红色折线），连 `Router0 Se0/0/0 ↔ Router1 Se0/0/0`。
   连完后 `Router0` 那端会出现一个**小时钟图标**，说明它是 DCE 端，需要在它上面配 `clock rate`。

5. 连完按 `Esc` 回到选择工具。**此时所有链路的端点应该是绿色小三角**（表示 up）。
   如果是红色或橙色，说明接口还没起来，先做下一步。

### 5.3 第三步：配 CoreSW（核心，最重要的一台）

双击 `CoreSW` → `CLI` 标签 → 敲回车出现 `Switch>`。

```text
Switch> enable
Switch# configure terminal
Switch(config)# hostname CoreSW

! ① 打开路由功能（3560 默认是二层，必须开）
CoreSW(config)# ip routing

! ② 创建三个 VLAN
CoreSW(config)# vlan 2
CoreSW(config-vlan)# name teacher
CoreSW(config-vlan)# vlan 3
CoreSW(config-vlan)# name stu
CoreSW(config-vlan)# vlan 4
CoreSW(config-vlan)# name server
CoreSW(config-vlan)# exit

! ③ 把接教师的三个口划进 VLAN2
CoreSW(config)# interface range fastEthernet 0/2 - 4
CoreSW(config-if-range)# switchport mode access
CoreSW(config-if-range)# switchport access vlan 2
CoreSW(config-if-range)# exit

! ④ 两个下联口做成 Trunk（因为对端交换机下面还有多个 VLAN 要过来）
CoreSW(config)# interface fastEthernet 0/5
CoreSW(config-if)# switchport trunk encapsulation dot1q
CoreSW(config-if)# switchport mode trunk
CoreSW(config-if)# interface fastEthernet 0/6
CoreSW(config-if)# switchport trunk encapsulation dot1q
CoreSW(config-if)# switchport mode trunk
CoreSW(config-if)# exit

! ⑤ 三个 SVI = 三个 VLAN 的网关
CoreSW(config)# interface vlan 2
CoreSW(config-if)# ip address 192.168.90.1 255.255.255.192
CoreSW(config-if)# no shutdown
CoreSW(config-if)# interface vlan 3
CoreSW(config-if)# ip address 192.168.90.65 255.255.255.192
CoreSW(config-if)# no shutdown
CoreSW(config-if)# interface vlan 4
CoreSW(config-if)# ip address 192.168.90.129 255.255.255.192
CoreSW(config-if)# no shutdown
CoreSW(config-if)# exit

! ⑥ 上联路由器的口改成三层口
CoreSW(config)# interface fastEthernet 0/1
CoreSW(config-if)# no switchport
CoreSW(config-if)# ip address 192.168.90.193 255.255.255.252
CoreSW(config-if)# no shutdown
CoreSW(config-if)# exit

! ⑦ 内网三个网段都是直连的，去 Internet 只需要一条默认路由
CoreSW(config)# ip route 0.0.0.0 0.0.0.0 192.168.90.194
CoreSW(config)# end
CoreSW# write
```

**验证（必须看到这个结果再往下做）**：

```text
CoreSW# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
FastEthernet0/1        192.168.90.193  YES manual up                    up
FastEthernet0/2        unassigned      YES unset  up                    up
...
Vlan2                  192.168.90.1    YES manual up                    up
Vlan3                  192.168.90.65   YES manual up                    up
Vlan4                  192.168.90.129  YES manual up                    up

CoreSW# show ip route
Gateway of last resort is 192.168.90.194 to network 0.0.0.0

     192.168.90.0/26 is subnetted, 3 subnets
C       192.168.90.0 is directly connected, Vlan2
C       192.168.90.64 is directly connected, Vlan3
C       192.168.90.128 is directly connected, Vlan4
     192.168.90.0/30 is subnetted, 1 subnet
C       192.168.90.192 is directly connected, FastEthernet0/1
S*   0.0.0.0/0 [1/0] via 192.168.90.194
```

> **如果 Vlan4 显示 down/down**：说明 Fa0/6（接 Server 交换机的口）还没起来，
> 或者 Server 交换机上没有任何 up 的口。先把接入交换机配好再回来看。

### 5.4 第四步：配两台接入交换机

**student**（挂学生）：

```text
Switch> enable
Switch# configure terminal
Switch(config)# hostname student
student(config)# vlan 3
student(config-vlan)# name stu
student(config-vlan)# exit
student(config)# interface range fastEthernet 0/1 - 3
student(config-if-range)# switchport mode access
student(config-if-range)# switchport access vlan 3
student(config-if-range)# exit
student(config)# interface fastEthernet 0/24
student(config-if)# switchport mode trunk
student(config-if)# end
student# write
```

**Server**（挂服务器）：

```text
Switch> enable
Switch# configure terminal
Switch(config)# hostname Server
Server(config)# vlan 4
Server(config-vlan)# name server
Server(config-vlan)# exit
Server(config)# interface range fastEthernet 0/1 - 3
Server(config-if-range)# switchport mode access
Server(config-if-range)# switchport access vlan 4
Server(config-if-range)# exit
Server(config)# interface fastEthernet 0/24
Server(config-if)# switchport mode trunk
Server(config-if)# end
Server# write
```

**验证**：

```text
student# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/4, Fa0/5, ...
3    stu                              active    Fa0/1, Fa0/2, Fa0/3
```

> **为什么下联口是 Trunk 而不是 Access？**
> 因为核心交换机上有 3 个 VLAN，两个下联口各自要承载「多个 VLAN」的流量，
> 只有 Trunk 才能带 802.1Q 标签区分 VLAN。如果配成 Access，SVI 会 down，VLAN 间就不通。

### 5.5 第五步：配两台路由器

**Router0**（内网出口）：

```text
Router> enable
Router# configure terminal
Router(config)# hostname Router0
Router0(config)# interface fastEthernet 0/0
Router0(config-if)# ip address 192.168.90.194 255.255.255.252
Router0(config-if)# no shutdown
Router0(config-if)# interface serial 0/0/0
Router0(config-if)# ip address 200.0.90.1 255.255.255.252
Router0(config-if)# clock rate 64000
Router0(config-if)# no shutdown
Router0(config-if)# exit
! 回内网：三个 VLAN 汇总成一条
Router0(config)# ip route 192.168.90.0 255.255.255.0 192.168.90.193
! 去 Internet
Router0(config)# ip route 0.0.0.0 0.0.0.0 200.0.90.2
Router0(config)# end
Router0# write
```

**Router1**（模拟 Internet）：

```text
Router> enable
Router# configure terminal
Router(config)# hostname Router1
Router1(config)# interface serial 0/0/0
Router1(config-if)# ip address 200.0.90.2 255.255.255.252
Router1(config-if)# no shutdown
Router1(config-if)# exit
! 用环回口模拟 Internet 上的一台主机
Router1(config)# interface loopback 0
Router1(config-if)# ip address 200.0.90.100 255.255.255.255
Router1(config-if)# exit
! 回程指向 Router0
Router1(config)# ip route 0.0.0.0 0.0.0.0 200.0.90.1
Router1(config)# end
Router1# write
```

> **`clock rate 64000` 只能配在 DCE 端**。哪端是 DCE？看连线上有没有小时钟图标。
> 本例 `Router0` 是 DCE。如果在 DTE 端敲 `clock rate`，PT 会接受命令但不生效（真实 IOS 会报错）。

### 5.6 第六步：配 6 台 PC 和 3 台服务器

**PC 配置**：单击 PC → `Desktop` 标签 → `IP Configuration`：

| PC | IP Address | Subnet Mask | Default Gateway |
|----|-----------|-------------|----------------|
| teacher1 | `192.168.90.10` | `255.255.255.192` | `192.168.90.1` |
| teacher2 | `192.168.90.11` | `255.255.255.192` | `192.168.90.1` |
| teacher3 | `192.168.90.12` | `255.255.255.192` | `192.168.90.1` |
| stu1 | `192.168.90.74` | `255.255.255.192` | `192.168.90.65` |
| stu2 | `192.168.90.75` | `255.255.255.192` | `192.168.90.65` |
| stu3 | `192.168.90.76` | `255.255.255.192` | `192.168.90.65` |

**服务器配置**：单击服务器 → `Desktop` → `IP Configuration`：

| Server | IP Address | Subnet Mask | Default Gateway |
|--------|-----------|-------------|----------------|
| Server0 | `192.168.90.138` | `255.255.255.192` | `192.168.90.129` |
| Server1 | `192.168.90.139` | `255.255.255.192` | `192.168.90.129` |
| Server2 | `192.168.90.140` | `255.255.255.192` | `192.168.90.129` |

**还要打开服务器的 HTTP 服务**（否则浏览器打不开网页）：
单击服务器 → `Services` 标签 → 左边选 `HTTP` → 确认 `HTTP` 和 `HTTPS` 都是 `On`。
PT 的 HTTP 服务**默认就是开着的**，一般不用改，但顺手确认一下。
顺便在 `HTTP` 页里把 `index.html` 的内容改成 `Server0 的首页` 之类，测试时一眼能看出打开的是哪台。

> **服务器网关必须填**，否则服务器 ping 不通别的网段，也没法回包给外网。

### 5.7 第七步：先测「全网通」，建立基线

**这一步不能跳过**。ACL 加上去之后很多流量会不通，如果不先确认「加 ACL 之前是通的」，
出了问题你分不清是路由错了还是 ACL 拦的。

在 `teacher1` 的 `Command Prompt` 里：

```text
PC> ping 192.168.90.11          ! 通 VLAN2 内部
PC> ping 192.168.90.74          ! 通 VLAN3（跨 VLAN，走 SVI）
PC> ping 192.168.90.138         ! 通 VLAN4
PC> ping 192.168.90.194         ! 通 Router0
PC> ping 200.0.90.100           ! 通 Router1 的 Loopback（模拟 Internet）
```

**全部应该通**。最后一条的 TTL 应该是 **126**：

> 起点 TTL=128。报文路径是 teacher1 → CoreSW → Router0 → Router1（Loopback0）。
> **每经过一台做三层转发的设备，TTL 减 1**：
> - CoreSW 把包从 VLAN2 转到 Fa0/1，减 1 → 127
> - Router0 把包从 Fa0/0 转到 Se0/0/0，减 1 → 126
> - Router1 收到后发现目的地址是自己的 Loopback0，**不再转发，所以不减**
>
> 所以最终是 **128 − 2 = 126**。交换机做二层转发时不减 TTL，只有三层转发才减。

```text
PC> ping 200.0.90.100
Reply from 200.0.90.100: bytes=32 time=1ms TTL=126
```

> **TTL 对不上怎么办？** 先 `tracert 200.0.90.100` 看路径有几跳，
> 每多一台三层设备 TTL 就少 1。TTL 是判断「有没有绕路」最快的工具。
> 如果 TTL 是 127，说明少经过了一台三层设备（可能 CoreSW 没开 `ip routing`，
> 走了二层直通）；如果是 125，说明多绕了一台。

### 5.8 第八步：设计并写 ACL

四条需求 → 三张扩展 ACL，全部配在 `CoreSW` 上。

**先想清楚顺序**（ACL 是自上而下匹配、命中即停）：

```text
! ============ ACL 110：挂在 Vlan4 out，管「发给服务器的流量」 ============
! 需求 4：只有 teacher1(.10) 可以 Telnet 服务器
CoreSW(config)# access-list 110 permit tcp host 192.168.90.10 192.168.90.128 0.0.0.63 eq telnet
! 需求 4：其他人 Telnet 服务器一律拒绝
CoreSW(config)# access-list 110 deny tcp any 192.168.90.128 0.0.0.63 eq telnet
! 需求 3：任何人对服务器发 ping（icmp echo）一律拒绝
CoreSW(config)# access-list 110 deny icmp any 192.168.90.128 0.0.0.63 echo
! 兜底：其余流量放行（否则「教师可以访问所有 server」做不到）
CoreSW(config)# access-list 110 permit ip any any

! ============ ACL 120：挂在 Vlan3 in，管「学生发出的流量」 ============
! 需求 2：学生只能访问 Server0(.138) 的 80 端口
CoreSW(config)# access-list 120 permit tcp 192.168.90.64 0.0.0.63 host 192.168.90.138 eq www
! 需求 2：学生访问服务器网段的其余流量一律拒绝
CoreSW(config)# access-list 120 deny ip 192.168.90.64 0.0.0.63 192.168.90.128 0.0.0.63
! 兜底：学生访问内网其他网段、Internet 照常放行
CoreSW(config)# access-list 120 permit ip any any

! ============ ACL 130：挂在 Vlan4 in，管「服务器发出的流量」 ============
! 需求 1：服务器网段不能访问 Internet（200.0.90.0/24）
CoreSW(config)# access-list 130 deny ip 192.168.90.128 0.0.0.63 200.0.90.0 0.0.0.255
! 兜底
CoreSW(config)# access-list 130 permit ip any any

! ============ 挂到接口上 ============
CoreSW(config)# interface vlan 4
CoreSW(config-if)# ip access-group 110 out
CoreSW(config-if)# ip access-group 130 in
CoreSW(config-if)# interface vlan 3
CoreSW(config-if)# ip access-group 120 in
CoreSW(config-if)# end
CoreSW# write
```

**为什么 ACL 110 里 `permit tcp host ... eq telnet` 要写在 `deny tcp any ... eq telnet` 前面？**
因为 ACL 命中即停。如果把 `deny` 写在前面，teacher1 的 Telnet 也会被拒，
后面那条 `permit` 永远轮不到。

**为什么 ACL 110 最后要有 `permit ip any any`？**
因为 ACL 末尾隐含 `deny any`。不加这条，教师访问服务器的 HTTP、ping 之外的所有流量都会被丢，
「教师可以访问所有 server」就做不到。

**为什么 ACL 120 第 2 条是 `deny ip` 而不是 `deny tcp`？**
因为需求是「学生**只能**访问 server0 的 web 服务」，除了 tcp 80 之外的所有流量（含 ping、其他端口）都该拒。

> **关于「学生 ping 不通 Server0」**：这是严格按字面实现的结果。
> 如果老师的意思是「学生只能访问 server0 的 web 页面，ping 无所谓」，
> 那把第 2 条改成 `deny ip 192.168.90.64 0.0.0.63 host 192.168.90.139` 再加一条 `.140` 即可。
> 两种写法都合理，**报告里说明你选了哪种、为什么**，比默默选一种更得分。

**验证 ACL 本身**：

```text
CoreSW# show access-lists
Extended IP access list 110
    10 permit tcp host 192.168.90.10 192.168.90.128 0.0.0.63 eq telnet
    20 deny tcp any 192.168.90.128 0.0.0.63 eq telnet
    30 deny icmp any 192.168.90.128 0.0.0.63 echo
    40 permit ip any any
Extended IP access list 120
    10 permit tcp 192.168.90.64 0.0.0.63 host 192.168.90.138 eq www
    20 deny ip 192.168.90.64 0.0.0.63 192.168.90.128 0.0.0.63
    30 permit ip any any
Extended IP access list 130
    10 deny ip 192.168.90.128 0.0.0.63 200.0.90.0 0.0.0.255
    20 permit ip any any
```

> **注意 PT 会把 `eq 80` 显示成 `eq www`、`eq 23` 显示成 `eq telnet`**。
> 这是正常的规范化，不是配错了。报告里照 `show access-lists` 的实际输出写。

### 5.9 第九步：逐条验证四条需求

在 PC 的 `Command Prompt` 里敲，或者用浏览器的 `Web Browser` 标签：

| 编号 | 在哪台设备上 | 命令 | 预期 | 对应规则 |
|------|------------|------|------|---------|
| ① | teacher1 | `ping 200.0.90.100` | **通**（TTL=126） | 未被拦截 |
| ② | Server0 | `ping 200.0.90.100` | **不通**（Request timed out） | ACL 130 |
| ③ | stu1 | `ping 192.168.90.138` | **不通** | ACL 120 第 2 条 |
| ④ | stu1 | 浏览器访问 `http://192.168.90.138` | **能打开** Server0 的网页 | ACL 120 第 1 条 |
| ⑤ | stu1 | 浏览器访问 `http://192.168.90.139` | **打不开** | ACL 120 第 2 条 |
| ⑥ | teacher2 | `ping 192.168.90.138` | **不通** | ACL 110 第 3 条 |
| ⑦ | teacher1 | `telnet 192.168.90.138` | 提示 `Connection refused`（端口通但无服务） | ACL 110 第 1 条 permit |
| ⑧ | teacher2 | `telnet 192.168.90.138` | 无响应 / 超时 | ACL 110 第 2 条 deny |
| ⑨ | CoreSW | `show access-lists` | 三张表都有匹配计数 | — |

**验证 ⑦⑧ 的差别时要有耐心**：PT 的 telnet 超时大约 30 秒，
被 deny 的那次会卡很久才返回。如果两次现象一样，八成是 ACL 没挂上（回去看 `show run interface vlan 4`）。

**检查匹配计数**：

```text
CoreSW# show access-lists
Extended IP access list 110
    10 permit tcp host 192.168.90.10 192.168.90.128 0.0.0.63 eq telnet (4 matches)
    20 deny tcp any 192.168.90.128 0.0.0.63 eq telnet (2 matches)
    30 deny icmp any 192.168.90.128 0.0.0.63 echo (12 matches)
    40 permit ip any any (86 matches)
```

> **匹配计数是 ACL 排错的第一手证据**。如果某条规则一直是 0 matches，
> 说明「你以为会走这条规则的流量根本没经过这里」——要么挂错接口，要么挂错方向，要么路由就不通。
> 报告里把带 matches 的输出贴上去，比只贴配置有说服力得多。

### 5.10 第十步：截图与收尾

按下面的清单截图（每张都截**整个 PT 窗口**，包含标题栏的工程路径，能证明是你自己做的）：

| 截图内容 | 存成 | 用在报告哪里 |
|---------|------|------------|
| 完整拓扑（能看清所有设备和接口标注） | `fig_acl_topo.png` | 图 2 |
| `CoreSW# show ip interface brief` | `fig_acl_svi.png` | 正文 |
| `CoreSW# show access-lists`（带 matches） | `fig_acl_showacl.png` | 正文 |
| `CoreSW# show run \| include access-group` | `fig_acl_apply.png` | 正文 |
| teacher1 ping 200.0.90.100 成功 | `fig_acl_t1ping.png` | 表 3 第 ① 项 |
| Server0 ping 200.0.90.100 失败 | `fig_acl_srvping.png` | 表 3 第 ② 项 |
| stu1 打开 Server0 网页成功 | `fig_acl_web_ok.png` | 表 3 第 ④ 项 |
| stu1 打开 Server1 网页失败 | `fig_acl_web_no.png` | 表 3 第 ⑤ 项 |
| teacher2 ping 服务器失败 | `fig_acl_t2ping.png` | 表 3 第 ⑥ 项 |
| teacher1 / teacher2 telnet 现象对比 | `fig_acl_telnet.png` | 表 3 第 ⑦⑧ 项 |

保存工程：`Ctrl+S`。

---

## 6. 实验（二）NAT 的配置：从零搭到能验证

### 6.1 最省力的起点：复制实验（一）

实验（二）的内网部分和实验（一）**一模一样**（同样的 3 个 VLAN、同样的 SVI、同样的 PC 地址）。
所以不要从零再搭一遍：

1. 打开 `90-实验二一-ACL配置.pkt`。
2. `File → Save As`，存成 `90-实验二二-NAT配置.pkt`。
3. 删掉 `Router0`、`Router1`，以及 `Server1`、`Server2`（实验二只有一台 web 服务器）。
4. 删掉 CoreSW 上所有 `access-list` 和 `ip access-group`（NAT 实验不考 ACL，
   留着会让 NAT 测试结果受干扰）：

```text
CoreSW(config)# no access-list 110
CoreSW(config)# no access-list 120
CoreSW(config)# no access-list 130
CoreSW(config)# interface vlan 4
CoreSW(config-if)# no ip access-group 110 out
CoreSW(config-if)# no ip access-group 130 in
CoreSW(config-if)# interface vlan 3
CoreSW(config-if)# no ip access-group 120 in
CoreSW(config-if)# exit
```

5. 把 `Server` 交换机的 Fa0/1 改成接 `web服务器`，地址 `192.168.90.138/26`、网关 `192.168.90.129`。

> **为什么要删 ACL？** 实验（二）的需求里没有 ACL。留着的话，
> 「服务器不能访问 Internet」那条会直接把 NAT 测试搞失败，你会以为 NAT 配错了。

### 6.2 摆上新设备

在原有基础上再加 5 台：

| 数量 | 设备型号 | 改名为 | 地址 |
|------|---------|--------|------|
| 1 | 1841（加 WIC-2T） | `NAT路由器` | Fa0/0 = `192.168.90.194/30`，Se0/0/0 = `200.0.90.1/30` |
| 1 | 1841（加 WIC-2T） | `Internet路由器` | Se0/0/0 = `200.0.90.2/30`，Fa0/0 = `200.0.90.9/29` |
| 1 | 2960-24TT | `外网网络` | 二层，划一个 VLAN10 |
| 1 | PC-PT | `外网用户` | `200.0.90.11/29`，网关 `200.0.90.9` |
| 1 | Server-PT | `外网服务器` | `200.0.90.10/29`，网关 `200.0.90.9` |

**新增连线**：

| 从 | 到 | 线型 |
|----|----|------|
| CoreSW Fa0/1 | NAT路由器 Fa0/0 | 直通 |
| NAT路由器 Se0/0/0 | Internet路由器 Se0/0/0 | Serial DTE |
| Internet路由器 Fa0/0 | 外网网络 Fa0/1 | 直通 |
| 外网网络 Fa0/2 | 外网用户 Fa0 | 直通 |
| 外网网络 Fa0/3 | 外网服务器 Fa0 | 直通 |

> **`NAT路由器` 是 DCE 端**（连线上有时钟图标），所以 `clock rate 64000` 配在它的 Se0/0/0 上。

### 6.3 配 NAT路由器（本实验的核心）

```text
Router> enable
Router# configure terminal
Router(config)# hostname NAT路由器
NAT路由器(config)# interface fastEthernet 0/0
NAT路由器(config-if)# ip address 192.168.90.194 255.255.255.252
NAT路由器(config-if)# ip nat inside                  ! 朝内网的一侧
NAT路由器(config-if)# no shutdown
NAT路由器(config-if)# interface serial 0/0/0
NAT路由器(config-if)# ip address 200.0.90.1 255.255.255.252
NAT路由器(config-if)# ip nat outside                 ! 朝 Internet 的一侧
NAT路由器(config-if)# clock rate 64000
NAT路由器(config-if)# no shutdown
NAT路由器(config-if)# exit

! ① 定义公网地址池
NAT路由器(config)# ip nat pool PUB 200.0.90.17 200.0.90.22 netmask 255.255.255.240

! ② 用 ACL 定义「哪些内网地址允许被转换」
NAT路由器(config)# access-list 1 permit 192.168.90.0 0.0.0.255

! ③ 绑定：ACL 1 匹配到的源地址，从池里取一个公网地址做一对一转换
NAT路由器(config)# ip nat inside source list 1 pool PUB

! ④ 静态 PAT：把 web 服务器的 80 端口发布到 200.0.90.30:80
NAT路由器(config)# ip nat inside source static tcp 192.168.90.138 80 200.0.90.30 80

! ⑤ 路由：回内网、去 Internet
NAT路由器(config)# ip route 192.168.90.0 255.255.255.0 192.168.90.193
NAT路由器(config)# ip route 0.0.0.0 0.0.0.0 200.0.90.2
NAT路由器(config)# end
NAT路由器# write
```

> **`access-list 1` 是标准 ACL**（1—99），NAT 只关心「源地址是否匹配」，
> 所以标准 ACL 就够了，不需要扩展 ACL。这一点和实验（一）不同，别搞混。

**验证**：

```text
NAT路由器# show ip nat translations
Pro  Inside global     Inside local      Outside local     Outside global
---  200.0.90.30       192.168.90.138    ---               ---
tcp  200.0.90.30:80    192.168.90.138:80 ---               ---
```

刚配完只有静态 PAT 那一条（常驻）。动态 NAT 的表项要等**内网主机主动发包**才出现。

### 6.4 配 Internet路由器与外网网络

**Internet路由器**：

```text
Router> enable
Router# configure terminal
Router(config)# hostname Internet路由器
Internet路由器(config)# interface serial 0/0/0
Internet路由器(config-if)# ip address 200.0.90.2 255.255.255.252
Internet路由器(config-if)# no shutdown
Internet路由器(config-if)# interface fastEthernet 0/0
Internet路由器(config-if)# ip address 200.0.90.9 255.255.255.248
Internet路由器(config-if)# no shutdown
Internet路由器(config-if)# exit
! 去 NAT 地址池的流量要回到 NAT 路由器，否则外网服务器无法回包给 .17—.22
Internet路由器(config)# ip route 200.0.90.16 255.255.255.240 200.0.90.1
Internet路由器(config)# end
Internet路由器# write
```

> **`.30` 为什么不用单独加路由？** 因为 `.30` 落在 `200.0.90.16/28` 里，
> 上面那条 `/28` 的静态路由已经覆盖了它。这是本实验的一个巧合便利，
> 如果静态 PAT 用的是别的网段的公网地址，就必须补一条明细路由。

**外网网络**（二层交换机，划一个 VLAN10 把三个口放进去）：

```text
Switch> enable
Switch# configure terminal
Switch(config)# hostname 外网网络
外网网络(config)# vlan 10
外网网络(config-vlan)# name outside
外网网络(config-vlan)# exit
外网网络(config)# interface fastEthernet 0/1
外网网络(config-if)# switchport mode access
外网网络(config-if)# switchport access vlan 10
外网网络(config-if)# interface fastEthernet 0/2
外网网络(config-if)# switchport mode access
外网网络(config-if)# switchport access vlan 10
外网网络(config-if)# interface fastEthernet 0/3
外网网络(config-if)# switchport mode access
外网网络(config-if)# switchport access vlan 10
外网网络(config-if)# end
外网网络# write
```

> **为什么要把三个口划进 VLAN10 而不是用默认的 VLAN1？**
> 用 VLAN1 也能通，但题目要求「在交换机上完成 vlan 的创建、将指定接口划分给相应 vlan」，
> 用一个专门的 VLAN10 才算真的做了这个动作。报告里也好写。

### 6.5 配外网终端

| 设备 | IP | 掩码 | 网关 | 额外设置 |
|------|-----|------|------|---------|
| 外网用户 | `200.0.90.11` | `255.255.255.248` | `200.0.90.9` | — |
| 外网服务器 | `200.0.90.10` | `255.255.255.248` | `200.0.90.9` | `Services → HTTP` 打开，改个首页内容 |

### 6.6 先测基线：动态 NAT 能不能工作

在 `teacher1` 的 Command Prompt 里：

```text
PC> ping 200.0.90.10
```

**第一次会丢一个包**（因为要先建立 NAT 表项），然后应该通。

立刻回 NAT路由器 看表项：

```text
NAT路由器# show ip nat translations
Pro  Inside global     Inside local       Outside local      Outside global
icmp 200.0.90.17:1     192.168.90.10:1    200.0.90.10:1      200.0.90.10:1
---  200.0.90.30       192.168.90.138     ---                ---
tcp  200.0.90.30:80    192.168.90.138:80  ---                ---
```

**读法**：
- `Inside local` = 内网主机的真实地址（`192.168.90.10`）
- `Inside global` = 它在公网上「看起来」的地址（`200.0.90.17`，从池里取的）

再让 `stu1` ping 一次，会出现第二条，占 `.18`：

```text
icmp 200.0.90.18:2     192.168.90.74:2    200.0.90.10:2      200.0.90.10:2
```

> **为什么是 `.17` 和 `.18` 而不是随机？** PT 的地址池是**按顺序分配**的，
> 第一台主机拿池里第一个地址，第二台拿第二个。这也是报告里可以写的观察结果。

### 6.7 测静态 PAT：外网访问内网服务器

在 `外网用户` 的 `Desktop → Web Browser` 里访问：

```text
http://200.0.90.30
```

**应该能打开 `web服务器` 的首页**（因为 `.30:80` 被映射到了 `192.168.90.138:80`）。

再访问一次私网地址，验证「公网不能直接路由私网」：

```text
http://192.168.90.138
```

**打不开**（外网路由器上没有 `192.168.90.0/24` 的路由）。

> 这个对比是 NAT 实验最有说服力的一组截图：
> **同一个 web 服务器，用公网地址 `.30` 能访问，用私网地址 `.138` 访问不了。**

### 6.8 完整测试表

| 编号 | 在哪台设备上 | 命令 / 操作 | 预期结果 | 说明 |
|------|------------|------------|---------|------|
| ① | teacher1 | `ping 200.0.90.10` | 通（第一次丢 1 个包） | 内网 → 外网服务器，触发动态 NAT |
| ② | NAT路由器 | `show ip nat translations` | 出现 `192.168.90.10 ↔ 200.0.90.17` | 动态 NAT 已建立 |
| ③ | stu1 | `ping 200.0.90.10` | 通，表项多一条（占 `.18`） | 池内地址按序分配 |
| ④ | 外网用户 | 浏览器访问 `http://200.0.90.30` | 能打开 web 服务器的网页 | 静态 PAT 生效 |
| ⑤ | 外网用户 | 浏览器访问 `http://192.168.90.138` | 打不开 | 私网地址在公网不可路由 |
| ⑥ | web服务器 | 浏览器访问 `http://200.0.90.10` | 打不开（或不通） | 该方向需要双向 NAT，本题未要求 |
| ⑦ | NAT路由器 | `show ip nat statistics` | 能看到 pool PUB 的地址总数与已用数 | 核对地址池 |

**第 ⑦ 项的输出示例**：

```text
NAT路由器# show ip nat statistics
Total active translations: 3 (1 static, 2 dynamic; 0 extended)
Outside interfaces:
  Serial0/0/0
Inside interfaces:
  FastEthernet0/0
Hits: 12  Misses: 0
...
Pool PUB: netmask 255.255.255.240
  start 200.0.90.17 end 200.0.90.22
  type generic, total addresses 6, allocated 2 (33%), misses 0
```

> `allocated 2 (33%)` 说明池里 6 个地址用了 2 个。这就是「动态 NAT 不加 overload 会耗尽地址」的直观证据。

### 6.9 截图清单

| 截图内容 | 存成 |
|---------|------|
| 完整 NAT 拓扑 | `fig_nat_topo.png` |
| `NAT路由器# show ip nat translations` | `fig_nat_trans.png` |
| `NAT路由器# show ip nat statistics` | `fig_nat_stats.png` |
| `NAT路由器# show run \| include nat` | `fig_nat_run.png` |
| teacher1 ping 外网服务器成功 | `fig_nat_ping.png` |
| 外网用户访问 `http://200.0.90.30` 成功 | `fig_nat_pat_ok.png` |
| 外网用户访问 `http://192.168.90.138` 失败 | `fig_nat_pat_no.png` |

---

## 7. 报告怎么写

### 7.1 模板长什么样

打开 `实验2\01-实验报告\90-实验二-ACL与NAT配置-实验报告.docx`（或者学校给的空白模板），
你会看到一张 8 行的表格，每行是一个填写区：

| 行 | 内容 | 你要填什么 |
|----|------|-----------|
| R0 | 实验名称 | `访问控制列表（ACL）与网络地址转换（NAT）的配置` |
| R1 | 姓名 / 学号 / 班级 | 自己填 |
| R2 | 实验地点 / 实验日期 / 评分 | 地点、日期填上，评分留空 |
| R3 | 指导老师 / 同组其他成员 / 评分 | 老师姓名，同组填「无」或组员名 |
| R4 | 一、实验内容（含实验任务） | 把题目原文**完整抄一遍**（含两个小实验的所有子项） |
| R5 | 二、实验目的 | 写 6—8 条，见 7.2 |
| R6 | 三、涉及实验的相关情况介绍 | 软件、设备清单、连线、模块、地址规划、测试方法，见 7.3 |
| R7 | 四、实验结果 | 正文主体，见 7.4 |

> **R4 一定要抄全**。有的同学图省事只写「见题目」，这是直接扣分的。
> 抄的时候保留题目里的编号（一、二、1、2、3…），让老师能一条条对。

### 7.2 R5 实验目的怎么写

按「知识 → 技能 → 分析」三层递进，每条一个动词开头：

1. 掌握 VLAN 的创建与端口划分，理解 Access 与 Trunk 端口的区别与适用场景；
2. 掌握三层交换机 `ip routing`、SVI、`no switchport` 三层口的配置，理解三层交换机实现 VLAN 间路由的原理；
3. 掌握静态路由的配置与 `show ip route` 的路由表阅读方法，能区分直连路由、静态路由与默认路由；
4. 掌握标准 ACL 与扩展 ACL 的语法差异，理解「源地址过滤」与「源+目的+协议+端口」四要素过滤的能力边界；
5. 掌握 ACL 在接口上的挂载方向（in/out）与位置选择，能用 `show access-lists` 的匹配计数验证规则是否生效；
6. 掌握 NAT 的四个组成部分（inside/outside 划分、地址池、匹配 ACL、绑定语句），理解动态 NAT、NAPT 与静态 PAT 的区别；
7. 掌握 `show ip nat translations` 与 `show ip nat statistics` 的输出阅读，能判断 NAT 是否真正建立了转换表项；
8. 能按「先通后控」的顺序组织实验：先验证全网可达建立基线，再逐条加入控制策略并观察差异。

### 7.3 R6 相关情况介绍怎么写

分六段，每段 2—4 行：

**（1）软件**：Cisco Packet Tracer 8.2.2（版本号 8.2.0.0162），Windows 版；
文档工具 Microsoft Word / WPS。

**（2）设备**（PT 内模拟）：Cisco 3560-24PS 三层交换机 1 台、Cisco 2960-24TT 二层交换机 2 台
（NAT 部分 3 台）、Cisco 1841 路由器 2 台、PC-PT 终端 6 台、Server-PT 服务器 3 台（NAT 部分 2 台）。

**（3）连接线**：PC 与交换机、交换机与路由器之间用直通线（Copper Straight-Through）；
两台路由器之间用串行线（Serial DTE，红色折线，DCE 端需配 `clock rate`）。

**（4）接口模块**：1841 出厂不带串行接口，需要在**断电状态**下把 WIC-2T 模块拖入空槽，
开机后才会出现 `Serial0/0/0` 与 `Serial0/0/1`。

**（5）地址规划**：内网全部落在 `192.168.90.0/24` 内（90 为学号后两位），
三个 VLAN 各用 `/26`（VLAN2 `192.168.90.0/26`、VLAN3 `192.168.90.64/26`、VLAN4 `192.168.90.128/26`）；
核心交换机与出口路由器之间用 `/30`（`192.168.90.192/30`）；
公网侧全部落在 `200.0.90.0/24` 内，互联用 `/30`，外网 LAN 用 `/29`，NAT 地址池用 `/28`。

**（6）测试方法**：PC 上使用 `ping`、`tracert`、`telnet` 与浏览器；
路由器/交换机上使用 `show ip interface brief`、`show ip route`、`show vlan brief`、
`show access-lists`、`show ip nat translations`、`show ip nat statistics`、`show running-config` 等命令。

### 7.4 R7 实验结果怎么写

建议按下面的骨架组织（本教程配套的报告就是按这个结构写的，共 14 页）：

```text
（一）ACL 的配置
  1. 实验拓扑与地址规划        ← 贴图 2 + 表 1
  2. 设备选型与连线            ← 文字 + 表 2（端口连接表）
  3. VLAN 与 Trunk 的配置      ← 代码块
  4. 三层交换机 SVI 与三层口    ← 代码块 + 验证输出
  5. 路由器的基本配置与路由     ← 代码块
  6. ACL 的设计与配置          ← 表 3（ACL 编号/位置/需求对应）+ 代码块
  7. 测试与结果                ← 表 4（9 项测试）+ 截图
  8. 实验结论                  ← 4 条

（二）NAT 的配置
  1. 拓扑与地址规划            ← 贴图 3 + 表 5
  2. 内网部分（与第一部分相同）
  3. NAT 路由器：inside/outside 与动态 NAT
  4. 静态 PAT
  5. Internet 路由器与外网网络
  6. 测试与结果                ← 表 6（7 项测试）+ 截图
  7. 实验结论                  ← 4 条

（三）实验总结
  两个部分串起来的完整出口链路 + 10 个易错点 + 排错顺序 + 地址规划说明
```

**写结论的技巧**：不要写「我学会了 ACL」这种空话，要写**机制层面的结论**。举几个本实验可用的：

- 扩展 ACL 的过滤粒度是「源地址 + 目的地址 + 协议 + 端口」四要素，
  标准 ACL 只能看源地址，做不了「学生只能访问 server0 的 web」这类需求，所以四条需求全部用扩展 ACL。
- SVI 上的 in/out 以「该 VLAN 内主机的视角」判断：in = 主机发出的包，out = 发给主机的包。
  同一个限制既可以写成「源所在接口 in」也可以写成「目的所在接口 out」，但 in 方向更早丢弃、不浪费带宽。
- ACL 末尾隐含 `deny any`，所以每张表最后都要补 `permit ip any any` 兜底；
  不加之后「本来能通的流量」也会被丢，这是 ACL 排错的第一大原因。
- ACL 只对穿越设备的流量生效，对设备自己产生的流量无效。
- NAT 的三个必备条件：正确的 inside/outside 划分、匹配内网源的 ACL、`ip nat inside source` 绑定语句，
  三者缺一，`show ip nat translations` 就是空的。
- 动态 NAT 与静态 PAT 的发起方向相反：动态 NAT 由内网发起才建表，静态 PAT 表项常驻、外网发起也能命中。
- 动态 NAT（不加 overload）是一个内网 IP 占一个公网 IP，池子用完就失败；
  加 overload 才是端口复用（NAPT），才能让任意多台主机共享少量公网地址。

### 7.5 截图与排版

- 截图宽度统一 `15 cm`（A4 正文宽 19 cm）。
- 每张图下面都要有图注：`图 2  实验二（一）ACL 实验拓扑`（**图号和正文引用必须一致**）。
- 代码块用等宽字体（Consolas / Courier New），字号 9—10 pt，加浅灰底。
- **不要用空格对齐**（换个字体就乱），表格用 Word 的表格功能。

### 7.6 四件不能做的事

1. **不要把别的同学的配置截图贴上来**（设备名、IP 里的学号后两位会露馅）。
2. **不要伪造测试结果**。ping 不通就写不通，然后分析原因——「预期通但实际不通，原因是…」比「全部通过」更得分。
3. **不要漏掉「实验现象」**。报告里只有配置没有现象，等于没做实验。
4. **不要在报告里写「PT 里做不到所以没做」**。要先查清楚是不是真的做不到（比如 Server-PT 没有 Telnet 服务端是真的做不到，那就要说明并给出替代验证方案，而不是直接跳过）。

---

## 8. 自检清单（做完逐条打勾）

### 8.1 通用（两个实验都要过）

- [ ] 工程文件名符合 `90-实验二X-内容.pkt`，存在 `实验2\03-工程文件\` 下。
- [ ] 打开工程后**标题栏显示完整路径**（证明文件能正常加载）。
- [ ] 所有设备的 `Display Name` 和 `hostname` **一致**（不能画布叫 CoreSW、CLI 里叫 Switch）。
- [ ] 所有 PC/服务器的 IP、掩码、**网关**都填了（网关最容易漏）。
- [ ] 所有用到的接口都是 `up/up`（`show ip interface brief` 里没有 `administratively down`）。
- [ ] 每个工程都 `write` 保存过配置（否则重开工程配置就没了）。
- [ ] 报告里所有图号、表号与正文引用**一一对应**，没有「图 3 说的是图 4 的内容」。

### 8.2 实验（一）ACL 专项

- [ ] CoreSW 上敲了 `ip routing`（`show run | include ip routing` 能看到）。
- [ ] 三个 SVI 都有 IP 且 `up/up`（`show ip interface brief`）。
- [ ] Fa0/1 是三层口（`show run interface fa0/1` 里有 `no switchport`）。
- [ ] Fa0/5、Fa0/6 是 Trunk（`show interfaces trunk` 能看到两个口）。
- [ ] student 的 Fa0/1—0/3 在 VLAN3，Server 的 Fa0/1—0/3 在 VLAN4（`show vlan brief`）。
- [ ] **加 ACL 之前**先验证过全网通（尤其 teacher1 能 ping 通 200.0.90.100）。
- [ ] 三张 ACL（110/120/130）都在，且**每条都带 `permit ip any any` 兜底**。
- [ ] `show run interface vlan 3` 里有 `ip access-group 120 in`。
- [ ] `show run interface vlan 4` 里有 `ip access-group 110 out` **和** `ip access-group 130 in`。
- [ ] `show access-lists` 里每条规则的 matches **不是全 0**（全 0 说明流量没经过）。
- [ ] 9 项测试（表 4）逐条做过，现象与预期一致，不一致的地方写清了原因。
- [ ] 通配符掩码是 `0.0.0.63` 这种形式，**不是** `0.0.0.192`。

### 8.3 实验（二）NAT 专项

- [ ] 内网部分与实验（一）一致（同 VLAN、同 SVI、同 PC 地址）。
- [ ] **实验（一）的 ACL 已全部删掉**（`show run | include access-group` 应该没有输出）。
- [ ] NAT路由器 Fa0/0 有 `ip nat inside`，Se0/0/0 有 `ip nat outside`。
- [ ] `ip nat pool PUB 200.0.90.17 200.0.90.22 netmask 255.255.255.240` 存在。
- [ ] `access-list 1 permit 192.168.90.0 0.0.0.255` 存在（**标准 ACL，编号 1**）。
- [ ] `ip nat inside source list 1 pool PUB` 存在（**没有** `overload`，因为题目要动态 NAT）。
- [ ] `ip nat inside source static tcp 192.168.90.138 80 200.0.90.30 80` 存在。
- [ ] `show ip nat translations` 里能看到 `192.168.90.10 ↔ 200.0.90.17` 这样的动态表项。
- [ ] `show ip nat statistics` 里 `allocated` 不是 0。
- [ ] 外网用户能访问 `http://200.0.90.30`，**不能**访问 `http://192.168.90.138`。
- [ ] 外网网络交换机上建了 VLAN10 且三个口都在里面（`show vlan brief`）。

### 8.4 报告检查

- [ ] R4 把题目**两个小实验**的要求都抄全了。
- [ ] R5 有 6 条以上实验目的，覆盖 VLAN/SVI/静态路由/ACL/NAT/验证方法。
- [ ] R6 六段齐全（软件/设备/连线/模块/地址规划/测试方法）。
- [ ] R7 里每个小实验都有：拓扑图 + 地址表 + 配置代码 + 测试表 + 结论。
- [ ] 报告里**主动写明**了两处与题目/环境相关的说明：
      （a）PT 的 Server-PT 没有 Telnet 服务端，Telnet 验证靠 permit/deny 的现象差异；
      （b）「学生只能访问 server0 的 web」按字面实现后，学生 ping Server0 也不通。
- [ ] 学号后两位 `90` 在所有 IP 里都体现了。
- [ ] 没有错别字（重点检查：`Vlan` vs `VLAN`、`Fa0/0` vs `Fa0/1`、`inside` vs `outside`、`overload`）。
- [ ] 全文没有「TODO」「待补」「占位」这类字样。

---

## 9. 故障排查速查表

### 9.1 二层/三层

| 现象 | 最可能的原因 | 怎么查 / 怎么修 |
|------|------------|----------------|
| SVI 是 `down/down`，IP 配了也不通 | 该 VLAN 里没有任何 up 的物理口 | `show vlan brief` 看 VLAN 里有没有口；把接终端的口划进该 VLAN |
| SVI 是 `up/up`，但 VLAN 间 ping 不通 | 忘了 `ip routing` | `show run \| include ip routing`，没有就补上 |
| 三层口配不了 IP | 还是二层口 | 先 `no switchport` |
| 下联口配成 Access 后 SVI down | Access 口只承载一个 VLAN，其它 VLAN 没口 up | 改成 `switchport mode trunk` |
| 两个 VLAN 都能 ping 网关，但互相不通 | Trunk 封装不一致 / 没配 Trunk | `show interfaces trunk`，两端都要 `switchport mode trunk` |
| `show ip route` 里没有默认路由 | 静态路由写错或下一跳不可达 | 检查下一跳是否在直连网段 |

### 9.2 ACL

| 现象 | 最可能的原因 | 怎么查 / 怎么修 |
|------|------------|----------------|
| 加了 ACL 之后**全网都不通** | 忘了末尾的 `permit ip any any` | 每张表最后补一条 |
| 某条规则 matches 一直是 0 | 挂错接口 / 挂错方向 / 路由本来就不通 | 先 `show ip route` 确认可达，再核对 `show run interface` 里的 in/out |
| 该通的被拒了 | 规则的**顺序**反了（deny 写在 permit 前面） | 删表重配，把 permit 提前 |
| 该拒的还能通 | 通配符掩码写成了子网掩码 | 改成 `0.0.0.63` 这种取反形式 |
| `ip access-group` 在交换机上不生效 | 该交换机是二层，没有三层转发能力 | 挂到三层交换机或路由器上 |
| 限制不住设备自己发的包 | ACL 只管穿越流量 | 用 `access-class` 或本地策略 |

### 9.3 NAT

| 现象 | 最可能的原因 | 怎么查 / 怎么修 |
|------|------------|----------------|
| `show ip nat translations` 完全是空的 | 缺 inside/outside 之一 / 缺 ACL / 缺绑定语句 | 四要素逐个核对 |
| 表项有，但 ping 不通外网 | 缺默认路由 / 外网路由器没有回程路由 | `show ip route` 两端都看 |
| 前几个包丢，后面通 | 正常现象（建表项需要时间） | 报告里说明即可 |
| 外网访问 `.30` 打不开 | 静态 PAT 写错端口 / 外网没有到 `.30` 的回程路由 | `show run \| include static`；检查外网路由 |
| 第 7 台主机上不了网 | 动态 NAT 不加 overload，池里只有 6 个地址 | 这就是题目要考的「动态 NAT 的局限」，写进结论 |
| `allocated` 一直是 0 | 内网主机没发过包，或 ACL 没匹配上 | 先从 PC ping 一次 |

### 9.4 特殊设备

| 现象 | 原因 | 处理 |
|------|------|------|
| 1841 上找不到 `Serial0/0/0` | 没插 WIC-2T | 断电 → 拖 WIC-2T 进空槽 → 通电 |
| 插模块时提示不能添加 | 设备没断电 | 先点电源开关 |
| `clock rate` 敲了但链路不通 | 配在了 DTE 端 | 配到有时钟图标的那一端 |
| 服务器网页打不开 | HTTP 服务没开 / 网关没填 | `Services → HTTP` 检查；`Desktop → IP Configuration` 补网关 |
| telnet 一直超时 | 目标没有 telnet 服务（Server-PT 就没有） | 换成路由器做 telnet 目标，或按 3.7 的方式解释现象 |
| 打开工程后点设备没反应 | 文件没加载成功 | 看标题栏有没有完整路径 |

### 9.5 排错黄金顺序

遇到「不通」，**永远按这个顺序查**，不要跳步：

```text
① show ip interface brief      → 链路和地址对不对（有没有 down、有没有配错 IP）
② show ip route                → 路由有没有（该有的网段在不在、下一跳对不对）
③ show vlan brief / show interfaces trunk  → 二层归属对不对
④ show access-lists            → ACL 有没有误拦（看 matches）
⑤ show ip nat translations     → NAT 有没有建表
⑥ PC 上 ping / tracert         → 端到端验证
```

**顺序不能颠倒**：先查 ACL 再查路由，会把「路由不通」误判成「被 ACL 拦了」，
然后去改 ACL，越改越乱。

---

## 10. 附录：四台关键设备的完整配置

下面四份配置是从 `90-实验二一-ACL配置.pkt` 与 `90-实验二二-NAT配置.pkt` 里
`show running-config` 抄出来的（PT 保存后会自动补全所有接口 stanza，这里只保留有内容的行）。

### 10.1 实验（一）CoreSW 完整配置

```text
version 12.2
hostname CoreSW
!
ip routing
!
vlan 2
 name teacher
vlan 3
 name stu
vlan 4
 name server
!
interface FastEthernet0/1
 no switchport
 ip address 192.168.90.193 255.255.255.252
!
interface FastEthernet0/2
 switchport access vlan 2
 switchport mode access
!
interface FastEthernet0/3
 switchport access vlan 2
 switchport mode access
!
interface FastEthernet0/4
 switchport access vlan 2
 switchport mode access
!
interface FastEthernet0/5
 switchport trunk encapsulation dot1q
 switchport mode trunk
!
interface FastEthernet0/6
 switchport trunk encapsulation dot1q
 switchport mode trunk
!
interface Vlan2
 ip address 192.168.90.1 255.255.255.192
!
interface Vlan3
 ip address 192.168.90.65 255.255.255.192
 ip access-group 120 in
!
interface Vlan4
 ip address 192.168.90.129 255.255.255.192
 ip access-group 110 out
 ip access-group 130 in
!
ip route 0.0.0.0 0.0.0.0 192.168.90.194
!
access-list 110 permit tcp host 192.168.90.10 192.168.90.128 0.0.0.63 eq telnet
access-list 110 deny tcp any 192.168.90.128 0.0.0.63 eq telnet
access-list 110 deny icmp any 192.168.90.128 0.0.0.63 echo
access-list 110 permit ip any any
access-list 120 permit tcp 192.168.90.64 0.0.0.63 host 192.168.90.138 eq www
access-list 120 deny ip 192.168.90.64 0.0.0.63 192.168.90.128 0.0.0.63
access-list 120 permit ip any any
access-list 130 deny ip 192.168.90.128 0.0.0.63 200.0.90.0 0.0.0.255
access-list 130 permit ip any any
!
end
```

### 10.2 实验（一）Router0 与 Router1

```text
! ================= Router0 =================
version 12.4
hostname Router0
!
interface FastEthernet0/0
 ip address 192.168.90.194 255.255.255.252
!
interface Serial0/0/0
 ip address 200.0.90.1 255.255.255.252
 clock rate 64000
!
ip route 192.168.90.0 255.255.255.0 192.168.90.193
ip route 0.0.0.0 0.0.0.0 200.0.90.2
!
end

! ================= Router1 =================
version 12.4
hostname Router1
!
interface Serial0/0/0
 ip address 200.0.90.2 255.255.255.252
!
interface Loopback0
 ip address 200.0.90.100 255.255.255.255
!
ip route 0.0.0.0 0.0.0.0 200.0.90.1
!
end
```

### 10.3 实验（二）NAT路由器

```text
version 12.4
hostname NAT路由器
!
interface FastEthernet0/0
 ip address 192.168.90.194 255.255.255.252
 ip nat inside
!
interface Serial0/0/0
 ip address 200.0.90.1 255.255.255.252
 ip nat outside
 clock rate 64000
!
ip route 192.168.90.0 255.255.255.0 192.168.90.193
ip route 0.0.0.0 0.0.0.0 200.0.90.2
!
ip nat pool PUB 200.0.90.17 200.0.90.22 netmask 255.255.255.240
access-list 1 permit 192.168.90.0 0.0.0.255
ip nat inside source list 1 pool PUB
ip nat inside source static tcp 192.168.90.138 80 200.0.90.30 80
!
end
```

### 10.4 实验（二）Internet路由器与外网网络

```text
! ================= Internet路由器 =================
version 12.4
hostname Internet路由器
!
interface Serial0/0/0
 ip address 200.0.90.2 255.255.255.252
!
interface FastEthernet0/0
 ip address 200.0.90.9 255.255.255.248
!
ip route 200.0.90.16 255.255.255.240 200.0.90.1
!
end

! ================= 外网网络 =================
version 12.2
hostname 外网网络
!
vlan 10
 name outside
!
interface FastEthernet0/1
 switchport access vlan 10
 switchport mode access
!
interface FastEthernet0/2
 switchport access vlan 10
 switchport mode access
!
interface FastEthernet0/3
 switchport access vlan 10
 switchport mode access
!
end
```

> **注意**：PT 保存后 `show running-config` 里会出现大量 `interface FastEthernet0/x` + `!` 的空 stanza
> （2960/3560 有 26 个口，每个都列一行），这是正常的，不是配错了。
> 上面为了可读性只保留了有内容的部分。

---

## 结尾：做完了怎么交付

### 交付清单

| 序号 | 交付物 | 路径 |
|------|--------|------|
| 1 | 实验报告（Word） | `实验2\01-实验报告\90-实验二-ACL与NAT配置-实验报告.docx` |
| 2 | 本教程 | `实验2\02-新手教程\网络设备配置与管理-实验二（ACL与NAT）Packet Tracer 新手教程.md` |
| 3 | ACL 工程 | `实验2\03-工程文件\90-实验二一-ACL配置.pkt` |
| 4 | NAT 工程 | `实验2\03-工程文件\90-实验二二-NAT配置.pkt` |
| 5 | 生成脚本 | `实验2\04-脚本与软件\`（`build_report2.py`、`build_pkts2.py`、`pktbuild.py`、`pktlib.py`、`draw_figures2.py`、`verify_pkts2.py`、`pt_probe.py`、`force_save.py`） |
| 6 | 配图 | `实验2\06-图表与截图\fig1_acl.png`、`fig2_nat.png`、`fig_overview2.png` |
| 7 | 原始资料 | `实验2\05-原始资料\`（题目与两张拓扑原图） |

### 提交前最后三件事

1. **关掉 PT 再打开两个 `.pkt`**，确认标题栏有完整路径、设备都在、配置还在（`show run` 有内容）。
   如果配置没了，说明你改完没 `write`。
2. **把报告导出成 PDF 看一眼**（`File → 另存为 → PDF`），确认图片没有跑版、表格没有跨页断裂。
3. **对照第 8 章的自检清单逐条打勾**，特别是「ACL 之前先验证过全网通」和
   「NAT 实验里 ACL 已删掉」这两条——这是最容易漏、也最容易让实验结果对不上的两条。

### 关于两个现成工程文件

`实验2\03-工程文件\` 下的两个 `.pkt` 已经配好了全部内容，可以直接打开验证。
但**别只会打开它**：

| 用法 | 评价 |
|------|------|
| 打开它，跑一遍第 5.9 / 6.8 节的测试表，对照自己的结果 | ✅ 这是最快的自检方式 |
| 打开它，然后 `write erase` 清空配置，自己从头重配一遍 | ✅ **最好的练法** |
| 打开它，照着 `show run` 把命令抄到自己工程里 | ✅ 至少抄的过程能学到东西 |
| 改个名字直接交上去 | ❌ 老师一问「为什么要挂 out 不挂 in」就露馅 |
