import subprocess

cmd = '''Get-CimInstance Win32_Process | Where-Object { $_.Name -eq "Unity.exe" } | Select-Object ProcessId, CommandLine | Format-List'''
res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
print(res.stdout)
