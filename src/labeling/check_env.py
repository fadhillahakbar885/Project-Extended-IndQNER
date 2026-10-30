pkgs = ['torch', 'transformers', 'ollama', 'accelerate', 'seqeval', 'pypdf']
for pkg in pkgs:
    try:
        m = __import__(pkg)
        print(f"{pkg}: {getattr(m, '__version__', 'installed')}")
    except ImportError:
        print(f"{pkg}: NOT installed")

