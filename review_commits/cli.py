import click
import os
import time
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markup import escape
from review_commits.git_handler import get_local_commits, get_remote_commits
from review_commits.llm_client import review_commit
from review_commits.report import generate
from review_commits.server import serve

# Load env variables from .env
load_dotenv()

console = Console()

@click.command()
@click.option("--url", default=None, help="Remote Git repository URL to review.")
@click.option("--limit", default=10, show_default=True, type=int, help="Number of recent commits to review.")
@click.option("--output", default="report.html", show_default=True,
              help="Filename to write the HTML report to.")
@click.option("--port", default=3546, show_default=True, type=int,
              help="Port to serve the HTML report on.")
@click.option("--no-serve", is_flag=True, default=False,
              help="Generate the report but do not start the local server.")
def main(url, limit, output, port, no_serve):
    """A CLI tool to review git commit messages."""

    # Validate --output is a plain filename, not a path
    if os.sep in output or "/" in output:
        raise click.ClickException(
            "--output must be a filename only, not a path. Use a plain name like report.html"
        )

    # Validate --port range
    if not (1024 <= port <= 65535):
        raise click.BadParameter("Port must be between 1024 and 65535.", param_hint="--port")

    if url:
        commits = get_remote_commits(url, limit)
    else:
        commits = get_local_commits(os.getcwd(), limit)

    console.print(f"\n[bold]Reviewing {len(commits)} commits...[/bold]\n")

    results = []
    excellent = 0
    good = 0
    bad = 0
    error = 0

    rating_colors = {
        "excellent": "bold green",
        "good": "bold yellow",
        "bad": "bold red",
        "error": "bold magenta"
    }

    for idx, c in enumerate(commits):
        r = review_commit(c["message"])
        results.append({**c, "rating": r["rating"], "reason": r["reason"]})

        # Count ratings
        if r["rating"] == "excellent":
            excellent += 1
        elif r["rating"] == "good":
            good += 1
        elif r["rating"] == "bad":
            bad += 1
        else:
            error += 1

        # Real-time console logs
        console.print(f"[dim][{c['hash']}][/dim] [cyan]{escape(c['author'])}[/cyan] | {c['timestamp']}")
        console.print(f'"{escape(c["message"])}"')
        
        color = rating_colors.get(r["rating"], "bold magenta")
        console.print(f"-> [{color}]{r['rating'].upper()}[/{color}]: {escape(r['reason'])}")
        console.print()

        # Rate limit protection (sleep 1 second between API calls, except after the last commit)
        if idx < len(commits) - 1:
            time.sleep(1)

    # Generate summary panel
    summary_lines = [
        f"+ {excellent} excellent",
        f"~ {good} good",
        f"x {bad} bad"
    ]

    if error > 0:
        summary_lines.append(f"! {error} errors")
        
    summary_text = "\n".join(summary_lines)
    console.print(Panel(summary_text, title="Review Complete", border_style="dim", expand=False))

    console.print("\n[bold]Generating report...[/bold]")
    report_path = generate(results, output_path=output)
    console.print(f"[green]Report written:[/green] {report_path}\n")

    if no_serve:
        console.print("Open it manually in your browser.")
    else:
        serve(report_path, port=port)

if __name__ == "__main__":
    main()
