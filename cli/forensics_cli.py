import click
from pathlib import Path
import sys
 
sys.path.insert(0, str(Path(__file__).parent.parent))
 
from backend.extractors.registry import get_extractor
from backend.reporters.cli_reporter import CLIReporter
from backend.reporters.html_reporter import HTMLReporter
from backend.reporters.json_reporter import JSONReporter
 
@click.group()
def cli():
    """Metadata Forensics Tool - Extract hidden metadata from files"""
    pass
 
@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['cli', 'html', 'json']), default='cli')
@click.option('--output', type=click.Path())
def analyze(file_path, format, output):
    """Analyze a single file"""
    try:
        extractor = get_extractor(file_path)
        metadata = extractor._safe_extract()
        
        if format == 'cli':
            CLIReporter.display(metadata)
        elif format == 'html':
            html = HTMLReporter.generate(metadata, output)
            if output:
                click.echo(f"✓ Report saved to {output}")
            else:
                click.echo(html)
        elif format == 'json':
            json_str = JSONReporter.generate(metadata, output)
            if not output:
                click.echo(json_str)
            else:
                click.echo(f"✓ Report saved to {output}")
    except ValueError as e:
        click.echo(f"✗ {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Failed: {e}", err=True)
        sys.exit(1)
 
@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def batch(directory):
    """Analyze all files in directory"""
    dir_path = Path(directory)
    files = list(dir_path.rglob('*'))
    click.echo(f"🔍 Scanning {len(files)} items...")
    count = 0
    for file_path in files:
        if file_path.is_file():
            try:
                extractor = get_extractor(str(file_path))
                metadata = extractor._safe_extract()
                click.echo(f"\n{'='*60}")
                CLIReporter.display(metadata)
                count += 1
            except ValueError:
                continue
            except Exception as e:
                click.echo(f"✗ Error: {file_path.name}: {e}", err=True)
    click.echo(f"\n✓ Analyzed {count} files")
 
if __name__ == '__main__':
    cli()
