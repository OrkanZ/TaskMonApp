import subprocess
import os

sdk_manager = r"C:\Users\pablo\AppData\Local\Android\Sdk\cmdline-tools\latest\bin\sdkmanager.bat"
packages = ["platforms;android-34", "build-tools;34.0.0", "platform-tools", "cmdline-tools;latest"]

env = os.environ.copy()
env["JAVA_HOME"] = r"C:\Users\pablo\java\17.0.13+11"

print("Installing packages...")
result = subprocess.run([sdk_manager, "--sdk_root=C:\\Users\\pablo\\AppData\\Local\\Android\\Sdk", *packages], env=env, input=b"y\n")
print(f"Return code: {result.returncode}")
