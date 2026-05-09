import os
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

# Settings
REPO_NAME = "calox-data-view"
ROOT_DIR = "results/html"
OUTPUT_FILE = "docs/overview.html"

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# 1. Build a nested dictionary (tree)
def tree(): return defaultdict(tree)
fs_tree = tree()

for root, _, files in os.walk(ROOT_DIR):
    for file in sorted(files):
        if file.endswith(".html"):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, ROOT_DIR)
            parts = rel_path.split(os.sep)
            
            curr = fs_tree
            for part in parts:
                curr = curr[part]

# 2. Function to recursively generate HTML
def build_html_tree(node, current_rel_path_list, depth=0):
    html_output = ""
    items = sorted(node.items())
    
    folders = [(name, children) for name, children in items if isinstance(children, dict) and children]
    files = [(name, children) for name, children in items if not (isinstance(children, dict) and children)]
    
    for name, children in folders:
        depth_class = "depth-root" if depth == 0 else f"depth-{min(depth, 2)}"
            
        html_output += f'      <details class="folder-container {depth_class}">\n'
        html_output += f'        <summary>{name}</summary>\n'
        html_output += f'        <div class="folder-content">\n'
        html_output += build_html_tree(children, current_rel_path_list + [name], depth + 1)
        html_output += f'        </div>\n'
        html_output += f'      </details>\n'
    
    if files:
        html_output += '        <ul class="file-list">\n'
        for name, _ in files:
            file_rel_path = "/".join(current_rel_path_list + [name])
            web_path = f"/{REPO_NAME}/results/html/{file_rel_path}"
            html_output += f'          <li><a href="{web_path}" target="_blank">{name}</a></li>\n'
        html_output += '        </ul>\n'
            
    return html_output

# 3. Get timestamp in Geneva time
generation_time = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%B %d, %Y, %I:%M %p %Z")

# 4. HTML Template
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CaloX DQM Overview</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #f2f5f9;
      margin: 0;
      padding: 30px;
    }
    h1 { color: #222; margin-bottom: 10px; }
    
    .timestamp { 
      color: #666; 
      font-size: 0.9em; 
      margin-bottom: 20px; 
      font-style: italic;
    }

    .controls { margin-bottom: 25px; display: flex; gap: 10px; }
    
    .btn {
      border: none; color: white; padding: 8px 14px;
      border-radius: 4px; font-size: 0.95em; cursor: pointer;
      font-weight: 500; transition: background-color 0.2s ease;
    }
    .btn-expand { background-color: #28a745; }
    .btn-expand:hover { background-color: #218838; }
    .btn-collapse { background-color: #6c757d; }
    .btn-collapse:hover { background-color: #5a6268; }

    details {
      background: #ffffff; border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
      margin-bottom: 15px; padding: 16px;
      transition: all 0.3s ease; border: 1px solid transparent;
    }
    details[open] { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

    summary {
      cursor: pointer; font-weight: 600; font-size: 1.1em;
      color: #333; list-style: none; display: flex; align-items: center;
    }
    summary::-webkit-details-marker { display: none; }
    summary::before {
      content: '▶';
      display: inline-block;
      font-size: 0.7em;
      margin-right: 12px;
      color: inherit;
      transition: transform 0.2s ease;
      opacity: 0.8;
    }
    details[open] > summary::before { transform: rotate(90deg); opacity: 1; }

    .depth-root { border: 1px solid #e0e0e0; }
    .depth-1 { 
      background: #f9fbfc; border-left: 4px solid #007acc; 
      margin-top: 10px; padding: 12px;
    }
    .depth-1 > summary { color: #005b99; font-size: 1em; }
    .depth-2 { 
      background: #fcfcfc; border-left: 4px solid #adb5bd; 
      margin-top: 8px; padding: 10px;
    }
    .depth-2 > summary { color: #555; font-size: 0.95em; }

    ul { list-style: none; padding-left: 0; margin: 10px 0; }
    li {
      margin: 10px 0; background: #fff; padding: 10px;
      border: 1px solid #e0e0e0; border-radius: 6px; transition: background 0.2s;
    }
    li:hover { background: #f4faff; }
    a { text-decoration: none; color: #007acc; font-weight: 500; }
    a:hover { text-decoration: underline; }
  </style>
  <script>
    function toggleAllDetails(open) {
      document.querySelectorAll("details").forEach(detail => { detail.open = open; });
    }
  </script>
</head>
<body>
  <h1>CaloX Test Beam Analysis Plots</h1>
  
  <div class="controls">
    <button class="btn btn-expand" onclick="toggleAllDetails(true)">Expand All</button>
    <button class="btn btn-collapse" onclick="toggleAllDetails(false)">Collapse All</button>
  </div>

  <div class="timestamp">
    Last updated on: <strong>REPLACE_WITH_TIME</strong>
  </div>

  REPLACE_WITH_CONTENT
</body>
</html>
"""

# 5. Injection and File Write
content_html = build_html_tree(fs_tree, [])
final_output = html_template.replace("REPLACE_WITH_CONTENT", content_html)
final_output = final_output.replace("REPLACE_WITH_TIME", generation_time)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(final_output)
    print(f"Overview generated at {OUTPUT_FILE}")
