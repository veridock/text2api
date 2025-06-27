"""
Narzędzia do zarządzania Docker i konteneryzacji
"""

import docker
import subprocess
import asyncio
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import tempfile
import shutil


class DockerManager:
    """Zarządza operacjami Docker"""

    def __init__(self):
        try:
            self.client = docker.from_env()
            self.docker_available = True
        except Exception:
            self.client = None
            self.docker_available = False

    def is_docker_available(self) -> bool:
        """Sprawdza czy Docker jest dostępny"""
        return self.docker_available

    def check_docker_daemon(self) -> bool:
        """Sprawdza czy Docker daemon działa"""
        if not self.docker_available:
            return False

        try:
            self.client.ping()
            return True
        except Exception:
            return False

    async def build_image(
        self,
        dockerfile_path: Union[str, Path],
        image_name: str,
        context_path: Union[str, Path] = None,
    ) -> Dict[str, Any]:
        """Buduje obraz Docker"""

        if not self.check_docker_daemon():
            return {"success": False, "error": "Docker daemon not available"}

        try:
            context_path = context_path or Path(dockerfile_path).parent

            # Zbuduj obraz
            image, logs = self.client.images.build(
                path=str(context_path),
                dockerfile=str(Path(dockerfile_path).name),
                tag=image_name,
                rm=True,
                forcerm=True,
            )

            # Zbierz logi
            build_logs = []
            for log in logs:
                if "stream" in log:
                    build_logs.append(log["stream"].strip())

            return {
                "success": True,
                "image_id": image.id,
                "image_name": image_name,
                "logs": build_logs,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def run_container(
        self,
        image_name: str,
        container_name: str = None,
        ports: Dict[str, str] = None,
        volumes: Dict[str, Dict[str, str]] = None,
        environment: Dict[str, str] = None,
        detach: bool = True,
    ) -> Dict[str, Any]:
        """Uruchamia kontener"""

        if not self.check_docker_daemon():
            return {"success": False, "error": "Docker daemon not available"}

        try:
            container = self.client.containers.run(
                image_name,
                name=container_name,
                ports=ports or {},
                volumes=volumes or {},
                environment=environment or {},
                detach=detach,
                remove=False,
            )

            return {
                "success": True,
                "container_id": container.id,
                "container_name": container.name,
                "status": container.status,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_container(self, container_name: str) -> Dict[str, Any]:
        """Zatrzymuje kontener"""

        try:
            container = self.client.containers.get(container_name)
            container.stop()

            return {"success": True, "message": f"Container {container_name} stopped"}

        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_name} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def remove_container(
        self, container_name: str, force: bool = False
    ) -> Dict[str, Any]:
        """Usuwa kontener"""

        try:
            container = self.client.containers.get(container_name)
            container.remove(force=force)

            return {"success": True, "message": f"Container {container_name} removed"}

        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_name} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_containers(self, all_containers: bool = False) -> List[Dict[str, Any]]:
        """Lista kontenerów"""

        if not self.check_docker_daemon():
            return []

        try:
            containers = self.client.containers.list(all=all_containers)

            return [
                {
                    "id": container.id[:12],
                    "name": container.name,
                    "image": container.image.tags[0]
                    if container.image.tags
                    else container.image.id[:12],
                    "status": container.status,
                    "ports": container.ports,
                }
                for container in containers
            ]

        except Exception:
            return []

    def list_images(self) -> List[Dict[str, Any]]:
        """Lista obrazów"""

        if not self.check_docker_daemon():
            return []

        try:
            images = self.client.images.list()

            return [
                {
                    "id": image.id[:12],
                    "tags": image.tags,
                    "size": image.attrs.get("Size", 0),
                }
                for image in images
            ]

        except Exception:
            return []

    async def compose_up(
        self, compose_file: Union[str, Path], detach: bool = True, build: bool = False
    ) -> Dict[str, Any]:
        """Uruchamia docker-compose"""

        compose_file = Path(compose_file)

        if not compose_file.exists():
            return {"success": False, "error": f"Compose file {compose_file} not found"}

        try:
            cmd = ["docker-compose", "-f", str(compose_file), "up"]

            if detach:
                cmd.append("-d")

            if build:
                cmd.append("--build")

            # Uruchom w tle
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=compose_file.parent,
            )

            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "returncode": process.returncode,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def compose_down(
        self, compose_file: Union[str, Path], remove_volumes: bool = False
    ) -> Dict[str, Any]:
        """Zatrzymuje docker-compose"""

        compose_file = Path(compose_file)

        try:
            cmd = ["docker-compose", "-f", str(compose_file), "down"]

            if remove_volumes:
                cmd.append("-v")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=compose_file.parent,
            )

            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "returncode": process.returncode,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_dockerfile(
        self, api_spec, base_image: str = "python:3.11-slim"
    ) -> str:
        """Generuje Dockerfile na podstawie specyfikacji API"""

        # Port mapping
        port_mapping = {
            "fastapi": 8000,
            "flask": 5000,
            "graphene": 8000,
            "grpc": 50051,
            "websockets": 8765,
            "click": None,  # CLI nie potrzebuje portu
        }

        port = port_mapping.get(api_spec.framework, 8000)

        dockerfile = f"""FROM {base_image}

# Metadata
LABEL maintainer="{api_spec.name}"
LABEL description="{api_spec.description}"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

"""

        if port:
            dockerfile += f"# Expose port\nEXPOSE {port}\n\n"

        # Command based on framework
        if api_spec.framework == "fastapi":
            dockerfile += (
                'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]'
            )
        elif api_spec.framework == "flask":
            dockerfile += 'CMD ["python", "app.py"]'
        elif api_spec.framework == "graphene":
            dockerfile += 'CMD ["python", "app.py"]'
        elif api_spec.framework == "grpc":
            dockerfile += 'CMD ["python", "server.py"]'
        elif api_spec.framework == "websockets":
            dockerfile += 'CMD ["python", "server.py"]'
        elif api_spec.framework == "click":
            dockerfile += 'ENTRYPOINT ["python", "cli.py"]'
        else:
            dockerfile += 'CMD ["python", "app.py"]'

        return dockerfile

    def generate_docker_compose(self, api_spec) -> str:
        """Generuje docker-compose.yml"""

        service_name = api_spec.name.replace("_", "-")

        # Port mapping
        port_mapping = {
            "fastapi": "8000:8000",
            "flask": "5000:5000",
            "graphene": "8000:8000",
            "grpc": "50051:50051",
            "websockets": "8765:8765",
        }

        compose = {
            "version": "3.8",
            "services": {
                service_name: {
                    "build": ".",
                    "container_name": service_name,
                    "restart": "unless-stopped",
                }
            },
        }

        # Dodaj porty jeśli nie CLI
        if api_spec.framework != "click":
            port = port_mapping.get(api_spec.framework, "8000:8000")
            compose["services"][service_name]["ports"] = [port]

        # Dodaj bazę danych jeśli wymagana
        if api_spec.database_required:
            compose["services"][service_name]["depends_on"] = ["db"]
            compose["services"][service_name]["environment"] = [
                f"DATABASE_URL=postgresql://user:password@db:5432/{service_name}"
            ]

            # Dodaj serwis bazy danych
            compose["services"]["db"] = {
                "image": "postgres:15",
                "container_name": f"{service_name}-db",
                "restart": "unless-stopped",
                "environment": [
                    f"POSTGRES_DB={service_name}",
                    "POSTGRES_USER=user",
                    "POSTGRES_PASSWORD=password",
                ],
                "volumes": ["postgres_data:/var/lib/postgresql/data"],
                "ports": ["5432:5432"],
            }

            compose["volumes"] = {"postgres_data": None}

        # Dodaj Redis jeśli wykryto cache/sessions
        if any(
            word in api_spec.description.lower()
            for word in ["cache", "session", "redis"]
        ):
            if "depends_on" not in compose["services"][service_name]:
                compose["services"][service_name]["depends_on"] = []
            compose["services"][service_name]["depends_on"].append("redis")

            compose["services"]["redis"] = {
                "image": "redis:7-alpine",
                "container_name": f"{service_name}-redis",
                "restart": "unless-stopped",
                "ports": ["6379:6379"],
            }

        return yaml.dump(compose, default_flow_style=False)

    def generate_dockerignore(self) -> str:
        """Generuje .dockerignore"""

        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Git
.git
.gitignore

# Documentation
*.md
docs/

# Development
node_modules/
npm-debug.log*
.tmp/
temp/

# Generated files
generated_apis/
*.log
"""

    async def optimize_dockerfile(self, dockerfile_content: str) -> str:
        """Optymalizuje Dockerfile"""

        # Podstawowe optymalizacje
        optimizations = [
            # Multi-stage build suggestion
            "# Consider using multi-stage build for smaller image size",
            "# FROM node:16-alpine AS builder",
            "# ... build steps ...",
            "# FROM python:3.11-slim AS runtime",
            "",
            # Cache optimization
            "# Copy requirements first for better layer caching",
            "# Install dependencies before copying source code",
            "",
            # Security
            "# Run as non-root user",
            "# RUN addgroup -g 1001 -S appgroup && adduser -S appuser -G appgroup",
            "# USER appuser",
            "",
            # Health check
            "# Add health check",
            "# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\",
            "#   CMD curl -f http://localhost:8000/health || exit 1",
        ]

        # Dodaj komentarze z optymalizacjami na początku
        optimized = "\n".join(optimizations) + "\n\n" + dockerfile_content

        return optimized

    def get_container_logs(
        self, container_name: str, tail: int = 100
    ) -> Dict[str, Any]:
        """Pobiera logi kontenera"""

        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=tail, timestamps=True).decode("utf-8")

            return {"success": True, "logs": logs, "container_status": container.status}

        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_name} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_container_stats(self, container_name: str) -> Dict[str, Any]:
        """Pobiera statystyki kontenera"""

        try:
            container = self.client.containers.get(container_name)
            stats = container.stats(stream=False)

            # Przetworz statystyki
            processed_stats = {
                "cpu_usage": self._calculate_cpu_percent(stats),
                "memory_usage": self._calculate_memory_usage(stats),
                "network_io": stats.get("networks", {}),
                "block_io": stats.get("blkio_stats", {}),
            }

            return {"success": True, "stats": processed_stats}

        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_name} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate_cpu_percent(self, stats: Dict[str, Any]) -> float:
        """Oblicza procent użycia CPU"""

        try:
            cpu_stats = stats["cpu_stats"]
            precpu_stats = stats["precpu_stats"]

            cpu_delta = (
                cpu_stats["cpu_usage"]["total_usage"]
                - precpu_stats["cpu_usage"]["total_usage"]
            )
            system_delta = (
                cpu_stats["system_cpu_usage"] - precpu_stats["system_cpu_usage"]
            )

            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (
                    (cpu_delta / system_delta)
                    * len(cpu_stats["cpu_usage"]["percpu_usage"])
                    * 100.0
                )
                return round(cpu_percent, 2)
        except (KeyError, ZeroDivisionError):
            pass

        return 0.0

    def _calculate_memory_usage(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Oblicza użycie pamięci"""

        try:
            memory_stats = stats["memory_stats"]

            used = memory_stats["usage"]
            limit = memory_stats["limit"]
            percent = (used / limit) * 100.0 if limit > 0 else 0.0

            return {
                "used_bytes": used,
                "limit_bytes": limit,
                "used_mb": round(used / (1024 * 1024), 2),
                "limit_mb": round(limit / (1024 * 1024), 2),
                "percent": round(percent, 2),
            }
        except KeyError:
            return {
                "used_bytes": 0,
                "limit_bytes": 0,
                "used_mb": 0,
                "limit_mb": 0,
                "percent": 0.0,
            }

    async def health_check_container(
        self, container_name: str, health_endpoint: str = "/health"
    ) -> Dict[str, Any]:
        """Sprawdza health kontenera"""

        try:
            container = self.client.containers.get(container_name)

            # Pobierz port kontenera
            ports = container.attrs["NetworkSettings"]["Ports"]
            port = None

            for container_port, host_ports in ports.items():
                if host_ports:
                    port = host_ports[0]["HostPort"]
                    break

            if not port:
                return {"success": False, "error": "No exposed ports found"}

            # Sprawdź health endpoint
            import aiohttp

            async with aiohttp.ClientSession() as session:
                try:
                    url = f"http://localhost:{port}{health_endpoint}"
                    async with session.get(url, timeout=5) as response:
                        status = response.status
                        text = await response.text()

                        return {
                            "success": status == 200,
                            "status_code": status,
                            "response": text,
                            "container_status": container.status,
                        }

                except aiohttp.ClientError as e:
                    return {
                        "success": False,
                        "error": f"Health check failed: {str(e)}",
                        "container_status": container.status,
                    }

        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_name} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cleanup_unused_resources(self) -> Dict[str, Any]:
        """Czyści nieużywane zasoby Docker"""

        if not self.check_docker_daemon():
            return {"success": False, "error": "Docker daemon not available"}

        try:
            # Usuń nieużywane kontenery
            containers_pruned = self.client.containers.prune()

            # Usuń nieużywane obrazy
            images_pruned = self.client.images.prune()

            # Usuń nieużywane volumy
            volumes_pruned = self.client.volumes.prune()

            # Usuń nieużywane sieci
            networks_pruned = self.client.networks.prune()

            return {
                "success": True,
                "containers_removed": containers_pruned.get("ContainersDeleted", []),
                "images_removed": len(images_pruned.get("ImagesDeleted", [])),
                "volumes_removed": len(volumes_pruned.get("VolumesDeleted", [])),
                "networks_removed": len(networks_pruned.get("NetworksDeleted", [])),
                "space_reclaimed": containers_pruned.get("SpaceReclaimed", 0)
                + images_pruned.get("SpaceReclaimed", 0),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_container_config(
        self, container_name: str, output_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """Eksportuje konfigurację kontenera"""

        try:
            container = self.client.containers.get(container_name)
            config = container.attrs

            # Zapisz konfigurację do pliku
            output_path = Path(output_path)

            with open(output_path, "w") as f:
                json.dump(config, f, indent=2, default=str)

            return {
                "success": True,
                "config_file": str(output_path),
                "container_id": container.id,
            }

        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_name} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def monitor_container(
        self, container_name: str, duration: int = 60, interval: int = 5
    ) -> List[Dict[str, Any]]:
        """Monitoruje kontener przez określony czas"""

        monitoring_data = []
        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < duration:
            try:
                # Pobierz statystyki
                stats = self.get_container_stats(container_name)

                if stats["success"]:
                    monitoring_data.append(
                        {
                            "timestamp": asyncio.get_event_loop().time(),
                            "stats": stats["stats"],
                        }
                    )

                await asyncio.sleep(interval)

            except Exception as e:
                monitoring_data.append(
                    {"timestamp": asyncio.get_event_loop().time(), "error": str(e)}
                )
                break

        return monitoring_data

    def get_system_info(self) -> Dict[str, Any]:
        """Pobiera informacje o systemie Docker"""

        if not self.check_docker_daemon():
            return {"success": False, "error": "Docker daemon not available"}

        try:
            info = self.client.info()
            version = self.client.version()

            return {
                "success": True,
                "docker_version": version.get("Version"),
                "api_version": version.get("ApiVersion"),
                "containers_running": info.get("ContainersRunning", 0),
                "containers_paused": info.get("ContainersPaused", 0),
                "containers_stopped": info.get("ContainersStopped", 0),
                "images": info.get("Images", 0),
                "memory_total": info.get("MemTotal", 0),
                "cpu_count": info.get("NCPU", 0),
                "storage_driver": info.get("Driver"),
                "kernel_version": info.get("KernelVersion"),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
