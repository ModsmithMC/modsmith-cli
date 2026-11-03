<p align="center">
  <img src="docs/assets/banner.svg" alt="Modsmith" width="100%">
</p>

<p align="center">
  <strong>在终端里查找、安装和更新 Minecraft 整合包、模组、资源包和光影，直接用于官方启动器。</strong>
</p>

<p align="center">
  <a href="https://github.com/ModsmithMC/modsmith/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/ModsmithMC/modsmith/ci.yml?branch=main&style=flat-square&label=CI&logo=github" alt="CI"></a>
  <a href="https://pypi.org/project/modsmith-cli/"><img src="https://img.shields.io/pypi/v/modsmith-cli?style=flat-square&color=3c8527" alt="PyPI"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12+"></a>
  <img src="https://img.shields.io/badge/status-alpha-orange?style=flat-square" alt="Alpha">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT license"></a>
</p>

<p align="center">
  <a href="https://modsmithmc.org/">网站</a> · <a href="https://modsmithmc.org/modsmith/">文档</a> · <a href="README.md">English</a> · <strong>简体中文</strong>
</p>

---

Modsmith 负责准备游戏文件，并在 Minecraft 官方启动器里添加一个安装项。它不登录账号，也不启动游戏：你在启动器里选中这个安装项，开始游戏就行。

<table>
  <tr>
    <td width="33%" valign="top">
      <img src="https://raw.githubusercontent.com/ModsmithMC/modsmithmc.github.io/main/site/assets/pixel/package.svg" alt="" width="24" height="24">
      <p><strong>一条命令装好整合包</strong></p>
      从 Modrinth、CurseForge 或本地文件安装整合包，连同它的模组加载器和 Minecraft。
    </td>
    <td width="33%" valign="top">
      <img src="https://raw.githubusercontent.com/ModsmithMC/modsmithmc.github.io/main/site/assets/pixel/puzzle.svg" alt="" width="24" height="24">
      <p><strong>想加什么就加什么</strong></p>
      添加模组、资源包和光影，所需的前置模组会一起装上。
    </td>
    <td width="33%" valign="top">
      <img src="https://raw.githubusercontent.com/ModsmithMC/modsmithmc.github.io/main/site/assets/pixel/refresh.svg" alt="" width="24" height="24">
      <p><strong>更新不丢改动</strong></p>
      更新整合包和你自己加的内容，并显示每个版本的更新内容。
    </td>
  </tr>
  <tr>
    <td valign="top">
      <img src="https://raw.githubusercontent.com/ModsmithMC/modsmithmc.github.io/main/site/assets/pixel/list.svg" alt="" width="24" height="24">
      <p><strong>先看再改</strong></p>
      每次改动都会先列出来，等你确认。<code>--dry-run</code> 只列出不执行。
    </td>
    <td valign="top">
      <img src="https://raw.githubusercontent.com/ModsmithMC/modsmithmc.github.io/main/site/assets/pixel/play.svg" alt="" width="24" height="24">
      <p><strong>启动器里直接能玩</strong></p>
      每个实例在官方启动器里都有自己的安装项，并带上整合包的图标。
    </td>
    <td valign="top">
      <img src="https://raw.githubusercontent.com/ModsmithMC/modsmithmc.github.io/main/site/assets/pixel/link.svg" alt="" width="24" height="24">
      <p><strong>接管已有的安装</strong></p>
      接管你在启动器里自己建的安装项，以及里面已有的模组。
    </td>
  </tr>
</table>

## 安装

Modsmith 需要 Python 3.12 或更新版本。用 [uv](https://docs.astral.sh/uv/) 从 PyPI 安装：

```bash
uv tool install modsmith-cli
```

或者用 [pipx](https://pipx.pypa.io/)：

```bash
pipx install modsmith-cli
```

然后确认安装成功：

```bash
modsmith --version
```

从 0.1.0 升级？它当时用的是另一个名字，请先用 `uv tool uninstall modsmith-app` 或 `pipx uninstall modsmith-app` 卸载。你的实例和设置都会保留。

## 快速上手

找一个整合包，装好，然后在官方启动器里开始游戏：

```bash
modsmith search "fabulously optimized" --type modpack
modsmith install fabulously-optimized --name fo
```

添加一个模组和一个光影包，再看看实例里都有什么：

```bash
modsmith add fo iris
modsmith add fo complementary-reimagined --type shader
modsmith show fo
```

保持最新：

```bash
modsmith update fo
```

如果你只有一个实例，可以不写实例名。

## 命令

| 命令 | 作用 |
| --- | --- |
| `install` | 把整合包安装成一个新实例 |
| `create` | 新建一个空实例，可以带模组加载器，也可以不带 |
| `import` | 接管你在官方启动器里自己建的安装项 |
| `list` | 列出你的实例 |
| `show` | 列出实例里的模组、资源包和光影 |
| `add` / `remove` | 添加项目及其前置，或者移除 |
| `enable` / `disable` | 开启或关闭文件，但不删除 |
| `pin` / `unpin` | 固定项目的版本，或者恢复更新 |
| `adopt` | 识别你自己放进实例里的文件 |
| `update` | 更新整合包和你加的内容 |
| `move` / `delete` | 重命名、移动或删除实例 |
| `search` / `info` | 查找项目，查看它的版本 |
| `loaders` | 列出模组加载器的版本 |
| `config` | 查看和修改设置 |

每个命令都可以用 `--help` 查看说明，里面附有示例。

## 用法示例

<details>
<summary><b>使用 CurseForge</b></summary>

CurseForge 需要一个 API key，可以在 [CurseForge 控制台](https://console.curseforge.com)免费申请。保存一次即可：

```bash
modsmith config set curseforge_api_key '<key>'
```

在 PowerShell 里请保留单引号：双引号里的 `$` 会被当成变量。之后用 `curseforge:` 指明 CurseForge 上的项目：

```bash
modsmith install curseforge:all-the-mods-9 --name atm9
modsmith add atm9 curseforge:jei
```

</details>

<details>
<summary><b>安装需要手动下载的文件</b></summary>

有些 CurseForge 作者禁止其他工具下载他们的文件。遇到这种文件，Modsmith 会把它们列出来，并附上每个文件的下载链接。把它们下载到同一个文件夹里，再运行一次同样的命令：

```bash
modsmith install curseforge:all-the-mods-9 --name atm9 --from Downloads/atm9-files
```

</details>

<details>
<summary><b>选择可选文件</b></summary>

整合包有可选文件时，Modsmith 会问你要哪些。也可以直接在命令行里指定：

```bash
modsmith install fabulously-optimized --optional shaders --optional zoom
modsmith install fabulously-optimized --all-optional
```

你的选择会被记住，`update` 时会沿用。

</details>

<details>
<summary><b>从零开始</b></summary>

```bash
modsmith loaders fabric 1.21.1
modsmith create survival --minecraft 1.21.1 --loader fabric
modsmith add survival sodium lithium
```

不指定 `--loader-version` 时，会使用推荐版本。

</details>

<details>
<summary><b>接管已有的安装项</b></summary>

先在官方启动器里给这个安装项设置单独的游戏目录，启动一次，然后运行：

```bash
modsmith import "My Fabric world"
```

Modsmith 会读出它的 Minecraft 和加载器版本，并识别其中的模组，以便之后更新。

</details>

<details>
<summary><b>在脚本里使用</b></summary>

没有终端时，Modsmith 从不询问：它会停下来，提示你加上 `--yes`。删除操作还需要再加 `--force`。如果需要更多控制，请直接使用 [Modsmith Python 库](https://github.com/ModsmithMC/modsmith-python)。

</details>

## 文件放在哪里

| 内容 | 位置 |
| --- | --- |
| 实例 | 用户数据文件夹下的 `Modsmith/instances`。可以用 `modsmith config set instances_dir <文件夹>` 修改 |
| 设置 | 用户配置文件夹里的 `config.toml`。运行 `modsmith config path` 可以看到具体路径 |
| 启动器安装项 | 官方启动器的 `launcher_profiles.json`，每个实例一个 |

设置 `MODSMITH_HOME` 后，所有内容都会放在同一个文件夹里。

## Modsmith 的组成

命令行基于 Python 库构建，平台、整合包格式、模组加载器和实例这些实际工作都由它完成。

| | 简介 | 代码 |
| :--- | :--- | :--- |
| [命令行](https://modsmithmc.org/modsmith/) | 在终端里安装整合包 | [ModsmithMC/modsmith](https://github.com/ModsmithMC/modsmith) |
| [Python 库](https://modsmithmc.org/modsmith-python/) | 打造你自己的整合包工具 | [ModsmithMC/modsmith-python](https://github.com/ModsmithMC/modsmith-python) |
| [网站](https://modsmithmc.org/) | 项目主页 | [ModsmithMC/modsmithmc.github.io](https://github.com/ModsmithMC/modsmithmc.github.io) |

## 许可证

Modsmith 基于 [MIT 许可证](LICENSE) 发布，与 Mojang、Microsoft、Modrinth 和 CurseForge 没有关联。
