"""
demo.py
1-click launch script for the Courtroom Video Analyzer Agent.
Starts the unified backend (FastAPI + Vision Agents) and the React frontend.
"""
import asyncio
import subprocess
import sys
from pathlib import Path

from backend.core.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


async def main():
    """Main entry point for the demo."""
    print("=" * 80)
    print("🚀 COURTROOM VIDEO ANALYZER AGENT - UNIFIED LAUNCHER")
    print("=" * 80)
    print()

    frontend_process = None
    backend_process = None

    try:
        # 1. Start the Unified Backend (API + Agent Orchestrator)
        print("[1/2] Starting Unified Backend (FastAPI + Vision Agents)...")
        print("   -> Starting 'uv run uvicorn backend.api.server:app --port 8000'")
        
        backend_process = subprocess.Popen(
            ["uv", "run", "uvicorn", "backend.api.server:app", "--port", "8000"],
            cwd=".",
            # Pipe output so we can see what's happening
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        print("✅ Backend Process spawned")
        print()

        # Give backend a moment to bind ports before frontend hammers it
        await asyncio.sleep(2)

        # 2. Start the Frontend 
        print("[2/2] Starting Stream frontend UI client...")
        frontend_path = Path("frontend")
        if not frontend_path.exists():
            print("⚠️  Frontend directory not found. Skipping frontend launch.")
            print("   Run 'pnpm create vite frontend --template react-ts' to create it.")
        else:
            try:
                frontend_process = subprocess.Popen(
                    ["pnpm", "run", "dev"],
                    cwd="./frontend",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print("✅ Frontend started successfully. Access http://localhost:5173")
            except Exception as e:
                print(f"⚠️  Could not start frontend: {e}")
        
        print("\nAll systems go! Press Ctrl+C to terminate everything.\n")

        # Keep the launcher running until interrupted
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown signal received. Terminating processes...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        if frontend_process:
            print("Terminating frontend process...")
            frontend_process.terminate()
            try:
                frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                frontend_process.kill()
                
        if backend_process:
            print("Terminating backend process...")
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
                
        print("✅ Cleanup complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
