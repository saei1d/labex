import os
import secrets
import shutil
import socket
import subprocess
import uuid
from dataclasses import dataclass


class RuntimeErrorException(Exception):
    pass


@dataclass
class RuntimeContainer:
    container_id: str
    port: int
    access_token: str
    workspace_path: str


class ContainerRuntime:
    def __init__(self):
        self.docker_bin = shutil.which("docker")

    @staticmethod
    def _find_open_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return int(s.getsockname()[1])

    def _run(self, *args):
        if not self.docker_bin:
            raise RuntimeErrorException("docker binary is not available")
        proc = subprocess.run([self.docker_bin, *args], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeErrorException(proc.stderr.strip() or "docker command failed")
        return proc.stdout.strip()

    def create_session_container(self, image: str, session_key: str) -> RuntimeContainer:
        access_token = secrets.token_urlsafe(24)
        port = self._find_open_port()
        workspace_path = f"/tmp/labex-workspaces/{session_key}"
        os.makedirs(workspace_path, exist_ok=True)

        name = f"labex-{session_key}-{uuid.uuid4().hex[:8]}"
        container_id = self._run(
            "run",
            "-d",
            "--name",
            name,
            "--read-only",
            "--pids-limit",
            "256",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--memory",
            "1024m",
            "--cpus",
            "1.0",
            "-u",
            "1000:1000",
            "-p",
            f"{port}:8080",
            "-e",
            f"PASSWORD={access_token}",
            "-e",
            "SUDO_PASSWORD=disabled",
            "-e",
            "DEFAULT_WORKSPACE=/workspace",
            "-v",
            f"{workspace_path}:/workspace",
            image,
            "--auth",
            "password",
            "--bind-addr",
            "0.0.0.0:8080",
            "/workspace",
        )
        return RuntimeContainer(container_id=container_id, port=port, access_token=access_token, workspace_path=workspace_path)

    def stop_container(self, container_id: str):
        self._run("stop", container_id)

    def destroy_container(self, container_id: str):
        self._run("rm", "-f", container_id)


runtime = ContainerRuntime()
