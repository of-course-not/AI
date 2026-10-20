# 网络设备配置与管理 · 实验全流程教程（Packet Tracer 新手版）

> 配套文件：`网络设备配置与管理-实验报告（路由器配置与路由协议）.docx`、四个工程文件 `90-实验一~四-*.pkt`、`README-PKT.md`
> 本教程按"打开软件 → 拖设备 → 连线 → 敲命令 → 截图 → 填报告"的顺序写，每一步都给出**命令原文**和**怎么判断自己做对了**。
> 全篇 IP 统一使用 `192.168.90.0/24`（90 = 学号后两位）。如果你学号后两位不是 90，把文中所有 `90` 换成你的数字即可，其余结构不用改。
> 唯一无法照抄原图的地方：原图的 Cisco 2501 在 Packet Tracer 8.2.2 里已不存在，实验三统一用 2621XM + WIC-2T 替代，详见 3.1 的"机型替代说明"。

---

## 目录

- [0. 读前须知](#0-读前须知)
- [1. 环境准备与界面认识](#1-环境准备与界面认识)
- [2. 命名规范（先定规则再动手）](#2-命名规范先定规则再动手)
- [3. 通用基本功（四个实验都要用）](#3-通用基本功四个实验都要用)
- [4. 地址规划总表](#4-地址规划总表)
- [5. 实验一：路由器基本配置与单臂路由](#5-实验一路由器基本配置与单臂路由)
- [6. 实验二：静态路由与三层交换机](#6-实验二静态路由与三层交换机)
- [7. 实验三：RIP 路由协议（v1 / v2 / 关闭自动汇总）](#7-实验三rip-路由协议v1--v2--关闭自动汇总)
- [8. 实验四：OSPF 多区域](#8-实验四ospf-多区域)
- [9. 报告怎么写（对照模板逐格填）](#9-报告怎么写对照模板逐格填)
- [10. 自检清单（打分前必过）](#10-自检清单打分前必过)
- [11. 故障排查速查表](#11-故障排查速查表)
- [12. 附录：四份配置汇总（可直接对照）](#12-附录四份配置汇总可直接对照)
- [结尾：做完了怎么交付](#结尾做完了怎么交付)

---

## 0. 读前须知

### 0.1 这份实验到底要你做什么

长图作业一共四部分，每部分 2 学时，**四部分都要做、都要写进同一份报告**：

| 部分 | 内容 | 交付物 |
|---|---|---|
| 实验一 | 路由器基本配置（console、模式切换、环回/以太网/串行接口、telnet）+ **自设计拓扑的单臂路由**（≥2 个 VLAN 互通） | 拓扑图 + 配置命令 + 测试截图 |
| 实验二 | **三层交换机 + 静态路由**（按图 1 拓扑） | 同上 |
| 实验三 | **RIP**：先 RIPv1，再改 v2，再关自动汇总，三次测试（按图 2 拓扑） | 同上 + 三组对比 |
| 实验四 | **OSPF 多区域**（按图 3 拓扑） | 同上 + 实验结论 |

硬性要求：**所有 IP 地址必须包含学号后两位**。本教程把 90 放在第二段的最后一段（`192.168.90.x`），一眼就能被检查出来。

### 0.2 你需要准备什么

1. **Cisco Packet Tracer 8.x**（学校机房一般装 8.2 或 8.2.1）。版本差异不影响本实验，7.x 也能做。
2. 一份报告模板（学校发的"实验报告（实验一）.doc"），或直接用配套的 .docx。
3. 一个固定的工作文件夹，例如 `D:\网络实验\`。**所有 .pkt 文件、截图都放这里，不要放桌面或 C 盘根目录。**

### 0.3 时间预算（别拖到最后一天）

| 阶段 | 建议用时 | 说明 |
|---|---|---|
| 熟悉 PT 界面 + 连线 | 40 min | 第一次用会手忙脚乱，正常 |
| 实验一 | 60~90 min | 含单臂路由，最容易卡在子接口 |
| 实验二 | 60~90 min | 静态路由条数多，要细心 |
| 实验三 | 60 min | 三次测试，改动小 |
| 实验四 | 60~90 min | 六台路由器，命令重复度高 |
| 写报告 + 截图整理 | 90 min | 别留到最后，边做边截图 |

---

## 1. 环境准备与界面认识

### 1.1 打开软件，认识三个区域

启动 Packet Tracer 后，界面分三块：

```
┌──────────────────────────────────────────────┐
│  菜单栏 + 工具栏（上面两行）                  │
├──────────┬───────────────────────┬───────────┤
│ 设备区   │      工作区（画布）    │ 右侧面板  │
│ (左下)   │                       │ (选设备/  │
│          │                       │  改参数)  │
├──────────┴───────────────────────┴───────────┤
│  实时/仿真模式切换 + 时间轴（最下面一行）      │
└──────────────────────────────────────────────┘
```

- **设备区（左下）**：两排图标，上排是分类（路由器、交换机、终端、连接线……），下排是该分类下的具体型号。
- **工作区（中间）**：拖设备、连线、右键操作都在这里。
- **实时/仿真模式（右下）**：做本实验全程用**实时模式（Realtime）**，不要切到 Simulation，否则 ping 不会自己走，要点播放键。

### 1.2 关掉两个烦人的默认设置

**（1）关掉设备名下方的型号文字（可选，但截图更干净）**
`Options → Preferences → 取消勾选 "Show device model labels"`。

**（2）把工作区调大一点**
`Options → Preferences → Font/Colors` 里可以调字号；画布不够大就按住 `Ctrl` 滚轮缩放。

### 1.3 建工程文件的正确姿势

1. 先 `File → Save As`，立刻存一次空文件：`D:\网络实验\90-实验一-基本配置与单臂路由.pkt`
2. **每完成一个小阶段就按一次 `Ctrl+S`**。PT 崩溃一次能让你重做一小时。
3. 四个实验存**四个独立文件**，不要塞在一个 .pkt 里。原因：四个实验用的是同一段 `192.168.90.0/24`，放在一个文件里会地址冲突，而且老师检查时也分不清。

### 1.4 现成的四个工程文件（可对照，但别只会打开）

随本教程一起提供的还有四个已配好的工程文件，用 `File → Open` 直接打开：

```
90-实验一-路由器基本配置与单臂路由.pkt
90-实验二-静态路由与三层交换机.pkt
90-实验三-RIP路由协议.pkt
90-实验四-OSPF多区域.pkt
```

它们的设备名、接口名、端口号、IP 地址与第 4 章的地址规划表**完全一致**，DCE 端的 `clock rate` 也已配好，打开就能 ping 通。

**怎么用才不算偷懒**：

| 用法 | 评价 |
|---|---|
| 打开后先跑一遍第 10 章的自检清单，确认自己知道每个结果是怎么来的 | ✅ 推荐 |
| 打开后把某台设备的配置 `write erase` 掉，自己重配一遍，再和原文件比对 | ✅ 最好的练法 |
| 照着文件抄命令到自己新建的工程里 | ✅ 可行 |
| 直接改个名字交上去，答辩时说不清 `ip route` 的下一跳为什么是那个地址 | ❌ 一问就露馅 |

> 关于机型替代（2501→2621XM）和原图未画 PC 的处理，见工程文件同目录的 `README-PKT.md`，那里有完整的端口对照表。**这两件事在报告里要主动说明**，不要装作完全复刻了原图。

---

## 2. 命名规范（先定规则再动手）

命名不规范是"看起来做了但老师给低分"的头号原因。下面这套规则建议原样照抄。

### 2.1 设备命名（PT 里的 hostname）

| 设备类型 | 命名规则 | 举例 |
|---|---|---|
| 路由器 | `R` + 拓扑中的编号 | `R0`、`R1`、`R2`、`R3`、`R4`、`R5` |
| 三层交换机 | `SW` + 编号 | `SW0` |
| 二层交换机 | `SW` + 编号（与三层区分时加 `L2`） | `SW1`、`SW2` |
| PC | `PC-` + 位置/角色 | `PC-A`、`PC-B`、`PC0`、`PC1` |
| 特殊型号实验 | 型号 + 字母（RIP 实验用） | `2621A`、`2501A`、`2501B`、`2501C` |

规则要点：
- **只用字母、数字、连字符**，不要中文、不要空格（CLI 里打不出来）。
- hostname 一律小写或首字母大写，全篇统一。本教程用 `R0`/`SW0` 这种形式。
- PT 里拖出来的设备默认叫 `Router0`、`Switch0`、`PC0`，**必须在 CLI 里用 `hostname` 改掉**，光在 PT 面板上改显示名不算（那只改了标签，配置里还是 Router0，`show running-config` 一看就露馅）。

### 2.2 接口写法规范

| 设备 | 接口在 PT 里的名字 | 简写 | 报告里统一写成 |
|---|---|---|---|
| 1841 以太网 | `FastEthernet0/0` | `fa0/0` | `Fa0/0` |
| 1841 串行（需 WIC-2T） | `Serial0/0/0` | `s0/0/0` | `Se0/0/0` |
| 3560/2960 交换机 | `FastEthernet0/1` | `fa0/1` | `Fa0/1` |
| 2621XM 以太网 | `FastEthernet0/0` / `FastEthernet0/1` | `fa0/0` | `F0/0` |
| 2621XM 串行（需 WIC-2T） | `Serial0/0`、`Serial0/1`（插一块）；插两块是 `Serial0/0`～`Serial0/3` | `s0/0` | `S0/0` / `S0/1` |
| VLAN 接口（SVI） | `Vlan2` | `vlan 2` | `VLAN2` |
| 子接口 | `FastEthernet0/0.10` | `fa0/0.10` | `Fa0/0.10` |
| 环回 | `Loopback0` | `lo0` | `Lo0` |

**报告和截图里的接口名必须和 PT 里一致**，别一半写 `fa0/0` 一半写 `Fa0/0`。

### 2.3 IP 地址命名规范

- 每台设备的接口地址在报告里用 `设备 接口 = .末位` 的形式，例如 `R1 Fa0/0.10 = .1`。
- 网关统一取**网段的第一个可用地址**（.1 或 .65 或 .129 这种），PC 从 `.10` 开始往后排。
- 点对点链路用 `/30`，两端分别是 `.x` 和 `.x+1`（例如 `.129` 和 `.130`）。

### 2.4 文件与截图命名

| 类型 | 规则 | 举例 |
|---|---|---|
| 工程文件 | `学号后两位-实验序号-内容.pkt` | `90-实验二-静态路由.pkt` |
| 拓扑截图 | `图-实验X-拓扑.png` | `图-实验二-拓扑.png` |
| 命令截图 | `图-实验X-设备-命令.png` | `图-实验二-SW0-show-ip-route.png` |
| 测试截图 | `图-实验X-PC-ping-目标.png` | `图-实验二-PC0-ping-PC3.png` |

统一放 `D:\网络实验\截图\`，按实验分四个子文件夹。这样最后往 Word 里插图时不用满硬盘找。

### 2.5 报告里的图表编号规范

- 图：`图1`、`图2`……按出现顺序连续编号，**正文里必须先提到再出现**（"如图 2 所示"）。
- 表：`表1`、`表2`……同上。
- 图注写在图**下方**，表注写在表**上方**（这是国标习惯，本报告模板也是这么排的）。

---

## 3. 通用基本功（四个实验都要用）

### 3.1 设备怎么选（别选错型号）

| 需要什么 | 在设备区哪一排 | 选哪个 | 备注 |
|---|---|---|---|
| 带串行口的路由器（1841） | Routers | `1841` | 默认**没有** Serial 口，要加 WIC-2T |
| 带两个以太网口的路由器 | Routers | `2621XM` | 有 Fa0/0、Fa0/1；**不自带串口**，要用 Serial 得加 WIC-2T |
| 老式路由器（RIP 实验用） | Routers | 原图为 `2501`，**PT 8.2.2 已无此型号**，改用 `2621XM` + WIC-2T | 见下方"机型替代说明" |
| 三层交换机 | Switches → 最下面 | `3560-24PS` | 支持 `ip routing`、`no switchport` |
| 二层交换机 | Switches | `2960-24TT` 或 `2950-24` | 只能做二层 |
| PC | End Devices | `PC-PT` | |
| 串行线 | Connections | 红色闪电 `Serial DTE` | 两端都是串口时用 |

> **机型替代说明（实验三必读）**
> 原图 2 标的是 Cisco **2501**（E0 + S0 + S1）。Packet Tracer 8.2.2 的设备面板和帮助文档里**都没有 2501**（8.2.2 的路由器只有 ISR4321/4331、1941、2901、2911、819、829、CGR1240、Router-PT、1841、2620XM、2621XM、2811）。所以实验三统一用 **2621XM + 一块 WIC-2T** 替代，拓扑、地址、协议全部不变，只是接口名换了：
>
> | 原图标注 | 替代后实际输入 | 说明 |
> |---|---|---|
> | `Ethernet0`（E0） | `interface fastEthernet 0/0` | 2621XM 的两个以太口是 Fa0/0、Fa0/1 |
> | `Serial0`（S0） | `interface serial 0/0` | 插一块 WIC-2T 得到 Se0/0、Se0/1 |
> | `Serial1`（S1） | `interface serial 0/1` | 插两块 WIC-2T 才有 Se0/2、Se0/3 |
>
> 报告里为了和原图对应，设备名仍叫 `2501A/B/C`，但接口一律写替代后的真实名字。答辩被问到时按上表解释即可。

### 3.2 连线类型对照表（连错线不通，而且不报错）

| 两端设备 | 用什么线 | 图标 |
|---|---|---|
| 路由器 ↔ 交换机 | **直通线** Copper Straight-Through | 黑色实线 |
| 交换机 ↔ PC | **直通线** | 黑色实线 |
| 路由器 ↔ PC | **交叉线** Copper Cross-Over | 黑色虚线 |
| 交换机 ↔ 交换机（同型号） | **交叉线** | 黑色虚线 |
| 路由器 ↔ 路由器（以太网口） | **交叉线** | 黑色虚线 |
| 串行口 ↔ 串行口 | **Serial DTE** | 红色闪电 |
| PC ↔ 路由器 Console 口 | **Console 线**（浅蓝） | 蓝色曲线 |

> **重要**：PT 里较新的设备支持"自动翻转（Auto-MDIX）"，插错线也可能通，但**考试/答辩时按标准连线**，不要赌。串行线两端一个是 DCE 一个是 DTE，PT 会自动分配，**DCE 那一端要配 `clock rate`**（见 3.5）。

### 3.3 用 Console 线登录设备（本实验的起点）

1. 拖一台 PC 和一台路由器。
2. 在 Connections 里选**浅蓝色的 Console 线**，先点 PC，弹出菜单选 `RS-232`，再点路由器，选 `Console`。
3. 点 PC → 上方标签页 `Desktop` → 点 `Terminal`。
4. 弹出配置框，保持默认：`9600-8-N-1`，Flow Control 选 `None`，点 OK。
5. 按一下**回车**，出现 `Router>` 就成功了。

> 如果一片空白：再按一次回车；还是空白就是线接错了（接成了 Console 到 Console，或者接到了 Auxiliary 口）。

### 3.4 CLI 四种模式（必须背下来）

| 模式 | 提示符 | 怎么进去 | 能干什么 |
|---|---|---|---|
| 用户模式 | `Router>` | 登录后默认 | 只能看，不能改 |
| 特权模式 | `Router#` | `enable` | 看所有配置、保存、调试 |
| 全局配置模式 | `Router(config)#` | `configure terminal` | 改全局参数（hostname、路由、VLAN） |
| 接口配置模式 | `Router(config-if)#` | `interface fa0/0` | 配某个接口 |
| 子接口模式 | `Router(config-subif)#` | `interface fa0/0.10` | 配子接口 |
| 线路模式 | `Router(config-line)#` | `line vty 0 4` | 配 telnet |
| 路由协议模式 | `Router(config-router)#` | `router rip` / `router ospf 1` | 配动态路由 |

**退出的三种方式**：
- `exit`：退一级（接口 → 全局 → 特权）
- `end`（或 `Ctrl+Z`）：**从任何配置模式直接退回特权模式**
- `Ctrl+C`：强行中断当前命令

**常用快捷键**：

| 按键 | 作用 |
|---|---|
| `?` | 显示当前位置能用的命令/参数（最有用） |
| `Tab` | 补全命令 |
| `Ctrl+P` / `↑` | 上一条命令 |
| `Ctrl+A` | 光标到行首 |
| `Ctrl+U` | 删整行 |
| `do show ...` | 在配置模式下临时执行特权命令（如 `do show ip route`） |

### 3.5 给 1841 加串行模块（不加就没有 Serial 接口）

这是新手第一个大坑：直接敲 `interface serial 0/0/0` 会报 `Invalid input`。

**正确步骤**：
1. 点开 1841，出现物理面板图。
2. 面板右侧有一个**电源开关**（小圆点/拨动开关），**先点一下断电**（面板变暗）。
3. 在面板下方/右侧的模块列表里找到 **`WIC-2T`**（2 口串行模块）。
4. **把 WIC-2T 拖到路由器的空插槽上**（拖上去会有"咔"的吸附效果）。
5. **再点电源开关上电**。
6. 点 `CLI` 标签，敲 `show ip interface brief`，现在能看到 `Serial0/0/0`、`Serial0/0/1`。

> **2621XM 不自带串行口**，同样要加 WIC-2T：插一块得到 `Serial0/0`、`Serial0/1`，插两块得到 `Serial0/0`～`Serial0/3`。以太口是 `FastEthernet0/0`、`FastEthernet0/1`（**不是** `Ethernet0`，原图 2501 的 `Ethernet0` 在 PT 8.2.2 里已不存在）。

**DCE / DTE 与 clock rate**：
- 串行链路的两端，一端是 DCE（提供时钟），一端是 DTE。
- 在 PT 里把鼠标悬停在串行线两端，会显示 `DCE` 或 `DTE`；也可以在路由器上敲 `show controllers serial 0/0/0` 看。
- **DCE 那一端必须配 `clock rate 64000`**，否则接口状态是 `up/down`，链路永远起不来。
- 不知道哪端是 DCE？**两端都配上 `clock rate` 也不会报错**（DTE 端会提示不支持但不影响），这是最省事的做法。

### 3.6 四条"救命名令"

```cisco
show ip interface brief        ! 看所有接口的 IP、状态（up/up 才是好的）
show ip route                  ! 看路由表（C=直连 S=静态 R=RIP O=OSPF）
show running-config            ! 看当前配置（内存里的）
show startup-config            ! 看已保存的配置（NVRAM 里的）
```

保存配置：`copy running-config startup-config`（或简写 `write`）。
**不保存，PT 关掉再打开就全没了。**

### 3.7 PC 怎么配 IP 和测试

1. 点 PC → `Desktop` → `IP Configuration`。
2. 填 `IP Address`、`Subnet Mask`、`Default Gateway`（网关填对应路由器的接口地址）。
3. 关掉窗口。
4. 点 `Desktop` → `Command Prompt`，敲：
   - `ping 目标IP` —— 测通不通
   - `tracert 目标IP` —— 看经过几跳、路径对不对
   - `ipconfig` —— 复查自己配的地址

> ping 第一次可能丢 1 个包（ARP 解析），这是**正常现象**，不要以为配错了。等 5 秒再 ping 一次，全通就对了。
---

## 4. 地址规划总表

### 4.1 为什么这么规划（先讲清楚再动手）

作业要求"IP 地址必须包括自己的学号后两位"。最容易犯的错是把所有设备都写成 `192.168.90.x`——**同一网段内不能有重复地址，跨网段又必须换网络号**，所以正确做法是：

- 主网取 `192.168.90.0/24`，`90` 就是学号后两位，**第二段的最后一段**一眼可查。
- 再从这个 /24 里切子网：局域网段用 `/26`（64 个地址，够用且好算），点对点链路用 `/30`（4 个地址，只浪费 2 个）。

### 4.2 四个实验的地址总表

> 四个实验是**四个独立的 .pkt 文件**，所以它们可以复用同一段地址，互不影响。

**实验一（自设计单臂路由拓扑）**

| 网段 | 网络地址/掩码 | 设备与接口地址 | 对端/PC 地址 |
|---|---|---|---|
| VLAN10 | 192.168.90.0/26 | R1 Fa0/0.10 = .1 | PC-A = .10 |
| VLAN20 | 192.168.90.64/26 | R1 Fa0/0.20 = .65 | PC-B = .74 |
| R1—R2 | 192.168.90.128/30 | R1 Se0/0/0 = .129 | R2 Se0/0/0 = .130 |
| PC-C 段 | 192.168.90.132/30 | R2 Fa0/0 = .133 | PC-C = .134 |
| Loopback0 | 192.168.90.200/32 | R1 Lo0 = .200 | — |

**实验二（静态路由 + 三层交换机）**

| 网段 | 网络地址/掩码 | 设备与接口地址 | 对端/PC 地址 |
|---|---|---|---|
| VLAN2 | 192.168.90.0/26 | SW0 SVI VLAN2 = .1 | PC0 = .10 |
| VLAN3 | 192.168.90.64/26 | SW0 SVI VLAN3 = .65 | PC1 = .74 |
| SW0—R0 | 192.168.90.128/30 | SW0 Fa0/1 = .129 | R0 Fa0/0 = .130 |
| R0—PC4 | 192.168.90.132/30 | R0 Fa0/1 = .133 | PC4 = .134 |
| R0—R1 | 192.168.90.136/30 | R0 Se0/0/0 = .137 | R1 Se0/0/0 = .138 |
| R1—PC2 | 192.168.90.140/30 | R1 Fa0/0 = .141 | PC2 = .142 |
| R1—R2 | 192.168.90.144/30 | R1 Se0/0/1 = .145 | R2 Se0/0/0 = .146 |
| R2—PC3 | 192.168.90.148/30 | R2 Fa0/0 = .149 | PC3 = .150 |

**实验三（RIP）**

| 网段 | 网络地址/掩码 | 设备与接口地址 | 对端/PC 地址 |
|---|---|---|---|
| ① | 192.168.90.0/27 | 2621A F0/0 = .1 | 2501A F0/0 = .2 |
| ② | 192.168.90.32/27 | 2501A S0/0 = .33 | 2501B S0/0 = .34 |
| ③ | 192.168.90.64/27 | 2501B S0/1 = .65 | 2501C S0/0 = .66 |
| ④ | 192.168.90.96/27 | 2501B F0/0 = .97 | PC2 = .98 |
| ⑤ | 192.168.90.128/27 | 2501C F0/0 = .129 | PC1 = .130 |

> 表中 `2501A/B/C` 是**沿用原图的名字**，实际设备是 2621XM；`F0/0` 对应原图 `E0`，`S0/0` 对应原图 `S0`，`S0/1` 对应原图 `S1`（详见 3.1 的机型替代说明）。

> **为什么 RIP 用 /27 而不是 /26？** RIPv1 是"有类"协议，路由更新里**不带掩码**，接收方按主类网络（/24）推断。同一个 192.168.90.0 主网内如果混用 /26 和 /30，接收方会把掩码算错，路由学不对。5 个 /26 又超过了一个 /24 的容量，所以统一用 /27（每个 32 个地址，5 个刚好占满 0/32/64/96/128 五块）。

**实验四（OSPF 多区域）**

| 区域/链路 | 网络地址/掩码 | 设备与接口地址 | 对端/PC 地址 |
|---|---|---|---|
| Area0 LAN | 192.168.90.0/26 | R0 Fa0/0 = .1 | PC0 = .10 |
| Area1 LAN | 192.168.90.64/26 | R1 = .65，R2 = .66 | PC1 = .74 |
| Area2 LAN | 192.168.90.128/26 | R3 .129，R4 .130，R5 .131 | PC2 = .138 |
| R0—R3 | 192.168.90.192/30 | R0 = .193 | R3 = .194 |
| R0—R1 | 192.168.90.196/30 | R0 = .197 | R1 = .198 |
| R3—R1 | 192.168.90.200/30 | R3 = .201 | R1 = .202 |

### 4.3 子网速查（/26 与 /30）

**/26（255.255.255.192）**：每块 64 个地址，可用 62 个。

| 子网 | 网络地址 | 可用范围 | 广播地址 |
|---|---|---|---|
| 0 | 192.168.90.0 | .1 ~ .62 | .63 |
| 1 | 192.168.90.64 | .65 ~ .126 | .127 |
| 2 | 192.168.90.128 | .129 ~ .190 | .191 |
| 3 | 192.168.90.192 | .193 ~ .254 | .255 |

**/30（255.255.255.252）**：每块 4 个地址，可用 2 个（正好点对点两端）。

| 子网 | 网络地址 | 可用 | 广播 |
|---|---|---|---|
| .128 | 192.168.90.128 | .129 / .130 | .131 |
| .132 | 192.168.90.132 | .133 / .134 | .135 |
| .136 | 192.168.90.136 | .137 / .138 | .139 |
| .140 | 192.168.90.140 | .141 / .142 | .143 |
| .144 | 192.168.90.144 | .145 / .146 | .147 |
| .148 | 192.168.90.148 | .149 / .150 | .151 |
| .192 | 192.168.90.192 | .193 / .194 | .195 |
| .196 | 192.168.90.196 | .197 / .198 | .199 |
| .200 | 192.168.90.200 | .201 / .202 | .203 |

**/27（255.255.255.224）**：每块 32 个地址，可用 30 个。

| 子网 | 网络地址 | 可用范围 | 广播 |
|---|---|---|---|
| 0 | 192.168.90.0 | .1 ~ .30 | .31 |
| 1 | 192.168.90.32 | .33 ~ .62 | .63 |
| 2 | 192.168.90.64 | .65 ~ .94 | .95 |
| 3 | 192.168.90.96 | .97 ~ .126 | .127 |
| 4 | 192.168.90.128 | .129 ~ .158 | .159 |

---

## 5. 实验一：路由器基本配置与单臂路由

### 5.0 本实验要达成的 8 个目标（做完逐条打勾）

- [ ] 用 Console 线登录路由器，能在四种模式间自由切换
- [ ] 配好 hostname、clock、banner，会 `copy` 保存，会 `show running-config`、`show ip route`
- [ ] 配好 Loopback0、Fa0/0、Serial0/0/0 三类接口，并用 `show ip route` 看到直连路由
- [ ] 用 telnet 从 PC 远程登录路由器成功
- [ ] 自己画一个含 2 个 VLAN 的拓扑，交换机侧配 Trunk
- [ ] 路由器侧配两个 dot1Q 子接口，VLAN 间能互通
- [ ] 两张 PC 能 ping 通（截图留证）
- [ ] 配置步骤写进报告

### 5.1 搭拓扑（照这张表拖设备、连线）

| 设备 | 型号 | 数量 |
|---|---|---|
| 路由器 | 1841 | 2（R1、R2） |
| 二层交换机 | 2960-24TT | 1（SW1） |
| PC | PC-PT | 3（PC-A、PC-B、PC-C） |

连线：

| 起点 | 终点 | 线型 |
|---|---|---|
| SW1 Fa0/1 | PC-A Fa0 | 直通线 |
| SW1 Fa0/2 | PC-B Fa0 | 直通线 |
| SW1 Fa0/24 | R1 Fa0/0 | 直通线 |
| R1 Se0/0/0 | R2 Se0/0/0 | Serial DTE（红闪电） |
| R2 Fa0/0 | PC-C Fa0 | 交叉线 |
| PC-A RS-232 | R1 Console | Console 线（蓝） |

> **R1、R2 都要先断电加 WIC-2T 再上电**（见 3.5）。R2 只用到 Fa0/0 和 Se0/0/0。

**检查**：所有链路两端小三角变**绿色**才算通。串行线如果一端红一端绿，说明 DCE 端没配 `clock rate`（配置时补上即可，此时先不管）。

### 5.2 配 R1：模式切换 + 基本配置

在 PC-A 的 Terminal 里操作：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname R1
R1(config)# no ip domain-lookup
R1(config)# clock timezone CST 8
R1(config)# clock set 10:00:00 18 oct 2026
R1(config)# banner motd #Welcome to R1, authorized access only!#
R1(config)# exit
R1# copy running-config startup-config
Destination filename [startup-config]? （直接回车）
R1# show running-config
R1# show ip route
```

**自检**：
- 提示符从 `Router>` 变成 `R1(config)#`，说明 hostname 生效。
- `show running-config` 的第一行应该是 `hostname R1`，**不是 `hostname Router`**。
- 此时 `show ip route` 只有一行 `Gateway of last resort is not set`，还没有任何路由——因为接口还没配地址，**这是对的**。

> `no ip domain-lookup` 一定要加。不加的话，你敲错一个命令，路由器会以为你要 telnet 一个主机名，卡在那里等 DNS 超时（约 30 秒），非常难受。

### 5.3 配 R1：三类接口

```cisco
R1(config)# interface loopback 0
R1(config-if)# ip address 192.168.90.200 255.255.255.255
R1(config-if)# exit

R1(config)# interface fastEthernet 0/0
R1(config-if)# no shutdown
R1(config-if)# exit

R1(config)# interface serial 0/0/0
R1(config-if)# ip address 192.168.90.129 255.255.255.252
R1(config-if)# clock rate 64000
R1(config-if)# no shutdown
R1(config-if)# end

R1# show ip interface brief
R1# show ip route
```

**自检**：
- `show ip interface brief` 里 `FastEthernet0/0` 和 `Serial0/0/0` 的 Status 和 Protocol 都必须是 **up / up**。
- `show ip route` 应该出现两条 `C`（connected）路由：
  - `C 192.168.90.128/30 is directly connected, Serial0/0/0`
  - `C 192.168.90.200/32 is directly connected, Loopback0`
- Fa0/0 现在没配 IP，所以**不会**出现 VLAN10 的直连路由，这是正常的（5.5 会配子接口）。

> **关键概念**：直连路由出现的条件 = 接口 `up/up` **且** 配了 IP 地址。少了任何一个，`show ip route` 里就没有这条。这是后面所有排错的出发点。

### 5.4 配 SW1：VLAN + Trunk

点 SW1 → CLI：

```cisco
Switch> enable
Switch# configure terminal
Switch(config)# hostname SW1
SW1(config)# vlan 10
SW1(config-vlan)# name vlan10
SW1(config-vlan)# vlan 20
SW1(config-vlan)# name vlan20
SW1(config-vlan)# exit

SW1(config)# interface fastEthernet 0/1
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# interface fastEthernet 0/2
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 20

SW1(config-if)# interface fastEthernet 0/24
SW1(config-if)# switchport mode trunk
SW1(config-if)# end

SW1# show vlan brief
SW1# show interfaces trunk
```

**自检**：
- `show vlan brief`：VLAN10 下面有 `Fa0/1`，VLAN20 下面有 `Fa0/2`，**Fa0/24 不在任何 VLAN 的列表里**（因为它是 trunk）。
- `show interfaces trunk`：能看到 `Fa0/24`，`Encapsulation dot1q`，`Vlans allowed on trunk: 1-1005`。

> 交换机端口默认是 `dynamic auto`，如果两端都是 auto，协商结果是 access，Trunk 起不来。所以**至少一端要手工 `switchport mode trunk`**，本实验在 SW1 上配。

### 5.5 配 R1：单臂路由子接口

```cisco
R1(config)# interface fastEthernet 0/0
R1(config-if)# no shutdown
R1(config-if)# exit

R1(config)# interface fastEthernet 0/0.10
R1(config-subif)# encapsulation dot1Q 10
R1(config-subif)# ip address 192.168.90.1 255.255.255.192
R1(config-subif)# exit

R1(config)# interface fastEthernet 0/0.20
R1(config-subif)# encapsulation dot1Q 20
R1(config-subif)# ip address 192.168.90.65 255.255.255.192
R1(config-subif)# end

R1# show ip route
R1# show ip interface brief
```

**自检**：
- `show ip route` 现在多了两条：
  - `C 192.168.90.0/26 is directly connected, FastEthernet0/0.10`
  - `C 192.168.90.64/26 is directly connected, FastEthernet0/0.20`
- `show ip interface brief` 里 `FastEthernet0/0.10`、`FastEthernet0/0.20` 都是 up/up。

**三个必须记住的点**：
1. **先 `no shutdown` 物理接口**，再配子接口。物理接口 down 着，子接口全 down。
2. `encapsulation dot1Q 10` 里的 `10` 必须和 VLAN 号一致，写错 VLAN 就通不了。
3. **子接口的 IP 就是这个 VLAN 里 PC 的网关**，PC-A 网关填 `.1`，PC-B 网关填 `.65`。

### 5.6 配 R2（为后面的跨设备测试准备）

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname R2
R2(config)# no ip domain-lookup
R2(config)# interface fastEthernet 0/0
R2(config-if)# ip address 192.168.90.133 255.255.255.252
R2(config-if)# no shutdown
R2(config-if)# interface serial 0/0/0
R2(config-if)# ip address 192.168.90.130 255.255.255.252
R2(config-if)# no shutdown
R2(config-if)# end
R2# show ip interface brief
R2# show ip route
```

**自检**：R2 上应有两条 C 路由（.128/30 和 .132/30）。**此时 R1 和 R2 之间还 ping 不通对方的远端网段**，因为还没有路由（下一步配）。

### 5.7 配 PC 地址

| PC | IP | 掩码 | 网关 |
|---|---|---|---|
| PC-A | 192.168.90.10 | 255.255.255.192 | 192.168.90.1 |
| PC-B | 192.168.90.74 | 255.255.255.192 | 192.168.90.65 |
| PC-C | 192.168.90.134 | 255.255.255.252 | 192.168.90.133 |

> 注意 PC-A 和 PC-B 的掩码是 **/26 = 255.255.255.192**，PC-C 是 **/30 = 255.255.255.252**。填错掩码是新手最常见的不通原因之一。

### 5.8 测试一：VLAN 间互通（单臂路由的核心）

PC-A 的 Command Prompt：

```
ping 192.168.90.74
```

**预期结果**：
- 第一次可能 `Request timed out`（ARP），再 ping 一次应全通。
- 通的标志：`Reply from 192.168.90.74: bytes=32 time<1ms TTL=127`。
- **TTL=127** 说明经过了 1 台路由器（128 - 1），这正是单臂路由在起作用。

**如果不通，按顺序查**：
1. `show ip interface brief`（R1）—— 两个子接口是否 up/up
2. `show vlan brief`（SW1）—— Fa0/1 在 VLAN10、Fa0/2 在 VLAN20？
3. `show interfaces trunk`（SW1）—— Fa0/24 是 trunk？
4. PC 的掩码和网关是否填对
5. 子接口的 `encapsulation dot1Q` 编号是否和 VLAN 号一致

### 5.9 测试二：跨路由器（此时应该不通，这是故意的）

PC-A 上：

```
ping 192.168.90.134
```

**预期：Request timed out。** 原因是 R2 不知道 `192.168.90.0/26`、`192.168.90.64/26` 在哪，R1 也不知道 `192.168.90.132/30` 在哪。**这正是"路由表里没有条目就不通"的最好证据**，报告里要写这个现象。

### 5.10 补路由打通，再测试

```cisco
R1(config)# ip route 192.168.90.132 255.255.255.252 192.168.90.130

R2(config)# ip route 192.168.90.0 255.255.255.192 192.168.90.129
R2(config)# ip route 192.168.90.64 255.255.255.192 192.168.90.129
```

再在 PC-A 上 `ping 192.168.90.134`：

**预期**：`Reply from 192.168.90.134: bytes=32 time<1ms TTL=126`。
**TTL=126** 说明经过 2 台路由器（128 - 2），和拓扑一致。**这个 TTL 变化是报告里最有说服力的证据**，一定要截图。

### 5.11 配 telnet 远程管理

```cisco
R1(config)# enable secret cisco123
R1(config)# line vty 0 4
R1(config-line)# password telnet123
R1(config-line)# login
R1(config-line)# transport input telnet
R1(config-line)# end
R1# copy running-config startup-config
```

**测试**：PC-A 的 Command Prompt：

```
telnet 192.168.90.1
```

- 提示 `Password:` → 输入 `telnet123`（**输入时屏幕不显示，正常**）
- 进入 `R1>` → 敲 `enable` → 提示 `Password:` → 输入 `cisco123`
- 变成 `R1#`，说明远程管理配置成功

**如果 telnet 不通**：
1. R1 上有没有配 `enable secret` 或 `enable password`？**没有特权密码，telnet 登录会被拒绝**（提示 `Password required, but none set`）。
2. `line vty 0 4` 下有没有 `password` 和 `login`？两个都要有。
3. PC-A 的网关是不是 `.1`？

> `enable secret` 和 `enable password` 二选一即可，**`secret` 优先且加密存储**，推荐用 `secret`。两个都配时 `secret` 生效。

### 5.12 本实验的截图清单（报告要用）

| 序号 | 截什么 | 在哪截 |
|---|---|---|
| 1 | 拓扑全图（带设备名和绿色链路） | 画布 |
| 2 | `show running-config` 前 20 行 | R1 CLI |
| 3 | `show ip route`（含 4 条直连） | R1 CLI |
| 4 | `show vlan brief` | SW1 CLI |
| 5 | `show interfaces trunk` | SW1 CLI |
| 6 | PC-A ping PC-B 通（TTL=127） | PC-A CMD |
| 7 | PC-A ping PC-C 不通（Request timed out） | PC-A CMD |
| 8 | PC-A ping PC-C 通（TTL=126） | PC-A CMD |
| 9 | telnet 登录成功（出现 R1#） | PC-A CMD |
---

## 6. 实验二：静态路由与三层交换机

### 6.0 本实验要达成的目标

- [ ] 三层交换机开 `ip routing`，建 VLAN2/VLAN3，Fa0/2 进 VLAN2、Fa0/3 进 VLAN3
- [ ] 配两个 SVI（VLAN2、VLAN3）作为网关
- [ ] Fa0/1 改成三层口（`no switchport`）并配地址
- [ ] 三层交换机上配 5 条静态路由
- [ ] 三台路由器各配静态路由（或默认路由）
- [ ] 5 台 PC 配好地址和网关
- [ ] 全网两两互 ping 通，`tracert` 路径与拓扑一致

### 6.1 搭拓扑

| 设备 | 型号 | 数量 | 说明 |
|---|---|---|---|
| 三层交换机 | **3560-24PS** | 1（SW0） | 必须是 3560，不能用 2960 |
| 路由器 | 1841 | 3（R0、R1、R2） | 都要加 WIC-2T |
| PC | PC-PT | 5（PC0~PC4） | |

连线：

| 起点 | 终点 | 线型 | 注意 |
|---|---|---|---|
| SW0 Fa0/1 | R0 Fa0/0 | 直通线 | SW0 侧要 `no switchport` |
| SW0 Fa0/2 | PC0 Fa0 | 直通线 | 划入 VLAN2 |
| SW0 Fa0/3 | PC1 Fa0 | 直通线 | 划入 VLAN3 |
| R0 Fa0/1 | PC4 Fa0 | **交叉线** | 路由器直连 PC |
| R0 Se0/0/0 | R1 Se0/0/0 | Serial DTE | |
| R1 Fa0/0 | PC2 Fa0 | **交叉线** | |
| R1 Se0/0/1 | R2 Se0/0/0 | Serial DTE | |
| R2 Fa0/0 | PC3 Fa0 | **交叉线** | |

> **为什么路由器直连 PC 要用交叉线？** 路由器的以太网口和 PC 的网卡都是"同类设备"（都做 MDI 引脚定义），同类之间要交叉。而路由器 ↔ 交换机是异类，用直通。PT 有 Auto-MDIX 可能容错，但按标准来。

### 6.2 配 SW0（三层交换机，最容易漏 `ip routing`）

```cisco
Switch> enable
Switch# configure terminal
Switch(config)# hostname SW0
SW0(config)# ip routing
SW0(config)# vlan 2
SW0(config-vlan)# name vlan2
SW0(config-vlan)# vlan 3
SW0(config-vlan)# name vlan3
SW0(config-vlan)# exit

SW0(config)# interface fastEthernet 0/2
SW0(config-if)# switchport mode access
SW0(config-if)# switchport access vlan 2
SW0(config-if)# interface fastEthernet 0/3
SW0(config-if)# switchport mode access
SW0(config-if)# switchport access vlan 3
SW0(config-if)# exit

SW0(config)# interface vlan 2
SW0(config-if)# ip address 192.168.90.1 255.255.255.192
SW0(config-if)# no shutdown
SW0(config-if)# interface vlan 3
SW0(config-if)# ip address 192.168.90.65 255.255.255.192
SW0(config-if)# no shutdown
SW0(config-if)# exit

SW0(config)# interface fastEthernet 0/1
SW0(config-if)# no switchport
SW0(config-if)# ip address 192.168.90.129 255.255.255.252
SW0(config-if)# no shutdown
SW0(config-if)# end

SW0# show ip interface brief
SW0# show ip route
```

**自检**：
- `show ip interface brief` 应该有 3 个 up/up：`Vlan2`、`Vlan3`、`FastEthernet0/1`，加一个 `Vlan1`（默认存在，down 着，不用管）。
- `show ip route` 应有 3 条 C 路由：`192.168.90.0/26`、`192.168.90.64/26`、`192.168.90.128/30`。

**三个高频坑**：

| 现象 | 原因 | 解决 |
|---|---|---|
| `ip routing` 报错 / 没有该命令 | 选成了 2960（二层交换机） | 换 3560-24PS |
| VLAN2 显示 `down/down` | 该 VLAN 内没有 up 的端口 | 检查 Fa0/2 是否接 PC 且 PC 已开机 |
| `no switchport` 报错 | 该口是路由口或已被占用 | 先 `switchport` 再 `no switchport`，或换口 |

> **SVI 的 up 条件**：VLAN 内至少有一个物理端口 up。所以 Fa0/2/Fa0/3 必须接上 PC 并开机，否则 VLAN2/VLAN3 的 SVI 是 down 的，网关不生效。

### 6.3 配三台路由器

**R0**（三个接口 + 5 条静态路由）：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname R0
R0(config)# no ip domain-lookup
R0(config)# interface fastEthernet 0/0
R0(config-if)# ip address 192.168.90.130 255.255.255.252
R0(config-if)# no shutdown
R0(config-if)# interface fastEthernet 0/1
R0(config-if)# ip address 192.168.90.133 255.255.255.252
R0(config-if)# no shutdown
R0(config-if)# interface serial 0/0/0
R0(config-if)# ip address 192.168.90.137 255.255.255.252
R0(config-if)# clock rate 64000
R0(config-if)# no shutdown
R0(config-if)# exit

R0(config)# ip route 192.168.90.0 255.255.255.192 192.168.90.129
R0(config)# ip route 192.168.90.64 255.255.255.192 192.168.90.129
R0(config)# ip route 192.168.90.140 255.255.255.252 192.168.90.138
R0(config)# ip route 192.168.90.144 255.255.255.252 192.168.90.138
R0(config)# ip route 192.168.90.148 255.255.255.252 192.168.90.138
R0(config)# end
R0# show ip route
```

**R1**（三个接口 + 5 条静态路由）：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname R1
R1(config)# no ip domain-lookup
R1(config)# interface serial 0/0/0
R1(config-if)# ip address 192.168.90.138 255.255.255.252
R1(config-if)# no shutdown
R1(config-if)# interface fastEthernet 0/0
R1(config-if)# ip address 192.168.90.141 255.255.255.252
R1(config-if)# no shutdown
R1(config-if)# interface serial 0/0/1
R1(config-if)# ip address 192.168.90.145 255.255.255.252
R1(config-if)# clock rate 64000
R1(config-if)# no shutdown
R1(config-if)# exit

R1(config)# ip route 192.168.90.0 255.255.255.192 192.168.90.137
R1(config)# ip route 192.168.90.64 255.255.255.192 192.168.90.137
R1(config)# ip route 192.168.90.128 255.255.255.252 192.168.90.137
R1(config)# ip route 192.168.90.132 255.255.255.252 192.168.90.137
R1(config)# ip route 192.168.90.148 255.255.255.252 192.168.90.146
R1(config)# end
R1# show ip route
```

**R2**（两个接口 + 默认路由）：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname R2
R2(config)# no ip domain-lookup
R2(config)# interface serial 0/0/0
R2(config-if)# ip address 192.168.90.146 255.255.255.252
R2(config-if)# no shutdown
R2(config-if)# interface fastEthernet 0/0
R2(config-if)# ip address 192.168.90.149 255.255.255.252
R2(config-if)# no shutdown
R2(config-if)# exit
R2(config)# ip route 0.0.0.0 0.0.0.0 192.168.90.145
R2(config)# end
R2# show ip route
```

**为什么要一条默认路由？** R2 是末端路由器，只有一条出口（.145 去 R1），所以 `0.0.0.0/0` 一条顶多条，比写 6 条静态路由简洁。`show ip route` 里显示为 `S* 0.0.0.0/0`，那个 `*` 表示"候选默认路由"。

### 6.4 SW0 上的静态路由（最容易漏）

```cisco
SW0(config)# ip route 192.168.90.132 255.255.255.252 192.168.90.130
SW0(config)# ip route 192.168.90.136 255.255.255.252 192.168.90.130
SW0(config)# ip route 192.168.90.140 255.255.255.252 192.168.90.130
SW0(config)# ip route 192.168.90.144 255.255.255.252 192.168.90.130
SW0(config)# ip route 192.168.90.148 255.255.255.252 192.168.90.130
SW0(config)# end
SW0# show ip route
```

> **为什么下一跳都是 .130？** 因为 SW0 只有一个出口（Fa0/1 接 R0），所有非直连网段都得先交给 R0。这也是为什么可以偷懒写成 `ip route 0.0.0.0 0.0.0.0 192.168.90.130`——但**作业要求练 `ip route 目的网络 掩码 下一跳` 的完整写法，所以按上面写全**。

### 6.5 配 PC

| PC | IP | 掩码 | 网关 |
|---|---|---|---|
| PC0 | 192.168.90.10 | 255.255.255.192 | 192.168.90.1 |
| PC1 | 192.168.90.74 | 255.255.255.192 | 192.168.90.65 |
| PC2 | 192.168.90.142 | 255.255.255.252 | 192.168.90.141 |
| PC3 | 192.168.90.150 | 255.255.255.252 | 192.168.90.149 |
| PC4 | 192.168.90.134 | 255.255.255.252 | 192.168.90.133 |

### 6.6 测试（这是本实验的得分点）

**测试 1：VLAN 间（PC0 → PC1）**

```
ping 192.168.90.74
```
预期：`Reply ... TTL=127`（经过 SW0 的三层转发，1 跳）

**测试 2：VLAN2 → PC4**

```
ping 192.168.90.134
```
预期：`TTL=126`（SW0 → R0，2 跳）

**测试 3：VLAN2 → PC2**

```
ping 192.168.90.142
```
预期：`TTL=125`（SW0 → R0 → R1，3 跳）

**测试 4：VLAN2 → PC3（最远端）**

```
ping 192.168.90.150
```
预期：`TTL=124`（SW0 → R0 → R1 → R2，4 跳）

**测试 5：看路径**

```
tracert 192.168.90.150
```
预期输出（逐跳）：

```
1   192.168.90.1      （SW0 的 VLAN2 SVI）
2   192.168.90.130    （R0 Fa0/0）
3   192.168.90.137    （R0 Se0/0/0）
4   192.168.90.138    （R1 Se0/0/0）
5   192.168.90.145    （R1 Se0/0/1）
6   192.168.90.146    （R2 Se0/0/0）
7   192.168.90.149    （R2 Fa0/0）
8   192.168.90.150    （PC3）
```

**这张 tracert 截图是全篇最有价值的证据**，它把拓扑结构、路由表、下一跳关系全部串起来了。报告里必须放。

### 6.7 全网两两互 ping（报告要列表）

建议做一张 5×5 的测试表，全部打 ✅：

| 源\目的 | PC0 | PC1 | PC2 | PC3 | PC4 |
|---|---|---|---|---|---|
| PC0 | — | ✅ | ✅ | ✅ | ✅ |
| PC1 | ✅ | — | ✅ | ✅ | ✅ |
| PC2 | ✅ | ✅ | — | ✅ | ✅ |
| PC3 | ✅ | ✅ | ✅ | — | ✅ |
| PC4 | ✅ | ✅ | ✅ | ✅ | — |

> 做这张表的时候，**注意 ping 的是对方的 IP**（表里填 IP 更严谨），不要只写"通"。

### 6.8 本实验截图清单

| 序号 | 截什么 |
|---|---|
| 1 | 拓扑全图 |
| 2 | SW0 `show ip route`（4 条 C + 5 条 S） |
| 3 | R0 `show ip route`（3 条 C + 5 条 S） |
| 4 | R2 `show ip route`（2 条 C + 1 条 S*） |
| 5 | PC0 ping PC1（TTL=127） |
| 6 | PC0 ping PC3（TTL=124） |
| 7 | PC0 `tracert 192.168.90.150`（8 跳） |
| 8 | 5×5 测试表（可以自己画一张截图，或直接写进报告） |

---

## 7. 实验三：RIP 路由协议（v1 / v2 / 关闭自动汇总）

### 7.0 本实验要达成的目标

- [ ] 按图 2 拓扑搭好 4 台路由器（2621A、2501A、2501B、2501C）+ 2 台 PC
- [ ] 全部配 RIPv1（`router rip` + `network`），测试全网通
- [ ] 改成 RIPv2（`version 2`），测试全网通，观察路由表变化
- [ ] 关闭自动汇总（`no auto-summary`），测试全网通，观察路由表变化
- [ ] 把三次的 `show ip route` 对比写进报告

### 7.1 搭拓扑

| 设备 | 型号 | 数量 | 说明 |
|---|---|---|---|
| 路由器 | **2621XM** | 1（2621A） | 有 Fa0/0、Fa0/1，不需要串口 |
| 路由器 | **2621XM** | 3（2501A、2501B、2501C） | **原图为 2501，PT 8.2.2 无此型号**，用 2621XM + WIC-2T 替代；以太口 `Fa0/0`，串口 `Serial0/0`/`Serial0/1` |
| PC | PC-PT | 2（PC1、PC2） | |

连线：

| 起点 | 终点 | 线型 |
|---|---|---|
| 2621A F0/0 | 2501A F0/0（原图 E0） | **交叉线**（路由器 ↔ 路由器） |
| 2501A S0/0（原图 S0） | 2501B S0/0 | Serial DTE |
| 2501B S0/1（原图 S1） | 2501C S0/0 | Serial DTE |
| 2501B F0/0（原图 E0） | PC2 Fa0 | **交叉线** |
| 2501C F0/0（原图 E0） | PC1 Fa0 | **交叉线** |

> **2621XM 要加 WIC-2T**（关机 → 拖 WIC-2T 进空槽 → 开机），加完才有 `Serial0/0`、`Serial0/1`。以太口名是 `FastEthernet0/0`，不是 `Ethernet0`；串口名是 `Serial0/0`，不是 `Serial0`。按原图的 `interface ethernet 0` / `interface serial 0` 敲会报 `Invalid interface`。

### 7.2 配地址（先配完地址再配 RIP）

**2621A**：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname 2621A
2621A(config)# no ip domain-lookup
2621A(config)# interface fastEthernet 0/0
2621A(config-if)# ip address 192.168.90.1 255.255.255.224
2621A(config-if)# no shutdown
2621A(config-if)# end
2621A# show ip interface brief
```

**2501A**：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname 2501A
2501A(config)# no ip domain-lookup
2501A(config)# interface fastEthernet 0/0
2501A(config-if)# ip address 192.168.90.2 255.255.255.224
2501A(config-if)# no shutdown
2501A(config-if)# interface serial 0/0
2501A(config-if)# ip address 192.168.90.33 255.255.255.224
2501A(config-if)# clock rate 64000
2501A(config-if)# no shutdown
2501A(config-if)# end
2501A# show ip interface brief
```

**2501B**（三个接口）：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname 2501B
2501B(config)# no ip domain-lookup
2501B(config)# interface serial 0/0
2501B(config-if)# ip address 192.168.90.34 255.255.255.224
2501B(config-if)# no shutdown
2501B(config-if)# interface serial 0/1
2501B(config-if)# ip address 192.168.90.65 255.255.255.224
2501B(config-if)# clock rate 64000
2501B(config-if)# no shutdown
2501B(config-if)# interface fastEthernet 0/0
2501B(config-if)# ip address 192.168.90.97 255.255.255.224
2501B(config-if)# no shutdown
2501B(config-if)# end
2501B# show ip interface brief
```

**2501C**：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname 2501C
2501C(config)# no ip domain-lookup
2501C(config)# interface serial 0/0
2501C(config-if)# ip address 192.168.90.66 255.255.255.224
2501C(config-if)# no shutdown
2501C(config-if)# interface fastEthernet 0/0
2501C(config-if)# ip address 192.168.90.129 255.255.255.224
2501C(config-if)# no shutdown
2501C(config-if)# end
2501C# show ip interface brief
```

**PC**：

| PC | IP | 掩码 | 网关 |
|---|---|---|---|
| PC2 | 192.168.90.98 | 255.255.255.224 | 192.168.90.97 |
| PC1 | 192.168.90.130 | 255.255.255.224 | 192.168.90.129 |

> 所有掩码都是 **/27 = 255.255.255.224**，全篇统一。这一步填错，后面 RIP 测试会莫名其妙不通。

### 7.3 阶段一：配 RIPv1

四台路由器都执行（只改 hostname 部分）：

```cisco
2621A(config)# router rip
2621A(config-router)# network 192.168.90.0
2621A(config-router)# end

2501A(config)# router rip
2501A(config-router)# network 192.168.90.0

2501B(config)# router rip
2501B(config-router)# network 192.168.90.0

2501C(config)# router rip
2501C(config-router)# network 192.168.90.0
```

**关键点**：RIPv1 的 `network` 后面**只写主类网络号**（`192.168.90.0`），**不能写子网**（写 `192.168.90.32` 会被自动改成主类）。这是 RIPv1 的有类特性。

**等待 30 秒**（RIP 每 30 秒发一次更新），然后测试：

```cisco
2501B# show ip protocols
2501B# show ip route
```

**预期 `show ip protocols` 输出**：
```
Routing Protocol is "rip"
Sending updates every 30 seconds, next due in ...
Default version control: send version 1, receive version 1
  Interface        Send  Recv  Triggered RIP  Key-chain
  Serial0/0        1     1
  Serial0/1        1     1
  FastEthernet0/0  1     1
Automatic network summarization is in effect
```

**预期 `show ip route`（RIPv1）**：
```
R    192.168.90.0/24 [120/1] via 192.168.90.33, 00:00:12, Serial0/0
```

**注意看**：学到的路由是 **`/24`**，不是 `/27`！这就是 RIPv1 的自动汇总——它在主网边界把所有子网汇总成一条 `192.168.90.0/24`。

**PC 测试**：
```
PC1> ping 192.168.90.98
Reply from 192.168.90.98: bytes=32 time<1ms TTL=126
```
TTL=126 表示经过 2 台路由器（PC1 → 2501C → 2501B → PC2）。**每经过一台路由器减 1，交换机不减**，所以 `跳数 = 128 - TTL`。

**截图**：`show ip protocols` + `show ip route` + ping 结果，三张。

### 7.4 阶段二：改成 RIPv2

四台路由器都执行：

```cisco
2621A(config)# router rip
2621A(config-router)# version 2
2621A(config-router)# end

2501A(config)# router rip
2501A(config-router)# version 2

2501B(config)# router rip
2501B(config-router)# version 2

2501C(config)# router rip
2501C(config-router)# version 2
```

**再等 30 秒**，然后：

```cisco
2501B# show ip protocols
2501B# show ip route
```

**预期 `show ip protocols`**：
```
Default version control: send version 2, receive version 2
```

**预期 `show ip route`**：
```
R    192.168.90.0/27 [120/1] via 192.168.90.33, 00:00:05, Serial0/0
R    192.168.90.32/27 [120/1] via 192.168.90.33, 00:00:05, Serial0/0
```

**关键差异**：掩码变成 **`/27`** 了！因为 v2 的更新里**携带掩码**。

**但仍然有汇总**：注意路由表里还是可能看到 `/24` 条目（取决于拓扑和计时），因为 `auto-summary` 在 v2 下**默认仍然开启**。这就是为什么还要做第三步。

**PC 测试**：`ping 192.168.90.98`，应该仍然通（TTL=126）。

### 7.5 阶段三：关闭自动汇总

四台路由器都执行：

```cisco
2621A(config)# router rip
2621A(config-router)# no auto-summary
2621A(config-router)# end

2501A(config)# router rip
2501A(config-router)# no auto-summary

2501B(config)# router rip
2501B(config-router)# no auto-summary

2501C(config)# router rip
2501C(config-router)# no auto-summary
```

**再等 30 秒**，然后：

```cisco
2501B# show ip route
```

**预期 `show ip route`（关汇总后）**：
```
R    192.168.90.0/27   [120/1] via 192.168.90.33, ...
R    192.168.90.64/27  [120/1] via 192.168.90.65, ...
R    192.168.90.96/27  [120/1] via 192.168.90.33, ...
R    192.168.90.128/27 [120/2] via 192.168.90.65, ...
```

**看这四条**：
- 四条**明细** `/27` 全部出现（自己直连的 `192.168.90.32/27` 不显示为 R，因为它已经是 C）
- 跳数 `[120/2]` 表示经过 2 跳（2501B → 2501C → 目标）
- 没有 `/24` 汇总条目了

**PC 测试**：`ping 192.168.90.98`，仍然通。

### 7.6 三组结果对比表（报告的核心）

把三次的 `show ip route` 关键行填进这张表：

| 阶段 | 配置 | `show ip route` 里学到的条目 | 掩码 | 连通性 |
|---|---|---|---|---|
| 一 | RIPv1 | `R 192.168.90.0/24` | /24（汇总） | 通 |
| 二 | RIPv2 | `R 192.168.90.0/27`、`.32/27` | /27（真实） | 通 |
| 三 | v2 + no auto-summary | 4 条明细 /27 | /27（明细） | 通 |

**分析要写什么**（这是得分点，不能只写"通了"）：

1. **RIPv1 为什么只显示 /24？** 因为 RIPv1 的更新报文里没有掩码字段，接收方只能按主类网络（A/B/C 类）推断。`192.168.90.0` 是 C 类，主类掩码就是 `/24`，所以不管实际是 /27 还是 /30，学过来都变成 /24。
2. **RIPv2 为什么能看到 /27？** v2 在更新里携带了掩码（这就是"无类路由协议"的含义），所以能传递真实掩码。
3. **为什么 v2 还要关自动汇总？** 因为 `auto-summary` 在 v2 下默认开启，它会在**主网边界**把子网汇总成主网路由。本实验所有子网都在同一个主网 `192.168.90.0/24` 内，属于"同一主网内的不连续子网"场景——如果不关汇总，明细路由会被汇总成一条 /24，可能导致某些网段不可达（路由黑洞）。
4. **为什么本实验三组都通？** 因为这个拓扑是"全连通"的，且所有子网都从同一个主网切出来，汇总后的 /24 恰好覆盖了所有明细，所以不影响可达性。**但如果是真实网络里的不连续子网，就会出问题**——这句话要写进报告，体现你理解了原理而不只是敲了命令。

### 7.7 本实验截图清单

| 序号 | 截什么 |
|---|---|
| 1 | 拓扑全图 |
| 2 | RIPv1：`show ip protocols`（send version 1） |
| 3 | RIPv1：`show ip route`（/24 汇总） |
| 4 | RIPv1：PC1 ping PC2 通 |
| 5 | RIPv2：`show ip protocols`（send version 2） |
| 6 | RIPv2：`show ip route`（/27） |
| 7 | RIPv2：PC1 ping PC2 通 |
| 8 | 关汇总：`show ip route`（4 条明细 /27） |
| 9 | 关汇总：PC1 ping PC2 通 |
---

## 8. 实验四：OSPF 多区域

### 8.0 本实验要达成的目标

- [ ] 按图 3 搭好 6 台路由器 + 3 台交换机 + 3 台 PC
- [ ] 划清 Area 0 / Area 1 / Area 2，R1 和 R3 做成 ABR
- [ ] 六台路由器全配 OSPF（`router ospf 1` + `network ... area ...`）
- [ ] `show ip ospf neighbor` 看到 FULL 状态
- [ ] `show ip route` 看到 `O`（区域内）和 `O IA`（区域间）
- [ ] 三台 PC 两两互 ping 通
- [ ] 写出四条实验结论

### 8.1 拓扑与区域划分（先看懂再动手）

```
        ┌──────────── Area 2 ────────────┐
        │  Router4 ── Switch2 ── Router5 │
        │       │                        │
        │     Router3 (ABR)              │
        └───────┼────────────────────────┘
                │ Se0/0/0
        ┌───────┼──────── Area 0 ─────────┐
        │    Router0 ──── Switch0 ── PC0  │
        │       │  Se0/0/0               │
        │       │                        │
        │    Router1 (ABR)               │
        └───────┼────────────────────────┘
                │ Fa0/0
        ┌───────┼──────── Area 1 ─────────┐
        │    Switch1 ── Router2          │
        │       │                        │
        │      PC1                       │
        └────────────────────────────────┘
```

| 区域 | 成员 | 说明 |
|---|---|---|
| **Area 0**（骨干） | Router0、Router1、Router3、Switch0、PC0 | 所有区域必须连到它 |
| **Area 1** | Router1、Switch1、Router2、PC1 | 通过 R1（ABR）接入骨干 |
| **Area 2** | Router3、Switch2、Router4、Router5、PC2 | 通过 R3（ABR）接入骨干 |

**ABR（区域边界路由器）**：R1 同时属于 Area 0 和 Area 1；R3 同时属于 Area 0 和 Area 2。**ABR 必须有一个接口在 Area 0**，否则区域间路由不通。

> **原图没有画 PC**，但作业要求"完成 PC 的配置"。本实验在 Switch0、Switch1、Switch2 上各补接一台 PC，报告里要**主动说明这是补接的**（这是加分项，说明你发现了任务与图的矛盾）。

### 8.2 搭拓扑

| 设备 | 型号 | 数量 | 备注 |
|---|---|---|---|
| 路由器 | 1841 | 6（R0~R5） | R0/R1/R3 要加 WIC-2T（有两个串行口），R2/R4/R5 可只加一个 |
| 交换机 | 2950-24 或 2960-24TT | 3（SW0/SW1/SW2） | 二层即可 |
| PC | PC-PT | 3（PC0/PC1/PC2） | 补接的 |

连线：

| 起点 | 终点 | 线型 |
|---|---|---|
| R0 Fa0/0 | SW0 Fa0/1 | 直通线 |
| SW0 Fa0/2 | PC0 Fa0 | 直通线 |
| R0 Se0/0/0 | R1 Se0/0/0 | Serial DTE |
| R0 Se0/0/1 | R3 Se0/0/0 | Serial DTE |
| R1 Se0/0/1 | R3 Se0/0/1 | Serial DTE |
| R1 Fa0/0 | SW1 Fa0/1 | 直通线 |
| SW1 Fa0/2 | R2 Fa0/0 | 直通线 |
| SW1 Fa0/3 | PC1 Fa0 | 直通线 |
| R3 Fa0/0 | SW2 **Fa0/3** | 直通线 |
| SW2 **Fa0/2** | R4 Fa0/0 | 直通线 |
| SW2 **Fa0/1** | R5 Fa0/0 | 直通线 |
| SW2 Fa0/4 | PC2 Fa0 | 直通线 |

> **SW2 的端口号按原图来，别顺手写成 Fa0/1、Fa0/2、Fa0/3**：原图 Switch2 上接 Router3 的是 **Fa0/3**，接 Router4 的是 **Fa0/2**，接 Router5 的是 **Fa0/1**，Fa0/4 用来补接 PC2。端口号不影响连通性（同一个 VLAN 内任意口都能通），但报告里要跟原图一致，否则会被扣"未严格按图连线"。

> 注意 SW1 上接了 R2 和 PC1 两台设备，它们都在 Area 1 的同一个网段 `192.168.90.64/26` 里。同理 SW2 上 R4、R5、PC2 都在 Area 2 的 `192.168.90.128/26` 里。**这就是用交换机把多台设备放进同一个广播域**，属于正常设计。

### 8.3 配地址 + OSPF（六台路由器）

**R0（全部接口在 Area 0）**：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname R0
R0(config)# no ip domain-lookup
R0(config)# interface fastEthernet 0/0
R0(config-if)# ip address 192.168.90.1 255.255.255.192
R0(config-if)# no shutdown
R0(config-if)# interface serial 0/0/0
R0(config-if)# ip address 192.168.90.197 255.255.255.252
R0(config-if)# clock rate 64000
R0(config-if)# no shutdown
R0(config-if)# interface serial 0/0/1
R0(config-if)# ip address 192.168.90.193 255.255.255.252
R0(config-if)# clock rate 64000
R0(config-if)# no shutdown
R0(config-if)# exit
R0(config)# router ospf 1
R0(config-router)# router-id 1.1.1.1
R0(config-router)# network 192.168.90.0 0.0.0.63 area 0
R0(config-router)# network 192.168.90.192 0.0.0.3 area 0
R0(config-router)# network 192.168.90.196 0.0.0.3 area 0
R0(config-router)# end
R0# show ip ospf neighbor
R0# show ip route
```

**R1（ABR：Area 0 + Area 1）**：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname R1
R1(config)# no ip domain-lookup
R1(config)# interface serial 0/0/0
R1(config-if)# ip address 192.168.90.198 255.255.255.252
R1(config-if)# no shutdown
R1(config-if)# interface serial 0/0/1
R1(config-if)# ip address 192.168.90.202 255.255.255.252
R1(config-if)# no shutdown
R1(config-if)# interface fastEthernet 0/0
R1(config-if)# ip address 192.168.90.65 255.255.255.192
R1(config-if)# no shutdown
R1(config-if)# exit
R1(config)# router ospf 1
R1(config-router)# router-id 2.2.2.2
R1(config-router)# network 192.168.90.196 0.0.0.3 area 0
R1(config-router)# network 192.168.90.200 0.0.0.3 area 0
R1(config-router)# network 192.168.90.64 0.0.0.63 area 1
R1(config-router)# end
R1# show ip ospf neighbor
```

**R3（ABR：Area 0 + Area 2）**：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname R3
R3(config)# no ip domain-lookup
R3(config)# interface serial 0/0/0
R3(config-if)# ip address 192.168.90.194 255.255.255.252
R3(config-if)# no shutdown
R3(config-if)# interface serial 0/0/1
R3(config-if)# ip address 192.168.90.201 255.255.255.252
R3(config-if)# no shutdown
R3(config-if)# interface fastEthernet 0/0
R3(config-if)# ip address 192.168.90.129 255.255.255.192
R3(config-if)# no shutdown
R3(config-if)# exit
R3(config)# router ospf 1
R3(config-router)# router-id 3.3.3.3
R3(config-router)# network 192.168.90.192 0.0.0.3 area 0
R3(config-router)# network 192.168.90.200 0.0.0.3 area 0
R3(config-router)# network 192.168.90.128 0.0.0.63 area 2
R3(config-router)# end
R3# show ip ospf neighbor
```

**R2（Area 1 内部）**：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname R2
R2(config)# no ip domain-lookup
R2(config)# interface fastEthernet 0/0
R2(config-if)# ip address 192.168.90.66 255.255.255.192
R2(config-if)# no shutdown
R2(config-if)# exit
R2(config)# router ospf 1
R2(config-router)# router-id 4.4.4.4
R2(config-router)# network 192.168.90.64 0.0.0.63 area 1
R2(config-router)# end
```

**R4（Area 2 内部）**：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname R4
R4(config)# no ip domain-lookup
R4(config)# interface fastEthernet 0/0
R4(config-if)# ip address 192.168.90.130 255.255.255.192
R4(config-if)# no shutdown
R4(config-if)# exit
R4(config)# router ospf 1
R4(config-router)# router-id 5.5.5.5
R4(config-router)# network 192.168.90.128 0.0.0.63 area 2
R4(config-router)# end
```

**R5（Area 2 内部）**：

```cisco
Router> enable
Router# configure terminal
Router(config)# hostname R5
R5(config)# no ip domain-lookup
R5(config)# interface fastEthernet 0/0
R5(config-if)# ip address 192.168.90.131 255.255.255.192
R5(config-if)# no shutdown
R5(config-if)# exit
R5(config)# router ospf 1
R5(config-router)# router-id 6.6.6.6
R5(config-router)# network 192.168.90.128 0.0.0.63 area 2
R5(config-router)# end
```

### 8.4 反掩码（wildcard mask）怎么算（这是必考点）

OSPF 的 `network` 后面跟的是**反掩码**，不是子网掩码。规则：**反掩码 = 255.255.255.255 - 子网掩码**。

| 子网掩码 | 反掩码 | 写法 |
|---|---|---|
| 255.255.255.192（/26） | 0.0.0.63 | `network ... 0.0.0.63 area X` |
| 255.255.255.252（/30） | 0.0.0.3 | `network ... 0.0.0.3 area X` |
| 255.255.255.224（/27） | 0.0.0.31 | `network ... 0.0.0.31 area X` |
| 255.255.255.255（/32） | 0.0.0.0 | `network ... 0.0.0.0 area X` |

> **写成子网掩码会怎样？** 比如写 `network 192.168.90.0 255.255.255.192 area 0`，Cisco 会报错 `Invalid input detected`（因为 255.x.x.x 不是合法的反掩码格式，或者被解释成完全不同的匹配范围）。**这是 OSPF 配置第一大错误**。

### 8.5 配 PC

| PC | IP | 掩码 | 网关 | 所属区域 |
|---|---|---|---|---|
| PC0 | 192.168.90.10 | 255.255.255.192 | 192.168.90.1 | Area 0 |
| PC1 | 192.168.90.74 | 255.255.255.192 | 192.168.90.65 | Area 1 |
| PC2 | 192.168.90.138 | 255.255.255.192 | 192.168.90.129 | Area 2 |

### 8.6 测试与验证

**验证 1：邻居关系（在 R1 上）**

```cisco
R1# show ip ospf neighbor
```

**预期**：
```
Neighbor ID     Pri   State      Dead Time   Address         Interface
3.3.3.3           1   FULL/  -   00:00:36    192.168.90.202  Serial0/0/1
1.1.1.1           1   FULL/  -   00:00:33    192.168.90.198  Serial0/0/0
```

- **`FULL` 才是好的**。如果显示 `INIT`、`EXSTART`、`EXCHANGE`、`LOADING`，说明还在建邻接，等 30 秒再看；一直不到 FULL 就是有问题（区域号不一致、掩码不一致、hello 计时器不一致）。
- `Neighbor ID` 就是对方的 `router-id`，所以配了 `router-id 1.1.1.1` 这里就显示 `1.1.1.1`，一眼能对上。

**验证 2：路由表（在 R1 上）**

```cisco
R1# show ip route ospf
```

**预期**：
```
O IA 192.168.90.128/26 [110/65] via 192.168.90.202, 00:02:11, Serial0/0/1
O    192.168.90.0/26   [110/65] via 192.168.90.198, 00:02:11, Serial0/0/0
```

- **`O`** = 同一区域内的 OSPF 路由（R1 的 Area 0 到 R0 的 Area 0 网段）
- **`O IA`** = 区域间（inter-area）路由，由 ABR 产生的 Type-3 LSA 通告过来
- `[110/65]` = 管理距离 110 / 度量值（cost）65

> **cost 65 是怎么来的？** OSPF 的 cost = 参考带宽（默认 100 Mbps）÷ 接口带宽。FastEthernet 是 100 Mbps → cost 1；Serial 是 1.544 Mbps → cost 64。所以"经过一条串行链路 + 一个以太网段"= 64 + 1 = **65**。两条路由都是 65，说明它们都只跨了一条串行链路，跳数相同。

**验证 3：PC 互通**

```
PC0> ping 192.168.90.74       ! Area0 -> Area1，经 R0、R1 两台路由器
Reply from 192.168.90.74: bytes=32 time<1ms TTL=126

PC0> ping 192.168.90.138      ! Area0 -> Area2，经 R0、R3 两台路由器
Reply from 192.168.90.138: bytes=32 time<1ms TTL=126

PC1> ping 192.168.90.138      ! Area1 -> Area2，经 R1、R3 两台 ABR
Reply from 192.168.90.138: bytes=32 time<1ms TTL=126
```

**TTL 分析**：
- PC0 → PC1：R0 → R1 → PC1，经过 2 台路由器，128-2=**126**。
- PC0 → PC2：R0 → R3 → PC2，经过 2 台路由器，**126**。
- PC1 → PC2：R1 → R3 → PC2，经过 2 台路由器（R1、R3 都是 ABR），**126**。

> 三条路径都只经过 2 台路由器，所以 TTL 都是 126。如果实测值比这个低，说明路径绕远了（比如走了 R1 → R0 → R3），可以用 `tracert` 确认。

> **TTL 的规律**：每经过一台**路由器**减 1，经过交换机不减。所以 TTL 可以反推跳数：`跳数 = 128 - TTL`（前提是源 PC 是 Windows，初始 TTL=128）。

**验证 4：OSPF 数据库（可选，加分）**

```cisco
R1# show ip ospf database
```

能看到 `Router Link States (Area 0)`、`Summary Net Link States (Area 0)` 等条目，说明 LSA 交换正常。

### 8.7 实验结论怎么写（报告要求"观察实验结果得出实验结论"）

四条结论，每条都要**先讲现象，再讲原理**：

**（1）关于邻居建立**
> OSPF 通过 Hello 报文建立邻居，邻居状态达到 FULL 才会交换链路状态信息。实验中在 R1 上 `show ip ospf neighbor` 看到与 R0、R3 均达到 FULL 状态，说明三台路由器在同一区域（Area 0）内的邻接关系建立正常。`router-id` 建议手工指定（本实验用 1.1.1.1~6.6.6.6），否则默认取接口最大 IP，接口地址一变就可能引起邻居重建。

**（2）关于区域划分**
> 区域划分的作用是把拓扑变化限制在区域内。Area 1、Area 2 内部的明细路由不会进入 Area 0，而是由 ABR（R1、R3）产生 Type-3 汇总 LSA 通告进 Area 0，因此 R1 的路由表里看到的是 `O IA` 的区域间路由。这减少了骨干区域的 LSA 数量，提高了收敛效率。

**（3）关于区域规则**
> 所有非骨干区域必须挂在 Area 0 上。本实验中 R1、R3 各有一条链路在 Area 0，满足这个规则。如果让 Area 1 直接连 Area 2（不经过 Area 0），区域间路由不会通——这是 OSPF 的强制性规则，不是配置技巧问题。

**（4）与静态路由、RIP 的对比**
> 与静态路由相比，OSPF 无需手工维护路由表，拓扑变化能自动收敛；与 RIP 相比，OSPF 支持 VLSM（反掩码可以精确匹配子网）、无 15 跳限制、收敛更快（Hello 10 秒 / Dead 40 秒 vs RIP 的 30 秒更新 / 180 秒超时）。OSPF 的配置量集中在 `network` 语句上，网络规模越大优势越明显；静态路由适合末端网络（如 R2 用一条默认路由），RIP 适合小型网络但要特别注意 v1/v2 和自动汇总的差异。

### 8.8 本实验截图清单

| 序号 | 截什么 |
|---|---|
| 1 | 拓扑全图（能看到三个 Area 标注更好） |
| 2 | R0 `show ip route`（O + O IA） |
| 3 | R1 `show ip ospf neighbor`（两个 FULL） |
| 4 | R1 `show ip route ospf`（O 与 O IA） |
| 5 | R3 `show ip ospf neighbor` |
| 6 | PC0 ping PC1（Area0→Area1） |
| 7 | PC0 ping PC2（Area0→Area2） |
| 8 | PC1 ping PC2（跨两个 ABR） |
| 9 | （加分）`show ip ospf database` |

---

## 9. 报告怎么写（对照模板逐格填）

### 9.1 模板结构（学校发的 .doc）

| 位置 | 内容 | 怎么填 |
|---|---|---|
| 标题 | 网络设备配置与管理 课程实验报告 | 不用改 |
| 表格第 1 行 | 实验名称 / 系别 | 实验名称写"路由器基本配置与静态路由、RIP、OSPF 配置"，系别"网络工程" |
| 第 2 行 | 姓名 / 学号 / 班级 | **必须手填**（配套 docx 里留空了） |
| 第 3 行 | 实验地点 / 实验日期 / 评分 | 地点日期手填，评分留空 |
| 第 4 行 | 指导老师 / 同组其他成员 | 李享梅 / 无 |
| **一、实验内容** | 作业原文 | 照抄长图四部分任务（配套 docx 已填好） |
| **二、实验目的** | 8 条 | 见配套 docx，可按自己理解微调 |
| **三、相关情况介绍** | 软件/设备/连线/模块/地址规划/测试方法 | 见配套 docx 六段 |
| **四、实验结果** | 四个实验的配置+测试+总结 | 这是主体，占 15 页左右 |

### 9.2 实验结果部分的结构（建议照这个骨架）

```
四、实验结果
  （一）路由器基本配置与单臂路由
      1. 实验拓扑与地址规划   ← 图 + 表
      2. 设备选型与连线
      3. 模式切换与基本配置   ← 代码块
      4. 接口配置：环回、以太网、串行接口
      5. 单臂路由：VLAN 间通信
      6. 测试与结果           ← 截图
      7. telnet 远程管理
      8. 小结
  （二）静态路由与三层交换机
      1. 拓扑与地址规划
      2. 三层交换机配置
      3. 路由器基本配置与静态路由
      4. PC 配置
      5. 测试结果
  （三）RIP 路由协议
      1. 拓扑与地址规划（含为什么用 /27 的说明）
      2. RIPv1 配置
      3. RIPv1 测试
      4. 改为 RIPv2 并测试
      5. 关闭自动汇总并测试
  （四）OSPF 多区域
      1. 拓扑与地址规划
      2. 基本配置与 OSPF 配置
      3. PC 配置
      4. 测试结果
      5. 实验结论
  （五）实验总结
      递进路线 + 易错点 + 排错顺序 + 地址规划说明
```

### 9.3 截图怎么放进 Word（保持清晰、不撑爆页面）

1. 在 PT 里按 `Ctrl+Shift+S` 或直接用系统截图工具（`Win+Shift+S`）截。
2. **只截需要的那一块**，不要把整个桌面截进去。
3. 插进 Word 后，**右键 → 大小和位置 → 宽度改成 14~15 cm**（和正文宽度一致）。超过 15 cm 会撑出页边距。
4. 图注写在图下方，格式：`图X  说明文字`，宋体 9 号，居中。
5. 代码/命令截图如果字太小，**优先用文字粘贴命令，而不是截图**——文字更清晰，也方便老师复制验证。

### 9.4 排版硬规则（老师会看这些）

| 项目 | 要求 |
|---|---|
| 正文 | 宋体小四（12pt）或五号（10.5pt），行距 1.3~1.5 |
| 标题 | 黑体，一级标题三号/四号，二级标题小四加粗 |
| 图 | 居中，宽度 ≤ 15 cm，图注在图下方 |
| 表 | 三线表或全框线，表头加粗，表注在表上方 |
| 代码 | Consolas 或 Courier New 等宽字体，9~10pt，可加浅灰底纹 |
| 页边距 | 上下 2.54 cm，左右 3.17 cm（A4 默认） |
| 页码 | 页脚居中，从第 1 页开始 |

> 配套的 .docx 已经按这个规范排好了，**你只需要补姓名/学号/班级/地点/日期**，以及把你自己的截图替换/补充进去（如果需要）。

### 9.5 绝对不能做的事

1. **不要把别人的拓扑图直接贴上去**——设备名、IP 段、接口编号对不上，一眼就能看出。
2. **不要只写"配置成功、测试通过"**——必须写**配置命令 + 测试输出 + 现象分析**三段。
3. **不要漏掉"不通"的那次测试**（实验一 5.9 的 ping 不通、实验三的三组对比）。**"先不通、配了路由才通"的过程比"一上来就通"更有说服力**，说明你真的理解了原理。
4. **不要四个实验塞进一个 .pkt 文件**，地址会冲突，也没法分别演示。

---

## 10. 自检清单（打分前必过）

### 10.1 通用检查（四个实验都适用）

- [ ] 所有设备的 hostname 都用 `hostname` 命令改过（不是只在 PT 面板上改标签）
- [ ] 所有 IP 地址都包含 `90`（学号后两位）
- [ ] 所有 PC 的 IP、掩码、网关三项都填了，没有漏网关
- [ ] 所有路由器接口都 `no shutdown` 了（`show ip interface brief` 全 up/up）
- [ ] 串行链路 DCE 端都配了 `clock rate`
- [ ] 1841 都加了 WIC-2T 模块
- [ ] 每个实验都 `copy running-config startup-config` 保存过
- [ ] 四个实验是四个独立的 .pkt 文件
- [ ] 工程文件名符合 `90-实验X-内容.pkt` 规范

### 10.2 实验一专项

- [ ] `show ip route` 里有 Loopback0 的 `/32` 直连路由
- [ ] `show vlan brief` 里 Fa0/1 在 VLAN10、Fa0/2 在 VLAN20
- [ ] `show interfaces trunk` 里 Fa0/24 是 trunk
- [ ] 两个子接口 `show ip interface brief` 都 up/up
- [ ] PC-A ping PC-B 通，TTL=127
- [ ] PC-A ping PC-C 配路由前不通、配路由后通，TTL=126
- [ ] telnet 能从 PC-A 登录到 R1 并 `enable`

### 10.3 实验二专项

- [ ] SW0 上 `ip routing` 配了
- [ ] SW0 的 `show ip interface brief` 里 Vlan2、Vlan3 都 up/up
- [ ] SW0 的 Fa0/1 是 `no switchport` 的三层口
- [ ] SW0 上有 5 条静态路由
- [ ] R2 上有默认路由 `S* 0.0.0.0/0`
- [ ] 5 台 PC 两两互 ping 全通
- [ ] `tracert 192.168.90.150` 的 8 跳地址与拓扑一致

### 10.4 实验三专项

- [ ] 5 个网段全部是 `/27`（255.255.255.224）
- [ ] 4 台路由器都是 2621XM，且都插了 WIC-2T（`show ip interface brief` 里能看到 `Serial0/0`、`Serial0/1`）
- [ ] 接口名用的是 `fastEthernet 0/0` / `serial 0/0` / `serial 0/1`（**不是** `ethernet 0` / `serial 0`，PT 8.2.2 没有 2501 型号）
- [ ] RIPv1 阶段 `show ip protocols` 显示 `send version 1`
- [ ] RIPv1 阶段 `show ip route` 显示 `/24` 汇总
- [ ] RIPv2 阶段 `show ip protocols` 显示 `send version 2`
- [ ] RIPv2 阶段 `show ip route` 显示 `/27`
- [ ] 关汇总后 `show ip route` 显示 4 条明细 `/27`
- [ ] 三次 ping 都通
- [ ] 报告里有三组对比表 + 原理分析（不是只写"通了"）

### 10.5 实验四专项

- [ ] 六台路由器都配了 `router ospf 1`
- [ ] 六台路由器的 `router-id` 各不相同（1.1.1.1 ~ 6.6.6.6）
- [ ] 所有 `network` 后面用的是**反掩码**（0.0.0.63 / 0.0.0.3），不是子网掩码
- [ ] 所有 `network` 后面都有 `area X`
- [ ] R1、R3 各有一个接口在 Area 0（ABR 条件）
- [ ] `show ip ospf neighbor` 显示 FULL
- [ ] `show ip route ospf` 能看到 `O` 和 `O IA` 两类
- [ ] 三台 PC 两两互 ping 通
- [ ] 报告里说明了"原图没画 PC，本实验补接"这件事
- [ ] 报告里有四条实验结论

### 10.6 报告检查

- [ ] 姓名、学号、班级、地点、日期都填了
- [ ] 图 1~图 5、表 1~表 6 编号连续，正文都有引用
- [ ] 每张图下面都有图注，每张表上面都有表注
- [ ] 所有截图宽度 ≤ 15 cm
- [ ] 代码块用等宽字体
- [ ] 没有错别字（常见错：`FastEthernet` 写成 `FastEthernet0/0` 与 `Fa0/0` 混用、`encapsulation` 拼成 `encapsulaton`、`no switchport` 写成 `no switch`）
- [ ] 总页数合理（一般 15~25 页，太少说明写得不够细）
- [ ] 导出 PDF 检查一遍（`文件 → 导出 → PDF`），确认没有图片跑版
- [ ] 报告里**主动写明**了两处与原创图不一致的地方：实验三用 2621XM 替代 2501、实验四补接 3 台 PC（隐瞒会被扣分，说明清楚反而是加分项）

### 10.7 用现成工程文件自查（最快的一条路）

把四个 `.pkt` 打开，按下表逐项比对。**任何一项对不上，说明你的配置漏了东西**：

| 打开的文件 | 敲这条命令 | 应该看到 |
|---|---|---|
| 实验一 | `R1# show ip route` | 2 条子接口 `C` + 1 条串口 `C` + `C 192.168.90.200/32 is directly connected, Loopback0` |
| 实验二 | `SW0# show ip route` | 3 条 `C`（Vlan2、Vlan3、Fa0/1）+ 5 条 `S` |
| 实验三 | `2501B# show ip protocols` | `Default version control: send version 1, receive version 1` |
| 实验三 | `2501B# show ip route` | 只有 `R 192.168.90.0/24`（有类汇总，**没有** `/27` 明细） |
| 实验四 | `R1# show ip ospf neighbor` | 2 个邻居，State 都是 `FULL/ -` |
| 实验四 | `R2# show ip route ospf` | 有 `O IA` 条目（区域间路由） |

实验三打开时是 RIPv1 阶段，你要自己加 `version 2` 和 `no auto-summary` 才能看到后两组结果——这是故意留的，让你亲手做出对比。

---

## 11. 故障排查速查表

### 11.1 接口状态类

| 现象 | 原因 | 解决 |
|---|---|---|
| `show ip interface brief` 显示 `down/down` | 没 `no shutdown`，或线没接 | 进接口 `no shutdown`；检查连线 |
| 显示 `up/down` | 串行链路 DCE 端没配 `clock rate` | 在 DCE 端配 `clock rate 64000` |
| 显示 `administratively down` | 明确被 shutdown 了 | `no shutdown` |
| 接口名不存在（如 `serial 0/0/0` 报错） | 1841 没加 WIC-2T | 断电加模块再上电 |
| 交换机口不显示在 VLAN 里 | 是 trunk 口 | 正常现象 |

### 11.2 路由类

| 现象 | 原因 | 解决 |
|---|---|---|
| `show ip route` 空 | 没配接口地址，或接口没 up | 先查 `show ip interface brief` |
| 有直连但 ping 不通邻居 | 掩码不一致，或不在同一网段 | 核对两端 IP 和掩码 |
| 能 ping 直连，不能 ping 远端 | 缺路由（去或回） | `show ip route` 逐台查，**两边都要有** |
| 静态路由配了但没生效 | 下一跳不可达 | 下一跳必须是直连网段内的地址 |
| `S*` 默认路由没生效 | 没有匹配的明细路由时才会用 | 正常，`*` 表示候选 |
| RIP 学不到路由 | `network` 写错，或版本不匹配 | 检查 `show ip protocols` |
| OSPF 邻居卡在 `EXSTART` | MTU 不一致（PT 里少见） | 检查接口 MTU |
| OSPF 邻居卡在 `INIT`/`2WAY` | 区域号不一致，或 hello 计时器不一致 | `show ip ospf interface` 对比 |

### 11.3 特殊设备类

| 现象 | 原因 | 解决 |
|---|---|---|
| 三层交换机 `ip routing` 命令不存在 | 选成 2960（二层） | 换 3560-24PS |
| SVI（VLAN 接口）down | 该 VLAN 内没有 up 的端口 | 接 PC 并开机 |
| `no switchport` 报错 | 端口不支持（二层交换机） | 换 3560 |
| 2621XM 上 `interface ethernet 0` 报 `Invalid interface` | 2621XM 的以太口叫 `FastEthernet0/0`，且 PT 8.2.2 没有 2501 型号 | 用 `interface fastEthernet 0/0` |
| 2621XM 上找不到 `serial 0/0` | 没插 WIC-2T | 关机 → 拖 WIC-2T 进空槽 → 开机 |

### 11.4 telnet 类

| 现象 | 原因 | 解决 |
|---|---|---|
| `Password required, but none set` | 没配 enable 密码 | 配 `enable secret xxx` |
| 连不上（超时） | 路由不通，或 vty 没配 | 先 ping 通，再查 `line vty` |
| 登录后进不去特权模式 | enable 密码错 | 重新配 `enable secret` |

### 11.5 排错的黄金顺序

```
第 1 步：show ip interface brief   → 链路和地址对不对（物理层/数据链路层）
第 2 步：ping 直连邻居             → 二层通不通
第 3 步：show ip route             → 路由有没有（网络层）
第 4 步：show ip protocols / show ip ospf neighbor → 协议跑没跑起来
第 5 步：PC 上 ping / tracert      → 端到端
```

**永远按这个顺序查，不要跳步。** 90% 的问题在第 1 步就能发现。

---

## 12. 附录：四份配置汇总（可直接对照）

### 12.1 实验一 R1 完整配置

```cisco
hostname R1
no ip domain-lookup
clock timezone CST 8
banner motd #Welcome to R1#
enable secret cisco123
interface Loopback0
 ip address 192.168.90.200 255.255.255.255
interface FastEthernet0/0
 no shutdown
interface FastEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.90.1 255.255.255.192
interface FastEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.90.65 255.255.255.192
interface Serial0/0/0
 ip address 192.168.90.129 255.255.255.252
 clock rate 64000
ip route 192.168.90.132 255.255.255.252 192.168.90.130
line vty 0 4
 password telnet123
 login
 transport input telnet
```

### 12.2 实验二 SW0 完整配置

```cisco
hostname SW0
ip routing
vlan 2
 name vlan2
vlan 3
 name vlan3
interface FastEthernet0/1
 no switchport
 ip address 192.168.90.129 255.255.255.252
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 2
interface FastEthernet0/3
 switchport mode access
 switchport access vlan 3
interface Vlan2
 ip address 192.168.90.1 255.255.255.192
interface Vlan3
 ip address 192.168.90.65 255.255.255.192
ip route 192.168.90.132 255.255.255.252 192.168.90.130
ip route 192.168.90.136 255.255.255.252 192.168.90.130
ip route 192.168.90.140 255.255.255.252 192.168.90.130
ip route 192.168.90.144 255.255.255.252 192.168.90.130
ip route 192.168.90.148 255.255.255.252 192.168.90.130
```

### 12.3 实验三 2501B 完整配置（RIP 三阶段最终态）

> 设备实际为 2621XM + WIC-2T；`FastEthernet0/0` 对应原图 `Ethernet0`，`Serial0/0` 对应原图 `Serial0`，`Serial0/1` 对应原图 `Serial1`。

```cisco
hostname 2501B
interface FastEthernet0/0
 ip address 192.168.90.97 255.255.255.224
interface Serial0/0
 ip address 192.168.90.34 255.255.255.224
interface Serial0/1
 ip address 192.168.90.65 255.255.255.224
 clock rate 64000
router rip
 version 2
 network 192.168.90.0
 no auto-summary
```

### 12.4 实验四 R1 完整配置（ABR）

```cisco
hostname R1
interface FastEthernet0/0
 ip address 192.168.90.65 255.255.255.192
interface Serial0/0/0
 ip address 192.168.90.198 255.255.255.252
interface Serial0/0/1
 ip address 192.168.90.202 255.255.255.252
router ospf 1
 router-id 2.2.2.2
 network 192.168.90.196 0.0.0.3 area 0
 network 192.168.90.200 0.0.0.3 area 0
 network 192.168.90.64 0.0.0.63 area 1
```

---

## 结尾：做完了怎么交付

1. **四个 .pkt 文件**（`90-实验一...pkt` ~ `90-实验四...pkt`）打包成 zip。
2. **一份 Word 报告**（配套的 .docx，补上姓名学号等信息）。
3. 如果老师要求，再导出 PDF 一份（`文件 → 导出 → 创建 PDF/XPS`）。
4. 可选的 **`README-PKT.md`**：里面写了机型替代（2501→2621XM）和补接 PC 的说明，如果老师对"没按原图"有疑问，直接给他看这份。

**最后再走一遍第 10 章的清单**，特别是"所有 IP 都含 90"和"每个实验都保存过"这两条——这两条是最容易丢分的。
