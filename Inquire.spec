# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Inquire.py'],
    pathex=[r'Z:\Django-Deployer\pythonProject'],
    binaries=[],
    datas=[
        ('baseurls.py', '.'),
        ('Deploy.py', '.'),
        ('models.py', '.'),
        #('ribbon.png', '.'),
        #('rr.ico', '.'),
        ('static.zip', '.'),
        ('tasks.py', '.'),
        ('templates.zip', '.'),
        ('urls.py', '.'),
        ('views.py', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Django Quick-Deploy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    uac_admin=False,
    #icon='rr.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
