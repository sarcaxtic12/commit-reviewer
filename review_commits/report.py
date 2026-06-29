"""Report generator module for commit-reviewer.

Generates an HTML report styled with Tailwind CSS.
"""

import os
import html
from datetime import datetime

def generate(results: list[dict], output_path: str = "report.html") -> str:
    """Generate HTML report from review results.
    
    Args:
        results: A list of dictionaries containing the review results.
        output_path: The path where the HTML report will be saved.
        
    Returns:
        The absolute path to the generated HTML file.
    """
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(results)
    
    excellent = sum(1 for r in results if r["rating"] == "excellent")
    good = sum(1 for r in results if r["rating"] == "good")
    bad = sum(1 for r in results if r["rating"] == "bad")
    error = sum(1 for r in results if r["rating"] == "error")
    
    summary_bar = f"""
    <div class="flex gap-6 mb-8 p-4 bg-gray-900 rounded-lg border border-gray-800">
      <span class="text-green-400 font-bold">✓ {excellent} Excellent</span>
      <span class="text-yellow-400 font-bold">~ {good} Good</span>
      <span class="text-red-400 font-bold">✗ {bad} Bad</span>
"""
    if error > 0:
        summary_bar += f'      <span class="text-purple-400 font-bold">⚠ {error} Error</span>\n'
    summary_bar += "    </div>"
    
    badge_classes = {
        "excellent": "bg-green-900 text-green-300 border border-green-700",
        "good": "bg-yellow-900 text-yellow-300 border border-yellow-700",
        "bad": "bg-red-900 text-red-300 border border-red-700",
        "error": "bg-purple-900 text-purple-300 border border-purple-700",
    }
    
    cards = []
    for r in results:
        h = html.escape(r.get("hash", ""))
        author = html.escape(r.get("author", ""))
        timestamp = html.escape(r.get("timestamp", ""))
        rating = html.escape(r.get("rating", "error")).lower()
        message = html.escape(r.get("message", ""))
        reason = html.escape(r.get("reason", ""))
        
        badge_class = badge_classes.get(rating, badge_classes["error"])
        
        card = f"""
    <div class="mb-4 p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-600 transition-colors">
      <div class="flex items-center gap-3 mb-2 text-sm text-gray-400">
        <span class="font-bold text-gray-300">[{h}]</span>
        <span>{author}</span>
        <span>·</span>
        <span>{timestamp}</span>
        <span class="ml-auto px-3 py-0.5 rounded-full text-xs font-bold {badge_class}">
          {rating.upper()}
        </span>
      </div>
      <p class="text-white mb-2 text-sm leading-relaxed">"{message}"</p>
      <p class="text-gray-400 text-sm">→ {reason}</p>
    </div>
"""
        cards.append(card)
        
    cards_html = "".join(cards)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Commit Review Report</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen p-8 font-mono">
  <div class="max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold mb-1">Commit Review Report</h1>
    <p class="text-gray-400 text-sm mb-6">{generated_at} · {total} commits reviewed</p>
{summary_bar}
{cards_html}
  </div>
</body>
</html>
"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return os.path.abspath(output_path)
