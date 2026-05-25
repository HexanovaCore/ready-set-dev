"""
Auto Dev Environment Setup CLI
Author: Your Name / Project Admin
Version: 1.2.0
Description: Ultimate production-ready main entry point with flawless 
             Rich text layouts and dynamic language detection (TR/EN).
"""

import sys
import os
import locale
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

# Projenin diğer katmanlarından kuralları ve motoru çekiyoruz
from config import SUPPORTED_LANGUAGES, VERSION, CLI_PROG_NAME
from engine import SetupEngine

console = Console()

class SetupContext:
    def __init__(self):
        self.verbose = False
        self.project_path = os.getcwd()


# ==========================================
# 1. SİSTEM DİLİ ALGILAMA VE YERELLEŞTİRME (I18N)
# ==========================================
def get_system_language() -> str:
    """İşletim sisteminin dilini algılar (tr veya en döner)."""
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith("tr"):
            return "tr"
    except Exception:
        pass
    return "en"

SYS_LANG = get_system_language()

LOCALIZED_TEXTS = {
    "tr": {
        "title": f"🚀 Auto Dev Environment Setup Tool v{VERSION}",
        "desc": "Bu araç, projeniz için gerekli olan geliştirme ortamını (Docker, VS Code ayarları ve paket yönetim dosyaları) saniyeler içinde otomatik olarak kurar.",
        "supported": "DESTEKLENEN DİLLER/ORTAMLAR:",
        "examples_title": "Kullanım Örnekleri",
        "cmd_col": "Komut",
        "desc_col": "Açıklama",
        "help_desc": "Bu yardım ve kullanım kılavuzunu gösterir.",
        "init_desc_1": "Mevcut dizinde",
        "init_desc_2": "ortamı kurar.",
        "no_docker_desc": "Docker olmadan sadece ortam dosyalarını kurar.",
        "path_desc": "Belirtilen hedef klasörde ortamı kurar.",
        "more_info": "Daha fazla bilgi için alt komutların yanına da --help ekleyebilirsiniz. Örn: setup-my-project init --help",
        "start_log": "⚙️ Kurulum Başlıyor:",
        "success_title": "Başarılı",
        "success_msg": "✨ Tebrikler! Kurulum Başarıyla Tamamlandı.",
        "success_sub": "Geliştirmeye başlamak için şu komutları kullanabilirsiniz:",
        "error_title": "Kritik Hata",
        "error_msg": "Kurulum sırasında bir sorun oluştu:"
    },
    "en": {
        "title": f"🚀 Auto Dev Environment Setup Tool v{VERSION}",
        "desc": "This tool automatically sets up the required development environment (Docker, VS Code configs, and package management files) for your project in seconds.",
        "supported": "SUPPORTED LANGUAGES/ENVIRONMENTS:",
        "examples_title": "Usage Examples",
        "cmd_col": "Command",
        "desc_col": "Description",
        "help_desc": "Shows this help and usage guide.",
        "init_desc_1": "Sets up",
        "init_desc_2": "environment in the current directory.",
        "no_docker_desc": "Sets up environment files only, without Docker.",
        "path_desc": "Sets up environment in the specified target directory.",
        "more_info": "For more information, you can add --help next to subcommands. e.g., setup-my-project init --help",
        "start_log": "⚙️ Starting Setup:",
        "success_title": "Success",
        "success_msg": "✨ Congratulations! Setup Completed Successfully.",
        "success_sub": "You can use the following commands to start developing:",
        "error_title": "Critical Error",
        "error_msg": "An error occurred during setup:"
    }
}

T = LOCALIZED_TEXTS[SYS_LANG]


# ==========================================
# 2. GÖRSEL OLARAK KUSURSUZ YARDIM MENÜSÜ
# ==========================================
def show_custom_help():
    """Kullanıcı 'help' veya parametresiz çağırdığında göreceği zengin dökümantasyon."""
    
    # Dilleri çirkin tagler olmadan parlatmak için Rich markup string'i oluşturuyoruz
    languages_markup = ', '.join([f'[bold yellow]{lang}[/bold yellow]' for lang in SUPPORTED_LANGUAGES])
    
    # Tüm paneli tek bir akıllı Text nesnesiyle örüyoruz (Click'in bozma şansı yok)
    help_content = Text()
    help_content.append(f"{T['title']}\n\n", style="bold green")
    help_content.append(f"{T['desc']}\n\n", style="white")
    help_content.append(f"{T['supported']} ", style="bold cyan")
    
    # Text.from_markup() sayesinde string içindeki [bold yellow] ifadeleri gerçek renge dönüşür
    help_content.append(Text.from_markup(languages_markup))
                   
    # Paneli ekrana basıyoruz
    console.print(Panel.fit(help_content, border_style="blue"))
    
    # Kullanım Örnekleri Tablosu (Hiçbir tag sızamaz, katı stil tanımlı)
    table = Table(title=T["examples_title"], title_style="bold magenta", box=None)
    table.add_column(T["cmd_col"], style="bold cyan", no_wrap=True)
    table.add_column(T["desc_col"], style="dim white")
    
    table.add_row(f"{CLI_PROG_NAME} help", T["help_desc"])
    table.add_row(f"{CLI_PROG_NAME} init python", f"{T['init_desc_1']} Python {T['init_desc_2']}")
    table.add_row(f"{CLI_PROG_NAME} init node --no-docker", T["no_docker_desc"])
    table.add_row(f"{CLI_PROG_NAME} -p ./my-project init go", T["path_desc"])
    
    console.print(table)
    console.print(f"\n[dim white]{T['more_info']}[/dim white]\n")


# ==========================================
# 3. INTERCEPTOR & CLI GROUP CONFIGURATION
# ==========================================
class HelpCommandCLI(click.Group):
    """Kullanıcı doğrudan 'help' yazdığında algılayan yakalayıcı sınıf."""
    def parse_args(self, ctx, args):
        if args and args[0] == "help":
            show_custom_help()
            ctx.exit()
        return super().parse_args(ctx, args)

@click.group(cls=HelpCommandCLI, invoke_without_command=True)
@click.option('--verbose', '-v', is_flag=True, help='Detaylı log çıktısını etkinleştirir. / Enables verbose logging.')
@click.option('--path', '-p', type=click.Path(exists=True), help='Projenin kurulacağı dizin. / Target directory path.')
@click.version_option(version=VERSION, prog_name=CLI_PROG_NAME)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, path: Optional[str]):
    ctx.ensure_object(SetupContext)
    ctx.obj.verbose = verbose
    if path:
        ctx.obj.project_path = os.path.abspath(path)
        
    if ctx.invoked_subcommand is None:
        show_custom_help()


# ==========================================
# 4. EXECUTION COMMAND (INIT)
# ==========================================
@cli.command(name="init")
@click.argument('language', type=click.Choice(SUPPORTED_LANGUAGES, case_sensitive=False))
@click.option('--no-docker', is_flag=True, help='Dockerfile üretimini atlar. / Skips Dockerfile generation.')
@click.pass_context
def init_project(ctx: click.Context, language: str, no_docker: bool):
    """Geliştirme ortamını kurar. / Sets up the dev environment."""
    project_dir = ctx.obj.project_path
    language = language.lower()
    
    console.print(f"\n[bold blue]{T['start_log']}[/bold blue] [magenta]{language.upper()}[/magenta] -> [dim white]{project_dir}[/dim white]\n")
    
    # Modern animasyonlu yükleme barı
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        try:
            engine = SetupEngine(project_path=project_dir, language=language, verbose=ctx.obj.verbose)
            
            task1 = progress.add_task(description="[cyan]Scaffolding structure...[/cyan]", total=None)
            src_path = engine.create_scaffolding()
            progress.update(task1, completed=True)

            task2 = progress.add_task(description="[cyan]Generating manifest files...[/cyan]", total=None)
            engine.create_manifest()
            progress.update(task2, completed=True)

            task3 = progress.add_task(description="[cyan]Writing initial source code...[/cyan]", total=None)
            engine.create_initial_source(src_path)
            progress.update(task3, completed=True)

            if not no_docker:
                task4 = progress.add_task(description="[cyan]Generating Docker configurations...[/cyan]", total=None)
                engine.generate_docker()
                progress.update(task4, completed=True)
                
            task5 = progress.add_task(description="[cyan]Initializing environment (Git/Packages)...[/cyan]", total=None)
            engine.initialize_environment()
            progress.update(task5, completed=True)
            
        except Exception as e:
            console.print(f"\n[bold red]❌ {T['error_title']}:[/bold red] [white]{T['error_msg']} {str(e)}[/white]")
            if ctx.obj.verbose:
                console.print_exception()
            sys.exit(1)

    # Başarı Paneli
    console.print("\n")
    console.print(Panel(
        f"[bold green]{T['success_msg']}[/bold green]\n\n"
        f"[white]{T['success_sub']}[/white]\n"
        f"  [bold cyan]cd {os.path.basename(project_dir)}[/bold cyan]\n"
        f"  [bold cyan]code .[/bold cyan]",
        border_style="green",
        title=f"[bold green]{T['success_title']}[/bold green]"
    ))

if __name__ == "__main__":
    cli(obj=SetupContext())