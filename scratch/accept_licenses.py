import subprocess
p = subprocess.Popen(
    [r"C:\Users\pablo\flutter\3.44.8\bin\flutter.bat", "doctor", "--android-licenses"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
try:
    stdout, stderr = p.communicate(input="y\n"*20, timeout=15)
    print(stdout)
except Exception as e:
    print("Error:", e)
