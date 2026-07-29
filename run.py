from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    subprocess.run(["npm", "start"], cwd=ROOT, check=False)
