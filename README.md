# Commit Message Reviewer

## What It Does

A Python CLI tool that reviews git commit messages using an LLM via the OpenRouter API. It extracts recent commits from any local or remote repository, rates each message as "excellent", "good", or "bad" with a one-sentence explanation, logs color-coded results to the terminal in real time, and generates a styled HTML report served locally in your browser.

## Requirements

- Python 3.10+
- Git installed and available on PATH
- An OpenRouter API key (free tier is sufficient) — https://openrouter.ai/keys

## Installation

```bash
# 1. Clone the repo
git clone <repo-url>
cd commit-reviewer

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install the package
pip install -e .
```

## Configuration

```bash
# Copy the example env file
cp .env.example .env

# Open .env and add your key
OPENROUTER_API_KEY=your_key_here
```

The `.env` file is gitignored and must never be committed.

## Usage

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--url` | None (uses cwd) | Remote repository URL to review |
| `--limit` | 10 | Number of recent commits to review |
| `--output` | `report.html` | Filename for the HTML report |
| `--port` | 3546 | Port to serve the report on |
| `--no-serve` | False | Skip the local server after generating the report |

**Examples:**

```bash
# Review the last 10 commits in the current directory
review-commits

# Review the last 5 commits in a remote repo
review-commits --url "https://github.com/psf/requests" --limit 5

# Custom report name and port
review-commits --limit 20 --output my-review.html --port 8080

# Generate report only, no browser
review-commits --limit 10 --no-serve
```

## Output

**Terminal:**

Each commit is logged as it is reviewed, showing the short hash, author, timestamp, commit message, rating, and reasoning. Ratings are color-coded: green for excellent, yellow for good, red for bad, and magenta for errors. After all commits are reviewed, a summary panel displays the total counts per rating.

**HTML Report:**

A self-contained HTML file styled with Tailwind CSS. It includes a header with the generation timestamp and total commit count, a summary bar with color-coded counters, and one card per commit showing the hash, author, timestamp, message, rating badge, and reasoning. The report is served locally and can also be opened manually from the output path.

## Project Structure

```text
commit-reviewer/
├── review_commits/
│   ├── __init__.py       # Package metadata
│   ├── cli.py            # Entry point, click commands, orchestration
│   ├── git_handler.py    # Local and remote commit extraction via GitPython
│   ├── llm_client.py     # OpenRouter API calls, response parsing
│   ├── report.py         # HTML report generation
│   └── server.py         # http.server wrapper, browser launch
├── .env                  # API key (gitignored)
├── .env.example          # Key template (committed)
├── .gitignore
├── pyproject.toml        # Package config and CLI entrypoint
├── requirements.txt
└── README.md
```

## How It Works

1. CLI parses flags and loads the API key from `.env`
2. GitPython opens the repo (or clones it to a temp dir for remote URLs)
3. The last N commit messages are extracted and structured
4. Each message is sent to OpenRouter (`openai/gpt-oss-120b:free`) individually
5. The model returns a rating (excellent / good / bad) and a one-sentence reason
6. Each result is logged to the terminal in real time with color coding via `rich`
7. After all commits are reviewed, a summary panel is printed
8. An HTML report is generated with Tailwind CSS and written to the working directory
9. A local `http.server` instance serves the file on `localhost:3546`
10. The report opens automatically in the default browser

## Limitations

- Only public repositories are supported for `--url` (no auth)
- Free OpenRouter model may apply rate limits for large `--limit` values
- HTML report is written to and served from the current working directory
- No persistent storage — each run overwrites the previous report file

## Troubleshooting

### `review-commits` not recognized in PowerShell
The virtual environment's Scripts directory may not be on your PATH.

Option 1 — Run via the venv directly:
    .venv\Scripts\review-commits

Option 2 — Run as a module:
    python -m review_commits.cli

Option 3 — Activate the venv first, then run:
    .venv\Scripts\activate
    review-commits
