"""
Narzędzia do zarządzania plikami i katalogami
"""

import os
import json
import yaml
import shutil
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import tempfile
import zipfile
import tarfile


class FileManager:
    """Zarządza operacjami na plikach i katalogach"""

    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "text2api"
        self.temp_dir.mkdir(exist_ok=True)

    async def ensure_directory(self, path: Union[str, Path]) -> Path:
        """Upewnia się, że katalog istnieje"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    async def write_file(
        self, path: Union[str, Path], content: str, encoding: str = "utf-8"
    ) -> None:
        """Zapisuje plik asynchronicznie"""
        path = Path(path)
        await self.ensure_directory(path.parent)

        async with aiofiles.open(path, "w", encoding=encoding) as f:
            await f.write(content)

    async def read_file(self, path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Odczytuje plik asynchronicznie"""
        async with aiofiles.open(path, "r", encoding=encoding) as f:
            return await f.read()

    async def write_json(
        self, path: Union[str, Path], data: Dict[str, Any], indent: int = 2
    ) -> None:
        """Zapisuje dane jako JSON"""
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        await self.write_file(path, content)

    async def read_json(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Odczytuje JSON"""
        content = await self.read_file(path)
        return json.loads(content)

    async def write_yaml(self, path: Union[str, Path], data: Dict[str, Any]) -> None:
        """Zapisuje dane jako YAML"""
        content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        await self.write_file(path, content)

    async def read_yaml(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Odczytuje YAML"""
        content = await self.read_file(path)
        return yaml.safe_load(content)

    def copy_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Kopiuje plik"""
        shutil.copy2(src, dst)

    def copy_directory(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Kopiuje cały katalog"""
        if Path(dst).exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    def remove_file(self, path: Union[str, Path]) -> None:
        """Usuwa plik"""
        Path(path).unlink(missing_ok=True)

    def remove_directory(self, path: Union[str, Path]) -> None:
        """Usuwa katalog rekurencyjnie"""
        shutil.rmtree(path, ignore_errors=True)

    def list_files(
        self, directory: Union[str, Path], pattern: str = "*", recursive: bool = False
    ) -> List[Path]:
        """Lista plików w katalogu"""
        directory = Path(directory)

        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))

    def get_file_size(self, path: Union[str, Path]) -> int:
        """Zwraca rozmiar pliku w bajtach"""
        return Path(path).stat().st_size

    def file_exists(self, path: Union[str, Path]) -> bool:
        """Sprawdza czy plik istnieje"""
        return Path(path).exists()

    def is_directory(self, path: Union[str, Path]) -> bool:
        """Sprawdza czy to katalog"""
        return Path(path).is_dir()

    async def create_temp_file(self, suffix: str = ".tmp", content: str = "") -> Path:
        """Tworzy tymczasowy plik"""
        temp_file = self.temp_dir / f"temp_{asyncio.current_task().get_name()}{suffix}"
        await self.write_file(temp_file, content)
        return temp_file

    async def create_temp_directory(self) -> Path:
        """Tworzy tymczasowy katalog"""
        temp_dir = self.temp_dir / f"temp_dir_{asyncio.current_task().get_name()}"
        await self.ensure_directory(temp_dir)
        return temp_dir

    def cleanup_temp_files(self) -> None:
        """Czyści tymczasowe pliki"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir(exist_ok=True)

    async def backup_file(
        self, path: Union[str, Path], backup_suffix: str = ".backup"
    ) -> Path:
        """Tworzy kopię zapasową pliku"""
        path = Path(path)
        backup_path = path.with_suffix(path.suffix + backup_suffix)

        if path.exists():
            self.copy_file(path, backup_path)

        return backup_path

    async def restore_backup(self, backup_path: Union[str, Path]) -> Path:
        """Przywraca plik z kopii zapasowej"""
        backup_path = Path(backup_path)
        original_path = backup_path.with_suffix(
            backup_path.suffix.replace(".backup", "")
        )

        if backup_path.exists():
            self.copy_file(backup_path, original_path)
            backup_path.unlink()

        return original_path

    def create_archive(
        self,
        source_dir: Union[str, Path],
        archive_path: Union[str, Path],
        format: str = "zip",
    ) -> None:
        """Tworzy archiwum z katalogu"""
        source_dir = Path(source_dir)
        archive_path = Path(archive_path)

        if format.lower() == "zip":
            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in source_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(source_dir)
                        zipf.write(file_path, arcname)

        elif format.lower() in ["tar", "tar.gz", "tgz"]:
            mode = "w:gz" if format.lower() in ["tar.gz", "tgz"] else "w"
            with tarfile.open(archive_path, mode) as tarf:
                tarf.add(source_dir, arcname=source_dir.name)

        else:
            raise ValueError(f"Nieobsługiwany format archiwum: {format}")

    def extract_archive(
        self, archive_path: Union[str, Path], extract_to: Union[str, Path]
    ) -> None:
        """Wypakuje archiwum"""
        archive_path = Path(archive_path)
        extract_to = Path(extract_to)

        extract_to.mkdir(parents=True, exist_ok=True)

        if archive_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(archive_path, "r") as zipf:
                zipf.extractall(extract_to)

        elif archive_path.suffix.lower() in [".tar", ".gz", ".tgz"]:
            with tarfile.open(archive_path, "r:*") as tarf:
                tarf.extractall(extract_to)

        else:
            raise ValueError(f"Nieobsługiwany format archiwum: {archive_path.suffix}")

    async def watch_file_changes(
        self, path: Union[str, Path], callback, interval: float = 1.0
    ) -> None:
        """Monitoruje zmiany w pliku (prosty polling)"""
        path = Path(path)
        last_modified = path.stat().st_mtime if path.exists() else 0

        while True:
            await asyncio.sleep(interval)

            if path.exists():
                current_modified = path.stat().st_mtime
                if current_modified != last_modified:
                    await callback(path)
                    last_modified = current_modified
            elif last_modified > 0:
                # Plik został usunięty
                await callback(path, deleted=True)
                last_modified = 0

    def get_file_info(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Zwraca informacje o pliku"""
        path = Path(path)

        if not path.exists():
            return {"exists": False}

        stat = path.stat()

        return {
            "exists": True,
            "path": str(path.absolute()),
            "name": path.name,
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "is_directory": path.is_dir(),
            "is_file": path.is_file(),
            "permissions": oct(stat.st_mode)[-3:],
            "extension": path.suffix,
        }

    def find_files_by_content(
        self, directory: Union[str, Path], search_term: str, file_pattern: str = "*.py"
    ) -> List[Path]:
        """Znajdź pliki zawierające określony tekst"""
        directory = Path(directory)
        matching_files = []

        for file_path in directory.rglob(file_pattern):
            if file_path.is_file():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if search_term in content:
                            matching_files.append(file_path)
                except (UnicodeDecodeError, PermissionError):
                    continue

        return matching_files

    async def batch_process_files(
        self, files: List[Path], processor_func, max_concurrent: int = 10
    ) -> List[Any]:
        """Przetwarza pliki wsadowo z ograniczeniem współbieżności"""

        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(file_path):
            async with semaphore:
                return await processor_func(file_path)

        tasks = [process_with_semaphore(file_path) for file_path in files]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def calculate_directory_size(self, directory: Union[str, Path]) -> int:
        """Oblicza całkowity rozmiar katalogu"""
        directory = Path(directory)
        total_size = 0

        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return total_size

    def format_file_size(self, size_bytes: int) -> str:
        """Formatuje rozmiar pliku do czytelnej formy"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    async def sync_directories(
        self,
        source: Union[str, Path],
        target: Union[str, Path],
        exclude_patterns: List[str] = None,
    ) -> Dict[str, List[str]]:
        """Synchronizuje katalogi (podstawowa implementacja)"""
        source = Path(source)
        target = Path(target)
        exclude_patterns = exclude_patterns or []

        result = {"copied": [], "updated": [], "deleted": [], "errors": []}

        try:
            # Kopiuj/aktualizuj pliki
            for source_file in source.rglob("*"):
                if source_file.is_file():
                    # Sprawdź wykluczenia
                    relative_path = source_file.relative_to(source)
                    if any(
                        relative_path.match(pattern) for pattern in exclude_patterns
                    ):
                        continue

                    target_file = target / relative_path

                    if not target_file.exists():
                        await self.ensure_directory(target_file.parent)
                        self.copy_file(source_file, target_file)
                        result["copied"].append(str(relative_path))
                    elif source_file.stat().st_mtime > target_file.stat().st_mtime:
                        self.copy_file(source_file, target_file)
                        result["updated"].append(str(relative_path))

            # Usuń pliki, które nie istnieją w source
            if target.exists():
                for target_file in target.rglob("*"):
                    if target_file.is_file():
                        relative_path = target_file.relative_to(target)
                        source_file = source / relative_path

                        if not source_file.exists():
                            target_file.unlink()
                            result["deleted"].append(str(relative_path))

        except Exception as e:
            result["errors"].append(str(e))

        return result
