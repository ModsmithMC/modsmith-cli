from modsmith_app.cli.install_cmd import loader_label


def test_loader_labels():
    assert loader_label("fabric", "0.16.10") == "Fabric 0.16.10"
    assert loader_label("neoforge", None) == "NeoForge"
    assert loader_label("test-loader", "1") == "test-loader 1"
    assert loader_label(None, None) == "no mod loader"
