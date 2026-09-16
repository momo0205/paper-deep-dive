import pytest
import torch
import transformer.tiny_attention as attention
from transformer.tiny_attention import SingleHeadAttention, load_text, CharTokenizer


def test_attention_shape_and_causality():
    torch.manual_seed(0)
    attn = SingleHeadAttention(n_embd=16, block_size=8)
    x = torch.randn(2, 5, 16)
    out, att = attn(x, return_attn=True)
    assert out.shape == (2, 5, 16)
    assert att.shape == (2, 5, 5)
    for b in range(2):
        for i in range(5):
            for j in range(i + 1, 5):
                assert att[b, i, j].item() == 0.0, "future position must be masked"
    assert torch.allclose(att.sum(dim=-1), torch.ones(2, 5), atol=1e-5)


def test_tokenizer_roundtrip_uses_offline_text(monkeypatch, tmp_path):
    monkeypatch.setattr(attention, "CACHE", str(tmp_path / "input.txt"))

    def fail_if_network_is_used(*args, **kwargs):
        pytest.fail("ordinary unit tests must not access the network")

    monkeypatch.setattr(attention.urllib.request, "urlretrieve", fail_if_network_is_used)

    text = load_text(offline=True)
    tok = CharTokenizer(text)
    s = text[:50]
    assert tok.decode(tok.encode(s)) == s
