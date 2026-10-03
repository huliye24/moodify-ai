# msp02_layer_d_001 — Layer D / D-0 工程前置证据包

**日期：** 2026-10-02
**裁决依据：** `docs/plan/2026-10-02_LAYER_D_COMMERCIALIZATION_PROPOSAL.md` §8（LD-1 保持 GPL-3.0-only / LD-2 仅 pip / LD-3 先私有部署 / LD-4 定价延后）
**内容：** D-ENG-3 构建验证——sdist + wheel 构建，干净 venv 安装，`moodify doctor` 冒烟。

## 包内文件

| 文件 | 说明 |
|---|---|
| `build_dist/moodify-1.0.0rc1.tar.gz` | sdist（`python -m build`，版本与 `release.PRODUCT_VERSION` 统一） |
| `build_dist/moodify-1.0.0rc1-py3-none-any.whl` | wheel（同一构建产物） |
| `doctor_clean_install.json` | 干净 venv 安装后的 `moodify doctor` 完整 stdout（冒烟证据） |
| `MANIFEST.sha256` | 以上文件的 SHA-256（`venv_clean/` 为本地安装环境，不入包不入库） |

## doctor 冒烟判读

`doctor_clean_install.json` 关键字段（生成环境：Windows 10 / Python 3.11）：

- `"ready": true` — 可用性判据是数据字段，不是退出码（doctor 恒 exit 0）
- `"core_version": "1.0.0-rc.1"`、`"judgment_rules_version": "1.1"`
- `"ffmpeg": {"found": true, ...}` — 运行时同一解析器（PATH + Windows winget 链接）
- `"packages"` — 8 个关键依赖可导入并带版本

## 复现

```bash
cd moodify-core-package
python -m build --outdir ../artifacts/msp02_layer_d_001/build_dist
python -m venv ../artifacts/msp02_layer_d_001/venv_clean
../artifacts/msp02_layer_d_001/venv_clean/Scripts/python.exe -m pip install \
  ../artifacts/msp02_layer_d_001/build_dist/moodify-1.0.0rc1-py3-none-any.whl
../artifacts/msp02_layer_d_001/venv_clean/Scripts/moodify.exe --version
../artifacts/msp02_layer_d_001/venv_clean/Scripts/moodify.exe doctor
```

测试钉死：`tests/test_layer_d_packaging.py`（版本一致性、包名/license 稳定、doctor 探测数据、缺 ffmpeg 时诚实降级）。

## 事实边界

- 干净 venv 从 PyPI 实拉依赖安装成功 = 分发形态验证；**不等于**公开 PyPI 上架——那是外部发布动作，待人类另行指令。
- 本证据只覆盖 pip 通道（LD-2 裁决：唯一分发形态）；无容器、无单二进制。
- license 按 LD-1 零改动（GPL-3.0-only 保持）；云端计量按 LD-3 关闭；定价按 LD-4 延后（结构占位在提案 §8）。
- 一次先行尝试使用 pip `--require-hashes` 安装因哈希不匹配中止（wheel 为本地构建，无 PyPI 侧锁定哈希），改用直接 wheel 安装重跑，产物哈希以 `MANIFEST.sha256` 为准。
