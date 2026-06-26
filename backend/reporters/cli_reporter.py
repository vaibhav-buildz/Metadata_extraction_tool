from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from typing import Dict, Any
 
console = Console()
 
class CLIReporter:
    @staticmethod
    def display(metadata: Dict[str, Any]):
        console.print(Panel(
            f"[bold orange1]🔍 FORENSICS[/bold orange1]\n"
            f"File: {metadata.get('filename', 'Unknown')}\n"
            f"Type: {metadata.get('file_type', 'Unknown')}\n"
            f"Size: {metadata.get('file_size_bytes', 0) / 1024:.2f} KB",
            title="[bold cyan]METADATA[/bold cyan]",
            border_style="cyan"
        ))
        
        for key, value in metadata.items():
            if key not in ('filename', 'file_type', 'file_size_bytes', 'anomalies') and isinstance(value, dict):
                table = Table(title=f"[orange1]{key.upper()}[/orange1]")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="green")
                for k, v in value.items():
                    table.add_row(k, str(v)[:100])
                console.print(table)
        
        if metadata.get('anomalies'):
            console.print(Panel(
                "\n".join(str(a) for a in metadata['anomalies']),
                title="[bold red]⚠️ ANOMALIES[/bold red]",
                border_style="red"
            ))
 
if __name__ == "__main__":
    print("✓ CLIReporter ready")
