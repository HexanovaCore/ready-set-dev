"""
Auto Dev Environment Setup - Core Execution Engine
Author: Your Name / Project Admin
Version: 1.2.0
Description: Handles disk I/O, folder structure creation, template rendering,
             and system command executions across different OS platforms.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional
from config import LANGUAGE_MATRIX, get_system_shell, get_virtualenv_exec_path
from templates import TemplateManager


class SetupEngine:
    """Projenin fiziksel kurulum adımlarını yöneten ana motor sınıfı."""

    def __init__(self, project_path: str, language: str, verbose: bool = False):
        self.project_path = Path(project_path).resolve()
        self.language = language.lower()
        self.verbose = verbose
        
        # Dil konfigürasyonunu config.py matrisinden çekiyoruz
        if self.language not in LANGUAGE_MATRIX:
            raise ValueError(f"[-] Desteklenmeyen dil veya framework: {self.language}")
        self.lang_config = LANGUAGE_MATRIX[self.language]
        self.project_name = self.project_path.name

    def _write_file(self, file_path: Path, content: str) -> None:
        """Dosyaları güvenli bir şekilde diske yazar."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except IOError as e:
            raise RuntimeError(f"Dosya yazma hatası ({file_path.name}): {str(e)}")

    def _execute_command(self, command: str, working_dir: Optional[Path] = None) -> bool:
        """Sistem komutlarını işletim sistemine uygun shell üzerinde güvenlice koşturur."""
        shell_prefix = get_system_shell()
        full_command = shell_prefix + [command]
        target_dir = working_dir or self.project_path

        try:
            # Komut çıktılarını verbose moduna göre yönetiyoruz
            stdout_destination = None if self.verbose else subprocess.DEVNULL
            stderr_destination = None if self.verbose else subprocess.PIPE

            result = subprocess.run(
                full_command,
                cwd=str(target_dir),
                stdout=stdout_destination,
                stderr=stderr_destination,
                text=True,
                check=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            if self.verbose and e.stderr:
                print(f"\n[Komut Hatası]: {e.stderr}")
            raise RuntimeError(f"Komut yürütülemedi: '{command}'. Hata Kodu: {e.returncode}")

    def create_scaffolding(self) -> Path:
        """1. Adım: Projenin klasör yapısını ve .vscode ayarlarını inşa eder."""
        # Dilin özel kaynak kod klasörünü oluştur (Örn: src/ veya .)
        src_path = self.project_path / self.lang_config.source_directory
        src_path.mkdir(parents=True, exist_ok=True)

        # .vscode klasörünü oluştur ve ayarlarını yaz
        vscode_path = self.project_path / ".vscode" / "settings.json"
        vscode_content = TemplateManager.get_vscode_settings(self.language)
        self._write_file(vscode_path, vscode_content)

        return src_path

    def create_manifest(self) -> None:
        """2. Adım: package.json, requirements.txt veya CMakeLists.txt gibi manifestoları üretir."""
        manifest_name = self.lang_config.manifest_file
        manifest_path = self.project_path / manifest_name
        
        manifest_content = TemplateManager.get_manifest(
            language=self.language,
            project_name=self.project_name,
            version=self.lang_config.version
        )
        self._write_file(manifest_path, manifest_content)

    def create_initial_source(self, src_path: Path) -> None:
        """3. Adım: Geliştiricinin hemen çalıştırabileceği ilksel 'Hello World' kodunu üretir."""
        extension_map = {
            "python": "main.py", "node": "index.js", "typescript": "index.ts",
            "go": "main.go", "rust": "src/main.rs", "java": "src/com/autodev/Main.java",
            "dotnet": "Program.cs", "cpp": "main.cpp"
        }
        
        file_name = extension_map.get(self.language, "main.txt")
        # Eğer dil rust veya java ise src_path zaten kendi içinde yönetilir, çakışmayı önlemek için:
        target_file = self.project_path / file_name if "src/" in file_name else src_path / file_name

        source_content = TemplateManager.get_source_code(
            language=self.language,
            project_name=self.project_name,
            version=self.lang_config.version
        )
        self._write_file(target_file, source_content)

    def generate_docker(self) -> None:
        """4. Adım: Projeye özel Multi-Stage Dockerfile ve .dockerignore üretir."""
        docker_path = self.project_path / "Dockerfile"
        docker_content = TemplateManager.get_dockerfile(
            language=self.language,
            project_name=self.project_name,
            version=self.lang_config.version,
            port=self.lang_config.port
        )
        self._write_file(docker_path, docker_content)

        # .dockerignore üretimi
        ignore_path = self.project_path / ".dockerignore"
        ignore_content = "node_modules/\nvenv/\n.git/\nbuild/\ntarget/\nbin/\nobj/\n.vscode/\n"
        self._write_file(ignore_path, ignore_content)

    def initialize_environment(self) -> None:
        """5. Adım: Arka planda git init yapar veya dillerin venv/npm kurulumlarını tetikler."""
        # Her proje için Git ilklendirmesi
        try:
            self._execute_command("git init")
        except Exception:
            pass # Sistemde git kurulu değilse kurulumu durdurma, pas geç.

        # Dile özel terminal operasyonları
        if self.language == "python":
            # Sanal ortam oluştur (venv)
            self._execute_command("python -m venv venv")
            # Pip upgrade et ve bağımlılıkları yükle (isteğe bağlı ama profesyonel yaklaşım)
            venv_python = get_virtualenv_exec_path(self.project_path)
            self._execute_command(f'"{venv_python}" -m pip install --upgrade pip')
            
        elif self.language in ["node", "typescript"]:
            # Eğer kullanıcı makinesinde node yüklüyse npm install tetikle
            try:
                self._execute_command("npm install")
            except RuntimeError:
                # Node yüklü olmayabilir, sadece uyarı amaçlı geçebiliriz
                pass