# 从三篇论文出发，回答三个问题

1. 为什么网络越深越难训练？——[ResNet](questions/q1-why-deep-networks-fail.md)
2. 为什么注意力能替代序列建模？——[Transformer](questions/q2-why-attention-works.md)
3. 为什么扩散模型能生成高质量样本？——[DDPM](questions/q3-why-diffusion-generates.md)

## 6–9 周学习循环

每周围绕一个问题执行同一循环：先写下自己的解释，再读固定版本的原论文并记录证据，接着运行最小实验，最后用 checkpoint 自测并修订解释。前 3 周分别完成 ResNet、Transformer、DDPM；第 4–6 周重做实验和交叉比较；第 7–9 周选择一个变体、记录假设与结果，并复盘仍未解决的问题。学习材料位于 `questions/`，证据与总结位于 `notes/`，自测位于 `checkpoints/`。

详细的每周行动和产出见 [学习方法](docs/learning-method.md)。

## 论文来源（固定官方 abstract 版本）

| 问题 | 论文 | 官方 abstract |
| --- | --- | --- |
| 深层网络训练 | Deep Residual Learning for Image Recognition | [arXiv:1512.03385v1](https://arxiv.org/abs/1512.03385v1) |
| 注意力机制 | Attention Is All You Need | [arXiv:1706.03762v7](https://arxiv.org/abs/1706.03762v7) |
| 扩散生成 | Denoising Diffusion Probabilistic Models | [arXiv:2006.11239v2](https://arxiv.org/abs/2006.11239v2) |

本仓库**不再分发 PDF**。请从 arXiv 官方获取；`papers.yml` 固定了每篇论文的版本、官方 PDF URL 和 SHA-256。下载后用以下命令获取并进行 hash 验证：

```bash
python scripts/fetch_papers.py --output-dir papers
```

下载的 PDF 被 `.gitignore` 排除，避免把第三方内容重新分发到仓库中。

## 从 clone 到测试

需要 Python 3.11。以下命令只需要网络来安装 Python 依赖；测试与 smoke 均不需要 API key，也不读取 PDF。

```bash
git clone <repository-url>
cd paper-deep-dive
python -m venv .venv
source .venv/bin/activate
pip install -e .
pytest -q
```

## 离线 smoke

三个 smoke 使用合成或仓库内的小型输入，写入显式输出目录，不下载数据集：

```bash
python code/resnet/plain_vs_residual.py --smoke --offline --output-dir /tmp/paper-deep-dive-resnet
python code/transformer/tiny_attention.py --smoke --offline --output-dir /tmp/paper-deep-dive-transformer
python code/ddpm/simple_ddpm.py --smoke --offline --output-dir /tmp/paper-deep-dive-ddpm
```

关于固定随机种子、CPU 运行预期、产物来源和 smoke 的解释，见[可复现性说明](docs/reproducibility.md)。参考输出目录的边界见 [outputs/reference/README.md](outputs/reference/README.md)。

## 许可与第三方材料

[MIT License](LICENSE) 只适用于本仓库的原创代码、文档和组织结构；链接的论文、PDF 与数据集仍分别受其作者和来源条款约束。本仓库不主张对这些第三方材料拥有所有权。
