with open("nexo-guia.html") as f:
    body = f.read()

logo_color_b64 = open("logo_color_b64.txt").read().strip()
logo_color_uri = f"data:image/png;base64,{logo_color_b64}"

lines = body.split("\n", 1)
title_line = lines[0]
rest = lines[1]

# insert the logo once, right above the existing hero eyebrow — no other change
rest = rest.replace(
    '<div class="hero">\n  <span class="eyebrow">',
    f'<div class="hero">\n  <img src="{logo_color_uri}" style="height:34px;display:block;margin-bottom:22px;">\n  <span class="eyebrow">',
    1,
)

layout_css = """
<style>
  body{ display:flex; flex-direction:column; align-items:center; }
  .hero{ width:480px; box-sizing:border-box; padding:50px 26px 34px; }
  .screen-block{ width:480px; box-sizing:border-box; padding:40px 26px; border-bottom:1px solid var(--line); }
  main{ padding:0; max-width:none; width:auto; }
  .railnav{ display:none; }
  .footer-note{ width:480px; box-sizing:border-box; padding:22px 26px 50px; }
</style>
"""

html = (
    "<!DOCTYPE html>\n<html lang=\"es\"><head><meta charset=\"UTF-8\">\n"
    + title_line + "\n</head><body>\n"
    + rest
    + layout_css
    + "\n</body></html>"
)

with open("shots.html", "w") as f:
    f.write(html)

print("written", len(html))
