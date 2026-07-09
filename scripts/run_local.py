#!/usr/bin/env python3
"""
Run both frontend and backend locally for development.
This script starts the NextJS frontend and FastAPI backend in parallel.
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from collections import deque

# On Windows, npm/node are .cmd files and need shell=True to be found
IS_WINDOWS = sys.platform == "win32"

# Track subprocesses for cleanup
processes = []

def cleanup(signum=None, frame=None):
    """Clean up all subprocess on exit"""
    print("\n🛑 Shutting down services...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            proc.kill()
    sys.exit(0)

# Register cleanup handlers
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def check_requirements():
    """Check if required tools are installed"""
    checks = []

    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        node_version = result.stdout.strip()
        checks.append(f"✅ Node.js: {node_version}")
    except FileNotFoundError:
        checks.append("❌ Node.js not found - please install Node.js")

    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, shell=IS_WINDOWS)
        npm_version = result.stdout.strip()
        checks.append(f"✅ npm: {npm_version}")
    except FileNotFoundError:
        checks.append("❌ npm not found - please install npm")

    # Check uv (which manages Python for us)
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        uv_version = result.stdout.strip()
        checks.append(f"✅ uv: {uv_version}")
    except FileNotFoundError:
        checks.append("❌ uv not found - please install uv")

    print("\n📋 Prerequisites Check:")
    for check in checks:
        print(f"  {check}")

    # Exit if any critical tools are missing
    if any("❌" in check for check in checks):
        print("\n⚠️  Please install missing dependencies and try again.")
        sys.exit(1)

def check_env_files():
    """Check if environment files exist"""
    project_root = Path(__file__).parent.parent

    root_env = project_root / ".env"
    frontend_env = project_root / "frontend" / ".env.local"

    missing = []

    if not root_env.exists():
        missing.append(".env (root project file)")
    if not frontend_env.exists():
        missing.append("frontend/.env.local")

    if missing:
        print("\n⚠️  Missing environment files:")
        for file in missing:
            print(f"  - {file}")
        print("\nPlease create these files with the required configuration.")
        print("The root .env should have all backend variables from Parts 1-7.")
        print("The frontend/.env.local should have Clerk keys.")
        sys.exit(1)

    print("✅ Environment files found")

def start_backend():
    """Start the FastAPI backend"""
    backend_dir = Path(__file__).parent.parent / "backend" / "api"
    backend_workspace_dir = backend_dir.parent

    print("\n🚀 Starting FastAPI backend...")

    # Check if the backend workspace already has a uv environment.
    if not (backend_dir / ".venv").exists() and not (backend_workspace_dir / ".venv").exists():
        print("  Installing backend dependencies...")
        subprocess.run(["uv", "sync"], cwd=backend_dir, check=True)

    # Start the backend
    proc = subprocess.Popen(
        ["uv", "run", "main.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    processes.append(proc)

    # Wait for backend to start
    print("  Waiting for backend to start...")
    for _ in range(30):  # 30 second timeout
        if proc.poll() is not None:
            print(f"  ❌ Backend exited early with code {proc.returncode}")
            stderr_output = proc.stderr.read().strip()
            if stderr_output:
                print("  Backend stderr:")
                for line in stderr_output.splitlines()[-20:]:
                    print(f"    {line}")
            cleanup()
        try:
            import httpx
            response = httpx.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("  ✅ Backend running at http://localhost:8000")
                print("     API docs: http://localhost:8000/docs")
                return proc
        except:
            time.sleep(1)

    print("  ❌ Backend failed to start")
    cleanup()

def start_frontend():
    """Start the NextJS frontend"""
    frontend_dir = Path(__file__).parent.parent / "frontend"
    frontend_env = os.environ.copy()
    frontend_env["NEXT_TEST_WASM"] = "1"
    frontend_env["NEXT_TEST_WASM_DIR"] = str(frontend_dir / "node_modules" / "@next" / "swc-wasm-nodejs")

    # Next.js downloads the wasm SWC package into this cache dir when native SWC crashes.
    next_swc_cache = Path.home() / ".cache" / "next-swc"
    next_swc_cache.mkdir(parents=True, exist_ok=True)

    wasm_dir = Path(frontend_env["NEXT_TEST_WASM_DIR"])
    if not (wasm_dir / "wasm.js").exists():
        print("  ❌ Missing wasm SWC fallback package")
        print("  Run: cd frontend && npm install @next/swc-wasm-nodejs@15.5.3")
        cleanup()

    print("\n🚀 Starting NextJS frontend...")

    # Check if dependencies are installed
    if not (frontend_dir / "node_modules").exists():
        print("  Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True, shell=IS_WINDOWS)

    # Start the frontend
    proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Combine stderr with stdout
        text=True,
        bufsize=1,
        shell=IS_WINDOWS,
        env=frontend_env,
    )
    processes.append(proc)

    # Wait for frontend to start
    print("  Waiting for frontend to start...")
    import httpx
    import threading

    # Read frontend output in a background thread (select.select doesn't work on Windows pipes)
    started_flag = {"started": False}
    recent_output = deque(maxlen=20)

    def read_output():
        for line in proc.stdout:
            stripped = line.strip()
            recent_output.append(stripped)
            print(f"    Frontend: {stripped}")
            if "ready" in line.lower() or "compiled" in line.lower() or "started server" in line.lower():
                started_flag["started"] = True

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()

    for i in range(30):  # 30 second timeout
        if proc.poll() is not None:
            print(f"  ❌ Frontend exited early with code {proc.returncode}")
            if recent_output:
                print("  Frontend output before exit:")
                for line in recent_output:
                    print(f"    {line}")
            cleanup()

        if started_flag["started"] or i > 5:  # Start checking after 5 seconds
            try:
                response = httpx.get("http://localhost:3000", timeout=1)
                if response.status_code < 500:
                    print("  ✅ Frontend running at http://localhost:3000")
                    return proc
            except httpx.ConnectError:
                pass  # Server not ready yet
            except httpx.HTTPError:
                pass

        time.sleep(1)

    print("  ❌ Frontend failed to start")
    cleanup()

def monitor_processes():
    """Monitor running processes and show their output"""
    print("\n" + "="*60)
    print("🎯 Alex Financial Advisor - Local Development")
    print("="*60)
    print("\n📍 Services:")
    print("  Frontend: http://localhost:3000")
    print("  Backend:  http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print("\n📝 Logs will appear below. Press Ctrl+C to stop.\n")
    print("="*60 + "\n")

    # Monitor processes
    while True:
        for proc in processes:
            # Check if process is still running
            if proc.poll() is not None:
                print(f"\n⚠️  A process has stopped unexpectedly!")
                cleanup()

            # Read any available output
            try:
                line = proc.stdout.readline()
                if line:
                    print(f"[LOG] {line.strip()}")
            except:
                pass

        time.sleep(0.1)

def main():
    """Main entry point"""
    print("\n🔧 Alex Financial Advisor - Local Development Setup")
    print("="*50)

    # Check prerequisites
    check_requirements()
    check_env_files()

    # Install httpx if needed
    try:
        import httpx
    except ImportError:
        print("\n📦 Installing httpx for health checks...")
        subprocess.run(["uv", "add", "httpx"], check=True)

    # Start services
    backend_proc = start_backend()
    frontend_proc = start_frontend()

    # Monitor processes
    try:
        monitor_processes()
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
