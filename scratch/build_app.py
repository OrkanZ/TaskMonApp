import subprocess
import os
import shutil

if os.path.exists("build"):
    shutil.rmtree("build", ignore_errors=True)

env = os.environ.copy()
env["PYTHONUTF8"] = "1"

cmd = [
    os.path.join("venv", "Scripts", "flet.exe"),
    "build", "apk",
    "--exclude", "venv",
    "--android-extract-packages", "certifi"
]

print("Iniciando compilacion...")
result = subprocess.run(cmd, env=env)
print("Terminado con codigo:", result.returncode)
