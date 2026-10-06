# Niu Image Gen

由 cOkieeman 独立维护的 Codex 图片生成插件，提取自 [borawong/AiMaMi](https://github.com/borawong/AiMaMi/tree/main/plugins/niu-image-gen)，原作者 BORAWONG。保留插件全部文件与历史提交，采用 Apache-2.0 许可证。

一次安装包含 GPT Image 与 Gemini 两种模型入口：

| 入口 | 默认模型 | 用法 |
| --- | --- | --- |
| Niu / 原有快速与批量工作流 | `gpt-image-2-x` | 文本生图、多变体、批量生成、单图 / 批量编辑 |
| `么么哒` / `么么哒改` | `gemini-3.1-flash-image` | Gemini Flash 生图 / 编辑 |
| `么么哒pro` / `么么哒pro改` | `gemini-3-pro-image` | Gemini Pro 生图 / 编辑 |

Niu 支持 1K / 2K / 4K，比例为正方形 / 横版 / 竖版；快速模式与批量模式分别保存默认参数。Gemini 由同一套 Momo 技能按触发词选择 Flash / Pro。

独立维护版为 **1.1.2**，Niu 基于上游 **1.1.0**，新增模型选择并修正图片编辑接口；Gemini 来自本机已有 Momo 技能。来源和更新时间见 [UPSTREAM.md](UPSTREAM.md)，独立改动见 [CHANGELOG.md](CHANGELOG.md)。

## 安装为 Codex 插件

需要本地 Node.js 22 或更高版本、Python 3.10 或更高版本、Git 和支持插件市场的 Codex。插件没有 npm 或 pip 运行依赖。

```powershell
codex plugin marketplace add cOkieeman/niu-image-gen --ref main
```

在 Codex 插件页选择 **Niu Image Gen · cOkieeman** 来源，安装其中的 **Niu Image Gen**，然后在新聊天中使用。

市场名为 `niu-image-gen`；插件标识为 `niu-image-gen@niu-image-gen`。这是本仓库的独立分发入口。已安装的 AiMaMi 来源不会自动切换到这个仓库。

也可以用 CLI 安装：

```powershell
codex plugin add niu-image-gen@niu-image-gen
```

本仓库根目录就是插件根目录，含可移植 `plugin.json` 与兼容 `.codex-plugin/plugin.json`；市场目录格式参考 [OpenAI 插件打包文档](https://developers.openai.com/plugins/build/plugins)。

## 直接运行脚本

```powershell
git clone https://github.com/cOkieeman/niu-image-gen.git
Set-Location niu-image-gen
node scripts/generate.mjs --help
```

首次使用在本地终端设置服务商 API Key。以下占位符须由你在终端替换为自己的密钥：

```powershell
node scripts/generate.mjs --set-key '<YOUR_API_KEY>'
node scripts/generate.mjs --set-quick-mode --quality 2K --ratio square --count 1
node scripts/generate.mjs --set-batch-mode --quality 2K --ratio landscape --concurrency 3
```

生成、批量和编辑示例：

```powershell
node scripts/generate.mjs --prompt '一只赛博朋克风格的猫'
node scripts/generate.mjs --model gpt-image-2.5 --prompt '一只橘猫' --quality 1K --count 1
node scripts/generate.mjs --prompt '水墨山水' --quality 4K --ratio landscape --count 2
node scripts/generate.mjs --batch-inline '雪山日出' '雨夜街头' --concurrency 2
node scripts/generate.mjs --edit --image 'C:\Images\cat.png' --prompt '把背景换成海边'
node scripts/generate.mjs --model gpt-image-2.5 --edit --image 'C:\Images\cat.png' --prompt '加一条蓝色围巾'
node scripts/generate.mjs --edit --image 'C:\Images\cat.png' --prompt '改成水彩风格' --count 2
node scripts/generate.mjs --edit --image 'C:\Images\a.png' --image 'C:\Images\b.png' --prompt '换成纯白背景'
```

批量文件使用 JSON 字符串数组，可通过 `--batch prompts.json` 传入。显式参数优先于已保存的模式配置，后者优先于脚本默认值。`--output-dir` 可指定输出目录。

`--model` 适用于所有生成和编辑模式，默认仍为 `gpt-image-2-x`。在聊天里说“用 image2.5 画……”或“用 image2.5 改……”会选择 `gpt-image-2.5`。

2026-10-06 的服务实测中，`gpt-image-2-x` 与 `gpt-image-2.5` 均成功生成 1024×1024 图片，2.5 也通过独立编辑接口返回图片。服务商模型列表还包含 `gpt-image-2.5-flare` / `gpt-image-2.5-sunburst`，可通过 `--model` 指定，但本次未实测这两个变体。实时可用性仍以服务返回为准。

## Gemini Flash / Pro

在聊天中使用下面的触发词，选择 Flash 或 Pro；编辑时带上原图路径或引用聊天中的图片：

```text
么么哒 一只水彩风格的猫
么么哒pro --横图 --2k 雨夜街头电影剧照
么么哒改 把背景换成海边
么么哒pro改 --竖图 --4k 改成杂志封面风格
```

直接运行（保留触发词，脚本据此选择模型）：

```powershell
python skills/momo-image-gen/scripts/generate_image.py '么么哒 一只水彩风格的猫' --output-dir 'C:\Images\Gemini'
python skills/momo-image-gen/scripts/generate_image.py '么么哒pro --横图 --2k 雨夜街头' --output-dir 'C:\Images\Gemini'
python skills/momo-image-gen/scripts/generate_image.py '么么哒pro改 改成水彩风格' --input-image 'C:\Images\cat.png' --output-dir 'C:\Images\Gemini'
```

Gemini 默认正方形 `1:1`、`4K`；`--横图` / `--竖图` 对应 `16:9` / `9:16`。尺寸可用 `--1k` / `--2k` / `--4k` 改写。编辑入口需要原图，直接调用脚本时务必传 `--input-image`。

Gemini 密钥读取优先级为 `IIIIITOKEN_API_KEY` → `API_KEY` → 已有 Niu 配置的 `apiKey`。设置过 Niu Key 后可直接复用，不需要提交密钥到仓库。

## 服务与本地文件

- 该插件调用第三方服务：文字生图为 `https://api.iiiiitoken.com/v1/images/generations`（JSON），图片编辑为 `https://api.iiiiitoken.com/v1/images/edits`（multipart）。默认模型为 `gpt-image-2-x`，可显式选择 `gpt-image-2.5`。
- 请求携带 API Key 与提示词；编辑请求还携带源图片数据。
- 配置与密钥保存于用户主目录的 `.codex/niu-image-gen-config.json`；图片默认保存于 `Pictures/niu-image-gen/`。
- 仓库只包含插件与维护文件，不包含个人配置、密钥或生成图片。
- 当前脚本的请求超时为生图 220 秒、编辑 250 秒。
- Gemini 使用同一第三方域名的 `/v1beta/models/<model>:generateContent`；请求超时 120 秒。Momo CLI 默认输出到当前目录的 `outputs/`，建议显式指定绝对输出路径。

技能要求每批最多 20 条提示词、批量编辑最多 10 张、并发最多 10、多变体最多 4。上游脚本没有强制限制批次总量，直接调用时请遵守这些范围。

## 维护与验证

```powershell
npm run check
git log --oneline
```

检查覆盖 JavaScript 语法、插件清单一致性、资源路径、marketplace 指向、两套 CLI 帮助、Niu 全流程模型传递 / multipart 编辑以及 Gemini 模型路由 / 编辑载荷 / 图片解码。不会调用生图服务或读写个人配置。GitHub Actions 在 Windows 和 Linux 执行相同检查。

若 Python 命令不叫 `python`，运行前设置 `NIU_PYTHON` 为 Python 可执行文件的绝对路径。

后续开发直接修改本仓库，版本号同时更新三个清单。上传前确认没有加入本地配置或生成产物。上游同步步骤见 [UPSTREAM.md](UPSTREAM.md)。
