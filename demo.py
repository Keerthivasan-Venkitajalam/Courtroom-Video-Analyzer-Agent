"""
demo.py
1-click launch script designed for the WeMakeDevs hackathon presentation.
Initializes the Vision Agent backend subprocesses and serves a minimal React frontend.
"""
import asyncio
import subprocess
import sys
from pathlib import Path

from agent import start_courtroom_agent
from constants import SESSION_ID, MOCK_CAMERA_STREAM


async def main():
    """Main entry point for the demo."""
    print("=" * 80)
    print("🚀 COURTROOM VIDEO ANALYZER AGENT - DEMO LAUNCHER")
    print("=" * 80)
    print()
    
    # Check if frontend exists
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("⚠️  Frontend directory not found. Skipping frontend launch.")
        print("   Run 'pnpm create vite frontend --template react-ts' to create it.")
        frontend_process = None
    else:
        # 1. Start the frontend client UI (React application using Stream Video SDK)
        print("[1/2] Starting Stream frontend UI client...")
        try:
            frontend_process = subprocess.Popen(
                ["pnpm", "run", "dev"],
                cwd="./frontend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("✅ Frontend started successfully")
        except Exception as e:
            print(f"⚠️  Could not start frontend: {e}")
            frontend_process = None
    
    print()
    
    try:
        # 2. Start the Vision Agent Backend (Connects autonomously to the same Stream room)
        print("[2/2] Starting Vision Agent Backend...")
        print(f"   Room ID: {SESSION_ID}")
        print(f"   Stream URL: {MOCK_CAMERA_STREAM}")
        print()
        
        # We utilize a local mock stream (via OBS or FFmpeg) for reliable live demoing 
        # without risking network degradation during the presentation.
        await start_courtroom_agent(SESSION_ID, MOCK_CAMERA_STREAM)
        
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
        print("✅ Cleanup complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
