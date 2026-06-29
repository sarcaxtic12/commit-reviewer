# Commit Message Reviewer

A Python CLI tool to automatically review and rate git commit messages using LLMs via the OpenRouter API.

## Features

- Reviews recent commits in the current local repository, or clones a remote repository.
- Leverages the OpenRouter API (using `openai/gpt-oss-120b:free`) to review and rate each commit message as "excellent", "good", or "bad", along with a one-sentence reasoning.
- Real-time CLI output using `rich`.
- Generates a standalone, beautiful HTML report styled with Tailwind CSS.
- Hosts the report locally on port 3546.

## Setup & Installation

### Prerequisites

- Python 3.10+
- Git installed on your system

### Installation

1. Clone the repository or navigate to its directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. Install the dependencies and the package in editable mode:
   ```bash
   pip install -e .
   ```

### API Key Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

## Usage

Run the CLI tool globally:

```bash
# Review recent 10 commits in the current directory's repository
review-commits

# Review a remote repository with a custom limit of commits
review-commits --url "https://github.com/example/repo" --limit 5

# Get help options
review-commits --help
```
