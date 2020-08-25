import sys

script_descriptor = open("buildKBs.py")
a_script = script_descriptor.read()

sys.argv = [
'-delppath', '/home/mario/results/tool/genGiani/small/delp0.delp',
'-nvar', '20',
'-nvaruse', '20',
'-outpath', '/home/mario/results/'
]

exec(a_script)
script_descriptor.close()
