from pathlib import Path
import re

UP_FILE = Path("index_up.html")
DOWN_FILE = Path("index_down.html")
OUT_FILE = Path("index.html")


def read_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return path.read_text(encoding="utf-8")


def get_tag_contents(html: str, tag: str):
    pattern = rf"<{tag}\b[^>]*>(.*?)</{tag}>"
    return re.findall(pattern, html, flags=re.IGNORECASE | re.DOTALL)


def get_links(html: str):
    return re.findall(r"<link\b[^>]*>", html, flags=re.IGNORECASE | re.DOTALL)


def get_body_inner(html: str) -> str:
    match = re.search(r"<body\b[^>]*>(.*?)</body>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError("Could not find <body>...</body>")

    body = match.group(1)

    # Scripts are moved to the end of the merged page.
    body = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.IGNORECASE | re.DOTALL)

    return body.strip()


def unique_links(*html_files: str):
    seen = set()
    output = []

    for html in html_files:
        for link in get_links(html):
            href_match = re.search(r"href=[\"']([^\"']+)[\"']", link, flags=re.IGNORECASE)
            key = href_match.group(1) if href_match else link
            if key not in seen:
                seen.add(key)
                output.append(link)

    return output


def indent(text: str, spaces: int = 2) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())


def main() -> None:
    up_html = read_file(UP_FILE)
    down_html = read_file(DOWN_FILE)

    links = unique_links(up_html, down_html)
    up_styles = get_tag_contents(up_html, "style")
    down_styles = get_tag_contents(down_html, "style")
    up_scripts = get_tag_contents(up_html, "script")
    down_scripts = get_tag_contents(down_html, "script")

    up_body = get_body_inner(up_html)
    down_body = get_body_inner(down_html)

    merged = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>LLM Diversity Calibration</title>
  <meta name="description" content="LLMs lack diversity. We identify two root causes: order and shape miscalibration. These two bottlenecks limit the diversity of LLM outputs.">

  <!-- Open Graph / social sharing -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="Sampling More, Getting Less: Calibration is the Diversity Bottleneck in LLMs">
  <meta property="og:description" content="LLMs collapse to a narrow set of outputs even when many valid alternatives exist. We identify two distributional bottlenecks: order and shape calibration.">
  <meta property="og:url" content="https://diversitycalibration.github.io/">
  <meta property="og:image" content="figs/Open Graph.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Sampling More, Getting Less: Calibration is the Diversity Bottleneck in LLMs">
  <meta name="twitter:description" content="LLMs collapse to a narrow set of outputs even when many valid alternatives exist. We identify two distributional bottlenecks: order and shape calibration.">
  <meta name="twitter:image" content="figs/Open Graph.png">

{indent(chr(10).join(links), 2)}

  <style>
    body {{
      margin: 0;
      background: #fff;
    }}

    .merged-demo-divider {{
      width: min(1080px, calc(100% - 32px));
      margin: 24px auto 34px;
      border: 0;
      border-top: 1px solid #e2e6ff;
    }}
  </style>

  <!-- Styles from index_up.html -->
  <style>
{indent(chr(10).join(up_styles), 4)}
  </style>

  <!-- Styles from index_down.html -->
  <style>
{indent(chr(10).join(down_styles), 4)}
  </style>
</head>

<body>
  <!-- Upper visualization -->  
{indent(up_body, 2)}

  <hr class="merged-demo-divider">

  <!-- Lower visualization -->
{indent(down_body, 2)}

  <!-- Scripts from index_up.html -->
  <script>
{indent(chr(10).join(up_scripts), 4)}
  </script>

  <!-- Scripts from index_down.html -->
  <script>
{indent(chr(10).join(down_scripts), 4)}
  </script>
</body>
</html>
"""

    OUT_FILE.write_text(merged, encoding="utf-8")
    print(f"Created {OUT_FILE}")
    print("Keep these files in the same folder:")
    print("  index.html")
    print("  index_up.html")
    print("  index_down.html")
    print("  data_up.json")
    print("  data_down.json")


if __name__ == "__main__":
    main()
