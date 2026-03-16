# utils/logger.py
# ============================================================
# AI Blog Writer — Rich Console Logger
# Prints colour-coded stage output so you can trace the DAG.
# ============================================================

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def log_stage(stage: str, message: str, style: str = "bold cyan"):
    console.print(f"\n[{style}]▶  {stage}[/{style}]  {message}")


def log_success(message: str):
    console.print(f"[bold green]✅  {message}[/bold green]")


def log_warning(message: str):
    console.print(f"[bold yellow]⚠️   {message}[/bold yellow]")


def log_error(message: str):
    console.print(f"[bold red]❌  {message}[/bold red]")


def log_info(message: str):
    console.print(f"[dim]   ℹ  {message}[/dim]")


def log_section(title: str, content: str):
    console.print(Panel(content[:300] + "...", title=f"[bold]{title}[/bold]", expand=False))


def log_final_blog(title: str, word_count: int, sections: int):
    console.print(
        Panel(
            f"[bold green]Title:[/bold green] {title}\n"
            f"[bold green]Words:[/bold green] {word_count}\n"
            f"[bold green]Sections:[/bold green] {sections}\n"
            f"[bold green]Status:[/bold green] Production Ready ✅",
            title="🎉 AI Blog Writer — Blog Generated",
            border_style="green",
        )
    )
