with open("nexo-guia.html") as f:
    body = f.read()

lines = body.split("\n", 1)
title_line = lines[0]
rest = lines[1]

layout_css = """
<style>
  body{ display:flex; flex-direction:column; align-items:center; }
  .hero{ width:480px; height:679px; box-sizing:border-box; display:flex; flex-direction:column; justify-content:center; padding:24px 24px; }
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
