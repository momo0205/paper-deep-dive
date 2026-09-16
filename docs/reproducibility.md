# 可复现性说明

## 运行边界

- **Python**：CI 与推荐环境为 Python 3.11；用 `python -m venv .venv` 后执行 `pip install -e .`。
- **硬件**：三个 `--smoke --offline` 入口面向 CPU 设计，使用很小的合成或仓库内输入；不要求 GPU，也不下载数据集。
- **随机性**：示例脚本在 smoke 模式固定其教学用随机种子。完整训练仍会受 PyTorch、NumPy、操作系统与硬件库版本影响；运行记录应注明命令、版本和 seed。
- **离线行为**：`--offline` 禁止下载数据或文本；所有产物必须通过 `--output-dir` 写到用户指定位置，不写回仓库。测试不需要 API key，也不需要本地 PDF。

## 论文与输出的来源

论文版本、官方 URL 和 SHA-256 位于仓库根目录的 `papers.yml`。PDF 不随仓库分发；使用 `python scripts/fetch_papers.py --output-dir papers` 从官方来源获取，脚本仅在 hash 与目录记录一致时保留下载文件。

`outputs/reference/` 只保存关于产物边界的说明。图像、权重、缓存、下载 PDF、数据集与实际运行输出都被忽略，避免把机器本地结果误当成可审计的基准。

## smoke 不是论文指标复现

smoke 的成功只说明：最小实现的命令行入口可以在离线 CPU 环境运行，并满足代码测试的结构性断言。它没有使用论文的完整训练预算、数据预处理、模型规模、硬件、超参数搜索或评估协议。因此，smoke 结果不等同于复现论文发表的准确率、损失、FID 或其他 published metrics。若要比较论文指标，应另行记录数据许可、完整配置、随机种子、硬件与评估过程。
