import pathlib,subprocess,sys
P=pathlib.Path(__file__).resolve().parent
# Source merge, coverage verification, cleanup, and final inventory must be sequential.
for name in ['续接落盘.py','收口.py','清理已读缓存.py','收口.py']:
 subprocess.run([sys.executable,str(P/name)],check=True)
