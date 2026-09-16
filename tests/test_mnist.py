import builtins
import socket
import urllib.request

import numpy as np
import pytest
import common.mnist as mnist


def test_load_mnist_offline_skips_network_sources_and_cache_creation(monkeypatch, tmp_path):
    """The public offline loader must not import download clients or create a cache."""
    cache_dir = tmp_path / "mnist-cache"
    monkeypatch.setattr(mnist, "CACHE_DIR", str(cache_dir))

    real_import = builtins.__import__

    def fail_if_dataset_client_is_imported(name, *args, **kwargs):
        if name == "torchvision" or name.startswith("torchvision."):
            pytest.fail("offline loader imported torchvision")
        if name == "sklearn" or name.startswith("sklearn."):
            pytest.fail("offline loader imported sklearn")
        return real_import(name, *args, **kwargs)

    def fail_if_cache_is_created(*args, **kwargs):
        pytest.fail("offline loader created a dataset cache")

    def fail_if_network_is_used(*args, **kwargs):
        pytest.fail("offline loader attempted a network connection")

    monkeypatch.setattr(builtins, "__import__", fail_if_dataset_client_is_imported)
    monkeypatch.setattr(mnist.os, "makedirs", fail_if_cache_is_created)
    monkeypatch.setattr(socket, "create_connection", fail_if_network_is_used)
    monkeypatch.setattr(socket.socket, "connect", fail_if_network_is_used)
    monkeypatch.setattr(urllib.request, "urlopen", fail_if_network_is_used)
    monkeypatch.setattr(urllib.request, "urlretrieve", fail_if_network_is_used)

    x_tr, y_tr, x_te, y_te = mnist.load_mnist(
        n_train=100, n_test=20, offline=True,
    )

    assert x_tr.shape == (100, 784)
    assert y_tr.shape == (100,)
    assert x_te.shape == (20, 784)
    assert y_te.shape == (20,)
    assert x_tr.dtype == np.float32
    assert y_tr.dtype == np.int64
    assert x_tr.min() >= 0.0 and x_tr.max() <= 1.0
    assert y_tr.min() >= 0 and y_tr.max() <= 9
    assert not cache_dir.exists()
