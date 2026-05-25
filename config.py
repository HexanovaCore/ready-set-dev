"""
Auto Dev Environment Setup - Configuration & Environment Manager
Author: Your Name / Project Admin
Version: 1.2.0
Description: Centralizes all system constants, defaults, OS detection, 
             language support matrices, and logging themes.
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any


# ==========================================
# 1. APPLICATION METADATA & PATHS
# ==========================================
APP_NAME: str = "AutoDev Setup"
VERSION: str = "1.2.0"
CLI_PROG_NAME: str = "setup-my-project"

# Kullanıcının aracı çalıştırdığı aktif dizin (Target Project Directory)
CWD_PATH: Path = Path(os.getcwd())


# ==========================================
# 2. ADVANCED LANGUAGE SUPPORT MATRIX
# ==========================================
# Desteklenen tüm dillerin merkezi listesi (main.py help menüsü burayı okur)
SUPPORTED_LANGUAGES: List[str] = [
    "python", "node", "typescript", "go", "rust", "java", "dotnet", "cpp"
]

@dataclass(frozen=True)
class LanguageDefaults:
    """Her dil için değişmez (immutable) varsayılan ayarları tutan veri modeli."""
    version: str
    port: int
    manifest_file: str
    docker_base_image: str
    source_directory: str = "src"

# Sektör standartlarına göre optimize edilmiş dinamik dil matrisi
LANGUAGE_MATRIX: Dict[str, LanguageDefaults] = {
    "python": LanguageDefaults(
        version="3.11", port=8000, manifest_file="requirements.txt", docker_base_image="python:3.11-slim", source_directory="."
    ),
    "node": LanguageDefaults(
        version="20", port=3000, manifest_file="package.json", docker_base_image="node:20-alpine"
    ),
    "typescript": LanguageDefaults(
        version="20", port=3000, manifest_file="package.json", docker_base_image="node:20-alpine"
    ),
    "go": LanguageDefaults(
        version="1.22", port=8080, manifest_file="go.mod", docker_base_image="golang:1.22-alpine", source_directory="."
    ),
    "rust": LanguageDefaults(
        version="1.76", port=8080, manifest_file="Cargo.toml", docker_base_image="rust:1.76-slim"
    ),
    "java": LanguageDefaults(
        version="17", port=8080, manifest_file="pom.xml", docker_base_image="eclipse-temurin:17-jdk-alpine"
    ),
    "dotnet": LanguageDefaults(
        version="8.0", port=5000, manifest_file="Program.cs", docker_base_image="mcr.microsoft.com/dotnet/sdk:8.0"
    ),
    "cpp": LanguageDefaults(
        version="17", port=8080, manifest_file="CMakeLists.txt", docker_base_image="ubuntu:24.04", source_directory="."
    )
}


# ==========================================
# 3. CROSS-PLATFORM OS DETECTION & SHELL COMPATIBILITY
# ==========================================
IS_WINDOWS: bool = os.name == "nt"
IS_MAC: bool = sys.platform == "darwin"
IS_LINUX: bool = sys.platform.startswith("linux")

def get_virtualenv_exec_path(project_path: Path) -> Path:
    """İşletim sistemine göre Python venv binary (executable) yolunu döner."""
    if IS_WINDOWS:
        return project_path / "venv" / "Scripts" / "python.exe"
    return project_path / "venv" / "bin" / "python"

def get_system_shell() -> List[str]:
    """İşletim sistemine uygun güvenli alt süreç (subprocess) shell yapısını ayarlar."""
    if IS_WINDOWS:
        return ["cmd.exe", "/c"]
    return ["/bin/sh", "-c"]


# ==========================================
# 4. RICH TERMINAL INTERFACE THEME
# ==========================================
# Rich kütüphanesinin tüm CLI içinde kullanacağı renk şeması (Merkezi UI Tasarımı)
RICH_THEME_CONFIG: Dict[str, str] = {
    "info": "bold cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "danger": "bold red",
    "highlight": "bold magenta",
    "muted": "dim white"
}


# ==========================================
# 5. RUNTIME STATE MANAGEMENT
# ==========================================
@dataclass
class RuntimeSettings:
    """Kullanıcının CLI üzerinden girdiği flag'lere göre değişen dinamik çalışma ayarları."""
    verbose: bool = False
    dry_run: bool = False  # True ise diske yazmaz, sadece simüle eder (Test senaryoları için)
    override_existing: bool = False
    
    # Port ayarını öncelikle işletim sistemi Çevresel Değişkeninden (Environment Variable), yoksa varsayılandan alır
    default_port: int = field(
        default_factory=lambda: int(os.getenv("AUTODEV_DEFAULT_PORT", 8080))
    )

    def verify_system_dependencies(self) -> List[str]:
        """Projenin sağlıklı kurulması için sistemde bulunması gereken eksik araçları listeler (Docker, Git vb.)."""
        import shutil
        missing_tools = []
        required_tools = ["git", "docker"]
        
        for tool in required_tools:
            if not shutil.whoami() if IS_WINDOWS else shutil.which(tool):
                # Basit bir check mekanizması, geliştirilebilir
                if not shutil.which(tool):
                    missing_tools.append(tool)
        return missing_tools