# 上游来源与同步

| 项目 | 值 |
| --- | --- |
| 原始仓库 | [borawong/AiMaMi](https://github.com/borawong/AiMaMi) |
| 插件目录 | `plugins/niu-image-gen` |
| 原作者 | BORAWONG |
| 上游许可证 | Apache-2.0 |
| 提取的仓库提交 | `add37271e29ba81ee17f15f444a24925af50bb87` |
| 插件最后提交 | `297c7af56f10fb371b77bc9b6b65aa320afcbe7e` |
| 上游插件版本 | 1.1.0 |
| 核对日期 | 2026-10-06（北京时间） |

核对时，本机安装的 1.1.0 与上游全部 5 个文件逐字节相同。源仓库 2026-08-03 的提交未修改插件；插件最后修改时间为 2026-07-02 16:59:46（北京时间）。

本仓库通过 `git subtree split --prefix=plugins/niu-image-gen` 提取该子目录的 13 条历史提交，保留原作者、时间和提交说明，提交 SHA 因目录变更而重写。未带入 AiMaMi 桌面程序或其他无关资源。

## 检查更新

在装有 GitHub CLI 的终端运行：

```powershell
gh api 'repos/borawong/AiMaMi/commits?path=plugins/niu-image-gen&per_page=5' --jq '.[] | {sha, date: .commit.committer.date, message: .commit.message}'
```

只关注插件目录的提交，避免把 AiMaMi 整个项目的更新时间当作插件更新。

## 合并上游插件改动

在独立临时目录克隆上游并拆分子目录，再在本仓库添加拆分后的仓库为 remote，审查差异后合并其分支。保持本仓库根目录布局，勿把 AiMaMi 的 `main` 直接合并进来。

更新后保留 NOTICE / LICENSE，更新本文件的来源提交和 CHANGELOG，再同步 `plugin.json`、`.codex-plugin/plugin.json` 与 `package.json` 的版本号，运行 `npm run check` 后提交。

## Gemini 本地来源

`skills/momo-image-gen/` 来自本机已有的 `momo-image-gen` 技能，包含 Gemini 3.1 Flash Image 与 Gemini 3 Pro Image 两个入口。

它不是 AiMaMi 上游的一部分；未发现单独的公开上游仓库，因此没有为 Gemini 声称上游版本号或更新状态。本次整理保留其 Python 运行脚本，只补充技能的脚本定位、模型路由、编辑输入和输出目录指导。
