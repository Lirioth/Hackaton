
import os, sys, subprocess, venv, platform

ROOT = os.path.abspath(os.path.dirname(__file__))
VENV_DIR = os.path.join(ROOT, ".venv")
PY = sys.executable

def ensure_venv():
    if not os.path.isdir(VENV_DIR):
        print("[*] Creating virtual environment .venv ...")
        venv.create(VENV_DIR, with_pip=True)
    else:
        print("[*] Using existing .venv")

def venv_python():
    if platform.system().lower().startswith("win"):
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")

def pip_install(py_path, *args):
    cmd = [py_path, "-m", "pip", "install", *args]
    print("[*] Running:", " ".join(cmd))
    subprocess.check_call(cmd)

def run_app(py_path, mode):
    if mode == "gui":
        cmd = [py_path, "-m", "novafit_plus.ui_tk"]
    else:
        cmd = [py_path, "-m", "novafit_plus.app"]
    print("[*] Launching:", " ".join(cmd))
    subprocess.check_call(cmd)

def main():
    mode = "gui" if ("--gui" in sys.argv) else "cli"
    ensure_venv()
    vpy = venv_python()
    # Upgrade pip
    try:
        pip_install(vpy, "--upgrade", "pip")
    except Exception as e:
        print("[!] pip upgrade failed:", e)
    # Install requirements safely
    req = os.path.join(ROOT, "requirements.txt")
    if not os.path.isfile(req):
        print("[!] requirements.txt not found at", req)
        sys.exit(1)
    pip_install(vpy, "-r", req)
    # Run
    run_app(vpy, "gui" if mode == "gui" else "cli")

if __name__ == "__main__":
    main()
