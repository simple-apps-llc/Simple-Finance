#!/usr/bin/env python3
"""
Generate privacy-policy.html from the in-app source of truth
(Finance/PrivacyPolicyView.swift). Keeps the hosted GitHub Pages privacy
policy in sync with what ships in the app.

Usage:  python3 generate_privacy_html.py
Output: ./privacy-policy.html  (upload to simple-apps-llc/Simple-Finance)
"""
import re, html, pathlib

SRC = pathlib.Path("Finance/PrivacyPolicyView.swift")
OUT = pathlib.Path("privacy-policy.html")

text = SRC.read_text(encoding="utf-8")

eff = re.search(r'effectiveDate\s*=\s*"([^"]+)"', text)
effective_date = eff.group(1) if eff else ""

# Grab each PolicySection(icon:..., title:"...", body:""" ... """)
sections = re.findall(
    r'PolicySection\(\s*icon:\s*"[^"]*",\s*title:\s*"([^"]*)",\s*body:\s*"""(.*?)"""',
    text, re.DOTALL)

def esc(s): return html.escape(s, quote=False)

def body_to_html(body: str) -> str:
    out, para, items = [], [], []
    def flush_para():
        if para:
            out.append("<p>" + esc(" ".join(para)) + "</p>"); para.clear()
    def flush_list():
        if items:
            out.append("<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>")
            items.clear()
    for raw in body.split("\n"):
        line = raw.rstrip()
        if line.startswith("• "):          # bullet
            flush_para(); items.append(line[2:].strip())
        elif line.strip() == "":                # blank -> paragraph break
            flush_para(); flush_list()
        else:
            flush_list(); para.append(line.strip())
    flush_para(); flush_list()
    return "\n        ".join(out)

cards = []
for title, body in sections:
    cards.append(f'''    <div class="card">
      <h2>{esc(title)}</h2>
        {body_to_html(body)}
    </div>''')
cards_html = "\n".join(cards)

doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Simple Finance — Privacy Policy</title>
<meta name="description" content="Simple Finance is built local-first: your financial data stays on your device and, if you choose, in your own iCloud. Read our full privacy policy.">
<style>
  :root {{ --accent:#00C896; --accent2:#00A878; --ink:#1c1c1e; --muted:#6b7280; --bg:#f2f2f7; --card:#ffffff; }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
         color:var(--ink); background:var(--bg); line-height:1.55; }}
  .header {{ background:linear-gradient(135deg,var(--accent),var(--accent2)); color:#fff; padding:48px 24px; }}
  .header .wrap {{ max-width:820px; margin:0 auto; }}
  .badge {{ display:inline-flex; align-items:center; justify-content:center; width:56px; height:56px;
           border-radius:50%; background:rgba(255,255,255,.2); font-size:26px; margin-bottom:14px; }}
  .header .kicker {{ font-size:13px; font-weight:600; opacity:.85; margin:0; letter-spacing:.02em; }}
  .header h1 {{ font-size:32px; font-weight:800; margin:2px 0 12px; }}
  .header p {{ font-size:15px; opacity:.94; margin:0; max-width:62ch; }}
  main {{ max-width:820px; margin:0 auto; padding:24px 16px 60px; }}
  .eff {{ color:var(--muted); font-size:14px; margin:4px 4px 16px; }}
  .card {{ background:var(--card); border-radius:14px; padding:20px 22px; margin:0 0 16px;
          box-shadow:0 1px 3px rgba(0,0,0,.06); }}
  .card h2 {{ font-size:19px; font-weight:800; margin:0 0 10px; }}
  .card p {{ margin:0 0 10px; }}
  .card ul {{ margin:0 0 10px; padding-left:22px; }}
  .card li {{ margin:5px 0; }}
  .card :last-child {{ margin-bottom:0; }}
  .footer {{ text-align:center; color:var(--muted); font-size:13px; padding:10px 0 0; }}
  a {{ color:var(--accent2); }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --ink:#f2f2f7; --muted:#9aa0aa; --bg:#000; --card:#1c1c1e; }}
  }}
</style>
</head>
<body>
  <div class="header">
    <div class="wrap">
      <div class="badge">\U0001f91a</div>
      <p class="kicker">SIMPLE FINANCE</p>
      <h1>Privacy Policy</h1>
      <p>Your financial data is yours. Simple Finance is built local-first — most data never leaves your device.</p>
    </div>
  </div>
  <main>
    <p class="eff">Effective Date: {esc(effective_date)}</p>
{cards_html}
    <p class="footer">Simple Finance · <a href="./support.html">Support</a> · <a href="mailto:simpleapphelp@outlook.com">simpleapphelp@outlook.com</a></p>
  </main>
</body>
</html>
'''

OUT.write_text(doc, encoding="utf-8")
print(f"Wrote {OUT} ({len(doc)} bytes) from {len(sections)} sections, effective {effective_date}")
