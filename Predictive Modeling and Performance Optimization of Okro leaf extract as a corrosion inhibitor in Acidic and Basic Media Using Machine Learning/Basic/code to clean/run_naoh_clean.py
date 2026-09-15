import subprocess
import sys
import os

# Change to the correct directory
script_dir = r"../Machine Learning-Driven Corrosion Inhibition Study Okro Leaf Extract in Acidic and Basic Media/Basic/code to clean"
script_path = os.path.join(script_dir, "clean_NAOH.py")

# Run the script
try:
    result = subprocess.run([sys.executable, script_path], cwd=script_dir, capture_output=True, text=True)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    print(f"Return code: {result.returncode}")
except Exception as e:
    print(f"Error running script: {e}")
