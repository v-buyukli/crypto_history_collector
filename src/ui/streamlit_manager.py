"""Streamlit subprocess management."""

import asyncio
import os
import subprocess
from pathlib import Path


class StreamlitManager:
    """Manager for Streamlit subprocess lifecycle."""

    def __init__(self, port: int = 8501, host: str = "localhost"):
        self.port = port
        self.host = host
        self.process: subprocess.Popen | None = None

    def start(self) -> None:
        """Start Streamlit as a subprocess."""
        app_path = Path(__file__).parent / "streamlit_app.py"

        # Get project root directory (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent

        cmd = [
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            str(self.port),
            "--server.address",
            self.host,
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ]

        # Set up environment with PYTHONPATH
        env = os.environ.copy()
        pythonpath = str(project_root)
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{pythonpath}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = pythonpath

        # Create subprocess (non-blocking on Windows)
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

    async def stop(self) -> None:
        """Gracefully stop Streamlit subprocess."""
        if self.process:
            # Send SIGTERM for graceful shutdown
            self.process.terminate()

            try:
                # Wait up to 5 seconds for graceful shutdown
                await asyncio.to_thread(self.process.wait, timeout=5.0)
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                self.process.kill()
                await asyncio.to_thread(self.process.wait)
