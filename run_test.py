import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
exec(open("test_quick.py", encoding="utf-8").read())
