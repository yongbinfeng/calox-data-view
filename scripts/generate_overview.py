import os
from collections import defaultdict

# Settings
REPO_NAME = "calox-live-dqm"
ROOT_DIR = "results/html"
OUTPUT_FILE = "docs/overview.html"

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# Group HTML entries by RunXXX
grouped_entries = defaultdict(list)
for root, _, files in os.walk(ROOT_DIR):
    for file in sorted(files):
        if file.endswith(".html"):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, ".")
            run_path = rel_path.replace("results/html/", "")
            web_path = f"/{REPO_NAME}/{rel_path}"
            run_name = run_path.split("/")[0]
            grouped_entries[run_name].append((web_path, run_path))

# Generate HTML
html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CaloX DQM Overview</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background: #f2f5f9;
      margin: 0;
      padding: 30px;
    }

    h1 {
      color: #222;
      margin-bottom: 20px;
    }

    .controls {
      margin-bottom: 20px;
    }

    button {
      background-color: #007acc;
      border: none;
      color: white;
      padding: 8px 14px;
      margin-right: 10px;
      border-radius: 4px;
      font-size: 0.95em;
      cursor: pointer;
      transition: background-color 0.2s ease;
    }

    button:hover {
      background-color: #005a99;
    }

    details {
      background: #ffffff;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
      margin-bottom: 15px;
      padding: 16px;
      transition: all 0.3s ease;
    }

    summary {
      cursor: pointer;
      font-weight: 600;
      font-size: 1.1em;
      color: #333;
    }

    details[open] {
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    details details {
      margin-top: 10px;
      background: #f9fbfc;
      border-left: 4px solid #007acc;
      padding: 12px;
    }

    details details summary {
      font-size: 1em;
      color: #005b99;
    }

    ul {
      list-style: none;
      padding-left: 0;
      margin: 10px 0;
    }

    li {
      margin: 10px 0;
      background: #fff;
      padding: 10px;
      border: 1px solid #e0e0e0;
      border-radius: 6px;
      transition: background 0.2s;
    }

    li:hover {
      background: #f4faff;
    }

    a {
      text-decoration: none;
      color: #007acc;
      font-weight: 500;
    }

    a:hover {
      text-decoration: underline;
    }

    iframe {
      border: 1px solid #ccc;
      margin-top: 10px;
      width: 100%;
      height: 300px;
      border-radius: 4px;
    }

    summary::-webkit-details-marker {
      display: none;
    }
  </style>
  <script>
    function toggleAllDetails(open) {
      document.querySelectorAll("details").forEach(detail => {
        detail.open = open;
      });
    }

    document.addEventListener("DOMContentLoaded", function () {
      document.querySelectorAll("details.preview").forEach(detail => {
        detail.addEventListener("toggle", function () {
          if (detail.open && !detail.dataset.loaded) {
            const container = detail.querySelector(".iframe-container");
            const src = container.dataset.src;
            const iframe = document.createElement("iframe");
            iframe.src = src;
            iframe.loading = "lazy";
            container.appendChild(iframe);
            detail.dataset.loaded = "true";
          }
        });
      });
    });
  </script>
</head>
<body>
  <h1>CaloX Test Beam DQM Plots</h1>
  <div class="controls">
    <button onclick="toggleAllDetails(true)">Expand All</button>
    <button onclick="toggleAllDetails(false)">Collapse All</button>
  </div>
"""

# Build grouped structure
for run_name in sorted(grouped_entries.keys()):
    html += f'  <details>\n    <summary>{run_name}</summary>\n    <div>\n'

    category_map = defaultdict(list)
    prefix = f"{run_name}/"
    for web_path, run_path in grouped_entries[run_name]:
        inner_path = run_path[len(prefix):]
        category = inner_path.split(
            "/")[0] if "/" in inner_path else inner_path
        category_map[category].append((web_path, inner_path))

    for category in sorted(category_map.keys()):
        html += f'      <details>\n        <summary>{category}</summary>\n        <ul>\n'
        for web_path, inner_path in sorted(category_map[category], key=lambda tup: tup[1]):
            parts = inner_path.split("/")
            display_name = "/".join(parts[1:]) if len(parts) > 1 else parts[0]
            html += f'          <li>\n'
            html += f'            <a href="{web_path}" target="_blank">{display_name}</a>\n'
            html += f'            <details class="preview">\n'
            html += f'              <summary style="font-size: 0.9em; color: #444;">Preview</summary>\n'
            html += f'              <div class="iframe-container" data-src="{web_path}"></div>\n'
            html += f'            </details>\n'
            html += f'          </li>\n'
        html += f'        </ul>\n      </details>\n'
    html += f'    </div>\n  </details>\n'

html += """</body>
</html>
"""

# Write to output file
with open(OUTPUT_FILE, "w") as f:
    f.write(html)
    print(f"Overview generated at {OUTPUT_FILE}")
