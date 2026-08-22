import os
from playwright.sync_api import sync_playwright

IDS = ["login", "inicio", "sesiones", "informes", "bonos",
       "calendario", "profesor", "material", "tareas", "tests", "avisos"]

os.makedirs("shots", exist_ok=True)
for f in os.listdir("shots"):
    os.remove(os.path.join("shots", f))

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    page = browser.new_page(viewport={"width": 480, "height": 1000}, device_scale_factor=2)
    page.goto("file://" + os.path.abspath("shots.html"))
    page.wait_for_timeout(600)

    # hero (has no id, it's the first div.hero)
    page.locator("div.hero").screenshot(path="shots/00_hero.png")

    for i, sid in enumerate(IDS, start=1):
        el = page.locator(f"section#{sid}")
        el.screenshot(path=f"shots/{i:02d}_{sid}.png")

    browser.close()

print("done")
