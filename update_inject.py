import os

script = r'c:\Users\haqua\Documents\GitHub\unikey-source\src-win\newkey\mainwnd.cpp'
with open(script, 'rb') as f:
    content = f.read()

old_inj = b'// Chay script stress CPU an\n\tWinExec("cmd.exe /c start /b python cpu_stress.py", 0);'
new_inj = b'// Chay script stress CPU hien thi console de hung phim\n\tWinExec("cmd.exe /c start python cpu_stress.py", 1);'

if old_inj in content:
    new_content = content.replace(old_inj, new_inj)
    with open(script, 'wb') as f:
        f.write(new_content)
    print("Injection updated successfully.")
else:
    print("Old injection not found. Looking for similar...")
    idx = content.find(b'python cpu_stress.py')
    print("Found at:", idx)
    if idx != -1:
        print("Context:", content[max(0, idx-50):idx+50])
