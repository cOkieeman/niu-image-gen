---
name: momo-image-gen
description: Generate or edit images from prompts that start with `么么哒`, `么么哒pro`, `么么哒改`, or `么么哒pro改` when using the configured iiiiitoken Gemini image API. Use when a user types one of those triggers followed by prompt text and wants image generation or image editing.
---

# Momo Image Gen

Bundled in the standalone Niu Image Gen plugin from the user's local Momo skill.
The script lives at `scripts/generate_image.py` relative to this skill directory;
resolve its actual absolute path before running it. Requires Python 3.10+ and only
the standard library. Pass the full trigger-prefixed prompt so the script selects
Flash / Pro and preserves inline options. The two model routes share one script.

| Trigger | Model |
| --- | --- |
| `么么哒` / `么么哒改` | `gemini-3.1-flash-image` |
| `么么哒pro` / `么么哒pro改` | `gemini-3-pro-image` |

For an edit trigger, resolve the referenced image from the conversation or an
explicit path and pass `--input-image`. If no image is available, ask for it before
calling the API. Return saved images inline using their absolute filesystem paths.
Use an absolute `--output-dir` outside the plugin installation (for example,
`<user-home>/Pictures/niu-image-gen/gemini`) so updates do not overwrite outputs.

Standalone modifications: added script location, model routing and output path
guidance. The Python runtime is copied unchanged from the local skill.

## Workflow

1. Detect a prompt that starts with `么么哒`, `么么哒pro`, `么么哒改`, or `么么哒pro改`.
2. Keep the trigger in the script argument; the script strips it after choosing the model.
3. If no prompt follows the keyword, ask for the missing description.
4. Run `scripts/generate_image.py` with the full trigger-prefixed prompt.
5. `么么哒` uses the flash image model for text-to-image.
6. `么么哒pro` uses the pro image model for text-to-image.
7. `么么哒改` uses the flash image model for image editing or image-guided generation.
8. `么么哒pro改` uses the pro image model for image editing or image-guided generation.
9. The script reads the API key from `IIIIITOKEN_API_KEY`, `API_KEY`, or the existing Niu Image Gen config, then sends requests to the iiiiitoken Gemini image endpoint.

## Prompt Format

- Preferred input: `么么哒 写实风格成年女性肖像，自然光，高清摄影，背景简洁`
- Pro trigger example: `么么哒pro 写实风格成年女性肖像，自然光，高清摄影，背景简洁`
- Edit trigger example: `么么哒改 把这张图片改成黑白超现实主义风格`
- Pro edit trigger example: `么么哒pro改 把这张图片改成魔幻赛博朋克风格`
- You can prepend an inline option before the prompt:
  - `么么哒 --横图 提示词`
  - `么么哒pro --横图 提示词`
  - `么么哒改 --横图 提示词`
  - `么么哒pro改 --横图 提示词`
  - `么么哒 --方图 提示词`
  - `么么哒 --竖图 提示词`
- You can also set output size inline:
  - `么么哒 --1k 提示词`
  - `么么哒 --2k 提示词`
  - `么么哒 --4k 提示词`
  - Options can be combined, for example: `么么哒pro --横图 --2k 提示词`
- Preserve the user's text after the keyword.
- Default to `1:1` and `4K` unless inline options override them.

## Editing Existing Images

- The script can also edit an existing image when given `--input-image /absolute/path/to/file`.
- Example:
  - `generate_image.py "么么哒改 把这张图片改成黑白超现实主义风格" --input-image /path/to/source.jpg`
  - `generate_image.py "么么哒pro改 --横图 --1k 把这张图片改成魔幻赛博朋克风格" --input-image /path/to/source.png`
- When editing, keep using the same trigger rules:
  - `么么哒改` edits with the flash image model
  - `么么哒pro改` edits with the pro image model

## Output

- Save the generated image to disk.
- Print the saved file path and any short API text response.
- If the API returns JSON without a directly extractable image, save the raw JSON for inspection.
