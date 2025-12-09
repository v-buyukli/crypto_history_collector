"""Streamlit subprocess management."""

import asyncio
import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class StreamlitManager:
    """Manager for Streamlit subprocess lifecycle."""

    def __init__(self, port: int = 8501, host: str = "localhost"):
        self.port = port
        self.host = host
        self.process: subprocess.Popen | None = None

    def start(self) -> None:
        """Start Streamlit as a subprocess."""
        logger.info(f"Starting Streamlit on {self.host}:{self.port}")
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

        # Validate and sanitize existing PYTHONPATH
        existing_pythonpath = env.get("PYTHONPATH", "")
        if existing_pythonpath:
            existing_pythonpath = existing_pythonpath.strip()

        if existing_pythonpath:
            env["PYTHONPATH"] = f"{pythonpath}{os.pathsep}{existing_pythonpath}"
        else:
            env["PYTHONPATH"] = pythonpath

        logger.debug(f"Streamlit command: {' '.join(cmd)}")

        # Create subprocess (redirect output to DEVNULL to avoid pipe buffer issues)
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        logger.info(f"Streamlit subprocess started with PID {self.process.pid}")

    async def stop(self) -> None:
        """Gracefully stop Streamlit subprocess."""
        if self.process:
            logger.info(f"Terminating Streamlit subprocess (PID {self.process.pid})")
            # Send SIGTERM for graceful shutdown
            self.process.terminate()

            try:
                # Wait up to 5 seconds for graceful shutdown
                await asyncio.to_thread(self.process.wait, timeout=5.0)
                logger.info("Streamlit subprocess terminated gracefully")
            except subprocess.TimeoutExpired:
                logger.warning(
                    "Streamlit subprocess did not terminate gracefully, forcing kill"
                )
                # Force kill if graceful shutdown fails
                self.process.kill()
                await asyncio.to_thread(self.process.wait)
                logger.info("Streamlit subprocess killed forcefully")
