# KR6 Live Control v4.1 — 王国保卫战 6 实时 MOD

面向 Windows Steam 版 **Kingdom Rush 6: Genesis TD** 的非官方本地 MOD。通过中文控制面板实时调整经验倍率、关卡金币和战斗速度。

> 本仓库仅包含原创修改器源码与本地安装工具，不包含游戏 EXE、DLL、原版脚本或存档。需要自行安装游戏。与游戏开发商及发行商无隶属关系。

**普通用户推荐下载 [Releases 中的 Windows x64 免 Python 版](https://github.com/sunsun511/kr6-live-control/releases)**，完整解压后双击 `KR6-Installer.exe` 选择游戏目录，安装后双击 `Launch.cmd`。无需安装 Python、Docker 或第三方 Python 库。

第一次使用可先看 [使用说明.txt](使用说明.txt)。仓库的 Code → Download ZIP 是源码版，运行源码安装器仍需要 Python；Release 中的 `KR6-Live-Control-v4.1-Windows-x64.zip` 才是包含独立安装器的成品。

## 环境与放置位置

- 使用能正常运行本游戏的 **64 位 Windows 电脑**。当前工具是 Windows 桌面版，未适配 Android、macOS、Linux 或 Steam Deck。
- 控制面板使用系统的 `powershell.exe`、Windows Forms 和 .NET 桌面组件；按 Windows PowerShell 5.1 环境制作，不需要另装 PowerShell 7。
- **免 Python 版**：安装器已包含 CPython 3.10.11 x64，无需自行配置 Python。仍使用 Windows 自带 PowerShell/.NET 显示面板。
- **源码版**：安装、升级需要 Python 3.10+，仅使用标准库，不用 pip 安装依赖；日常打开面板不调用 Python。
- 不需要 CUDA、AI 模型、显卡计算环境、Cheat Engine 或另外安装 Lua。游戏所需运行环境以原版能够正常启动为准。
- 工具目录和游戏目录都需要写入权限。首次会额外生成约 1.2 GB 的 MOD EXE；升级还会保留旧 MOD，另需备份空间。建议预留至少 3 GB 空间，并另外考虑存档和累积备份。
- 修改器本身离线工作；Steam 登录、授权及游戏自身联网要求仍由游戏决定。

工具可放在任意可写目录，例如 `D:\Tools\KR6-Live-Control\`，**不用放进游戏目录**。把压缩包完整解压，保持 `Install.cmd`、`Install.ps1`、`Launch.cmd`、`Live-Control.ps1`、`build_mod.py`、`systems_wrapper.lua` 在同一文件夹，不能只拷贝一个启动文件。

通过 Steam 库 → 右键游戏 → 管理 → 浏览本地文件，可以找到游戏目录。安装时选择直接包含 `Kingdom Rush Genesis.exe` 的那一层文件夹，不是 Steam 总目录，也不是存档目录。

安装器不会自动搜索全盘或下载游戏：由你选目录后，读取其中的原版 EXE，校验兼容版本，生成同目录下的独立 MOD EXE，并在工具目录写入本机的 `manifest.json`。之后控制面板按这份安装记录寻找游戏、写入配置并读取游戏回传状态。

## 功能

| 功能 | 范围 / 行为 |
| --- | --- |
| 英雄经验获取倍率 | 1–100 倍，可实时修改 |
| 主动技能经验倍率 | 1–100 倍，援军、法术等，与英雄经验分开 |
| 游戏速度 | 1–5 倍；建议先试 2 倍 |
| 当前关卡金币 | 一次性设为 0–999999，输入框默认 50000 |
| 击杀金币倍率（v4.1） | 0–100 倍，支持两位小数；仅本局，换局或重开恢复 1 倍 |
| 实时状态 | 单独显示游戏回传的英雄倍率、技能倍率、游戏速度 |
| 存档备份 | 通过面板启动 MOD 前，自动备份本地存档 |

金币修改不会锁定余额，建塔后正常扣费。经验倍率只影响之后获得的经验，不改升级门槛；原本不提供经验的模式仍为零。战斗加速与经验倍率独立，菜单及音乐不主动加速。

## 支持范围

- Windows，Windows PowerShell 5.1，Python 3.10 或更高版本（仅使用标准库）。
- Steam app 4259190，已适配 build **25661788**。
- 原版 EXE SHA-256：`ea9d367b89aa879fc013fdd790be46e44b89b6c4515f29dc4ebddddf2d0340dd`。
- 安装器会拒绝未适配的游戏版本，避免把旧补丁套在更新后的程序上。

## 安装

### 普通用户：免 Python 版

1. 从 Releases 下载 `KR6-Live-Control-v4.1-Windows-x64.zip`，完整解压到可写目录。
2. 正常退出游戏，双击 `KR6-Installer.exe`（或 `Install.cmd`）。
3. 选择包含 `Kingdom Rush Genesis.exe` 的目录；安装器自动判断首次安装或升级，升级保留旧 MOD 备份。
4. 等待完成，双击 `Launch.cmd`，在面板里点“启动新版 MOD”。

这是便携文件夹，不是只复制一个 EXE：请保留随包的 `.ps1`、`.cmd` 和说明文件。安装器内置 Python 与补丁，不包含游戏本体。无需 Docker、WSL 或管理员级后台服务。当前 EXE 未做商业代码签名。

### 开发者：源码版

1. 从本仓库 **Code → Download ZIP** 下载并解压到有写入权限的文件夹。不要直接在 ZIP 内运行。
2. 安装 Python 3.10+，确保 `py -3` 或 `python` 命令可用。
3. 正常退出游戏，双击 **Install.cmd**，选择包含 `Kingdom Rush Genesis.exe` 的游戏安装目录。
4. 安装器在你的电脑上读取原游戏并生成独立的 `Kingdom Rush Genesis Live V4 Mod.exe`，原版 EXE 不变。
5. 双击 **Launch.cmd**，在面板中点“启动新版 MOD”。建议保持 Steam 已运行。

也可以在命令行安装：

```powershell
py -3 build_mod.py --game-dir "E:\SteamLibrary\steamapps\common\Kingdom Rush Genesis"
```

只检查兼容性而不安装：

```powershell
py -3 build_mod.py --game-dir "E:\SteamLibrary\steamapps\common\Kingdom Rush Genesis" --check
```

图形安装入口会自动检测已存在的 MOD 并执行带备份的升级。命令行安装默认不覆盖；升级用 `python build_mod.py --game-dir "游戏目录" --upgrade`。独立版可把 `python build_mod.py` 换为 `KR6-Installer.exe`。原版 EXE 不变。

## 使用

- 进入关卡后，面板收到游戏回传才显示已生效值；未连接或暂停过久时显示“—”。
- 改英雄倍率后点“应用倍率”；改技能倍率后点“应用技能倍率”；改速度后点“应用速度”。
- 设置金币只执行一次。默认 50000 不会自动写入，必须点击“设置金币”。
- 击杀金币：进入关卡后填入例如 `1.5`，点击“应用本局倍率”，等待下方回传显示 `1.5×`。原本奖励 10 金币的敌人之后会奖励 15；不追补此前击杀。设为 1 恢复正常，设为 0 不发击杀金币。
- 击杀倍率只包装死亡结算：不放大初始金币、卖塔返还、提前开波、漏怪补偿或手动设置金币。保留游戏原模式系数；小数金币按原游戏数值累积，例如 3 × 1.5 = 4.5，界面显示可能取整。
- 此倍率不存为跨关默认值，退出关卡、重开、下一关或重新启动游戏恢复 1×。已经拿到并花掉的金币不会因为恢复倍率而撤销。
- 切出游戏若自动暂停，切回并恢复运行，通常约 0.25 秒后处理请求。面板刷新间隔为 0.5 秒。
- 首次换成此 MOD 需要重启游戏一次；此后调参数不用重启。
- 主动技能通过使用获得独立经验，累计升级门槛为 6000、16000、36000、72000、120000。原模式和等级规则仍保留。
- 不要同时打开多个旧版面板，它们会共用配置文件。

## 存档与卸载

原版和 MOD 共用存档。通过面板获得并保存的经验不会因切回原版自动撤销。

存档通常在 `%APPDATA%\kingdom_rush_genesis`。备份保存在本工具的 `save_backups/`。恢复时先退出游戏，另存当前存档，再自行复制需要的备份；注意 Steam Cloud 可能同步存档。

卸载时退出游戏，删除生成的 MOD EXE、游戏目录内的 `hero_xp_multiplier.txt`、`live_mod_command.txt`、`live_mod_bounty.txt`、`live_mod_power_xp.txt`、`live_mod_speed.txt`、`live_mod_v4_status.txt`，以及本工具文件夹即可。保留你需要的存档和旧 MOD 备份；不要删除原游戏 EXE 或 DLL。

## 分享到 GitHub 或网盘

推荐普通用户分享 Releases 的免 Python ZIP；开发者可以分享源码。接收者都需要自己的兼容游戏安装，并在本机运行一次安装器。`KR6-Installer.exe` 是可分享的原创安装器，与包含游戏内容的 `Kingdom Rush Genesis Live V4 Mod.exe` 不同。

**不要直接压缩安装后的整个文件夹或游戏目录。** 分享包中不应包含：

- 原版或生成的 MOD EXE、游戏 DLL、提取的游戏脚本或其他游戏资源；生成的 MOD EXE 包含游戏内容，并非可独立分发的小补丁。
- `manifest.json`：包含你的本机绝对路径，不适用于接收者的电脑。
- `save_backups/`、`mod_backups/`：包含个人存档或完整旧版游戏 MOD。
- 本机快捷方式、游戏配置、状态文件、临时文件及测试结果。

可分享文件为本目录内的原创 `.py`、`.ps1`、`.cmd`、`systems_wrapper.lua`、`README.md`、`使用说明.txt` 和 `LICENSE`；开发测试脚本可选。保留 MIT 许可证及署名。已有 `.gitignore` 能排除常见本机生成文件，但手动打包时仍应检查 ZIP 内容。

## 常见问题

| 现象 | 处理 |
| --- | --- |
| 安装提示找不到 Python | 推荐改用 Release 免 Python 版并完整解压；若坚持用源码版，则安装 Python 3.10+ |
| 找不到游戏 EXE | 重新选择直接包含 `Kingdom Rush Genesis.exe` 的游戏目录 |
| Unsupported game build | 原版哈希不匹配当前适配版本。停止安装，等待适配；不要删除或绕过版本校验 |
| MOD already exists | 不必重复安装；升级时退出游戏并使用上文的 `--upgrade` 命令 |
| 打开面板报 manifest.json 不存在 | 尚未在这台电脑安装；先运行 `Install.cmd`，不要复制他人的安装记录 |
| 面板一直等待、数值为 — | 确认从面板启动的是新版 MOD，已经进入关卡并恢复运行；暂停或切出导致暂停时不会处理指令 |
| 启动后修改无效 | Steam 的普通“开始游戏”通常启动原版；改用面板里的“启动新版 MOD”，并观察回传值而不是只看输入框 |
| 提示访问被拒绝 | 确认游戏已退出、目录可写；优先使用账户可写的安装位置，受管理电脑需管理员处理权限 |
| 游戏移动目录后无法启动 | 安装记录仍指向旧路径；在新的游戏位置重新安装，已有 MOD 时使用 `--upgrade` 更新本机记录 |

游戏大版本、文件哈希与适配范围以本 README 为准。当前没有对所有 Windows 版本、杀毒软件或硬件组合做兼容性测试。

## 验证状态

- 用户实测：关卡金币修改可用、2 倍战斗速度可接受；2026-10-06 用户反馈新增击杀金币倍率测试没有问题。
- 代码测试：使用安装游戏自带 LuaJIT 执行原英雄经验和主动技能经验函数，验证实时切换倍率、恢复 1 倍及不重复累乘。
- 模拟循环测试：同样 2 秒输入，1/1.5/2/3/5 倍分别推进 2/3/4/6/10 秒；验证暂停。
- 金币测试：单次执行、额度边界、旧指令不会跨关重放。
- 击杀金币测试：使用原游戏编译后的 health 结算函数验证 10→15、实时切换、零/小数/上限、保留模式系数、无重复发钱或累乘、异常恢复、换局失效。已获得用户进游戏测试通过的反馈，尚未覆盖全部敌人和模式。
- 完整实战中的英雄/技能经验结算，以及超过 2 倍速度的稳定性，仍未完成验证。设定倍率并不保证机器在重负载下达到相同的实际速度。

安装后，开发者可运行 `python test_power.py` 和 `python test_speed.py`。测试只读取已安装游戏代码，不修改存档；无游戏时无法运行集成测试。可通过 `KR6_GAME_DIR` 环境变量指定测试用游戏目录。

## 实现

开发者构建便携包：在 Windows x64 的独立 Python 环境安装 `pyinstaller==6.22.3`，执行 `python build_portable.py`。输出在 `dist/`，包含 ZIP 和 SHA-256。已用 CPython 3.10.11 x64 构建；不需要用户安装此构建环境。第三方运行库许可证随便携包提供。

`build_mod.py` 保留原生启动前缀，复制未修改 ZIP 成员的压缩数据，只包装 `all/systems.lua`。安装时把原系统模块保存在本地生成的 EXE 内。补丁在关卡更新期间读取本地配置；速度通过分段调用原模拟循环实现；金币指令带有关卡会话标识，避免重复执行。

安装器验证原版哈希、ZIP CRC 和未替换成员信息。源码与控制面板不含网络请求或遥测。游戏自身的 Steam/网络行为保持原样。

## 许可

原创 MOD 代码采用 [MIT License](LICENSE)。此许可不涵盖原游戏及其资源。
