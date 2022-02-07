# -*- mode: python -*-
import importlib
import os
import pkg_resources

block_cipher = None

datas = [("./tutor/templates", "./tutor/templates")]
hidden_imports = []

# Auto-discover plugins and include patches & templates folders
for entrypoint in pkg_resources.iter_entry_points("tutor.plugin.v0"):
    plugin_name = entrypoint.name
    try:
        plugin = entrypoint.load()
    except Exception as e:
        print(f"ERROR Failed to load plugin {plugin_name}: {e}")
        continue
    plugin_root = os.path.dirname(plugin.__file__)
    plugin_root_module_name = os.path.basename(plugin_root)
    hidden_imports.append(entrypoint.module_name)
    for folder in ["patches", "templates"]:
        path = os.path.join(plugin_root, folder)
        if os.path.exists(path):
            datas.append((path, os.path.join(plugin_root_module_name, folder)))
# Fix license import: if we don't declare some modules, pyinstaller does not find them
hidden_imports.append("tutorlts.__about__")
hidden_imports.append("Crypto.Cipher.AES")
hidden_imports.append("Crypto.Cipher.PKCS1_OAEP")
hidden_imports.append("Crypto.Hash.SHA256")
hidden_imports.append("Crypto.PublicKey.RSA")
hidden_imports.append("Crypto.Random")
hidden_imports.append("Crypto.Signature.PKCS1_v1_5")
hidden_imports.append("kubernetes")
hidden_imports.append("uuid")


# The following was initially generated with:
# pyinstaller --onefile --name=tutor --add-data=./tutor/templates:./tutor/templates ./bin/main.py

a = Analysis(
    ["bin/main.py"],
    pathex=[os.path.abspath(".")],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="tutor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,
)
