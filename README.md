# 王国保卫战 6 实时控制 v4.2.1

适用于 Windows x64 Steam 版《Kingdom Rush 6: Genesis TD》，App 4259190，Build 26406218。

从 [GitHub Releases](https://github.com/sunsun511/kr6-live-control/releases/tag/v4.2.1) 下载 KR6-Live-Control-v4.2.1-Windows-x64.zip，或者使用网盘里的同名压缩包。成品包含独立安装器，无需安装 Python。需要本机已安装对应版本的 Steam 游戏。

1. 将整个 ZIP 解压到固定的可写文件夹，预留至少 2 GB 空间。升级时使用新文件夹。
2. 正常退出游戏，双击 Install.cmd，选择包含 Kingdom Rush Genesis.exe 和 main.kra 的 Steam 游戏目录。安装器校验版本并在修改器目录生成供本机使用的游戏副本。
3. 保持 Steam 运行，双击 Launch.cmd，在中文面板点击「启动新版 MOD」。
4. 进入关卡并恢复战斗，等面板显示「已连接 MOD 关卡」再调倍率。如果面板提示正在运行 Steam 原版，先正常退出该局，再从面板启动。

可调整英雄经验、主动技能经验（各 1–100 倍）、战斗速度（1–5 倍）、当前局金币（0–999999）和击杀金币倍率（0–100）。经验倍率作用于之后获得的经验；击杀金币倍率换局恢复为 1。面板启动 MOD 时会备份本地存档。

再次使用时直接打开 Launch.cmd。每次重新安装会生成新的运行目录。分发时上传原始 ZIP 即可，安装后的目录含本机游戏文件、配置和可能的存档备份。

开发者可使用 Python 3.10+ 运行 build_mod.py --game-dir "游戏目录" --check 核对版本。使用 --game-dir 安装。开发环境安装 PyInstaller 后运行 build_portable.py 可生成 Windows 成品包。非官方工具，MIT 许可。
