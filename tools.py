from playwright.async_api import async_playwright
import asyncio
import re
import urllib.parse
from agents import function_tool

@function_tool
async def scrape_yp_listing(url: str):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Change to True later
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        await page.wait_for_selector(".listing", timeout=30000)

        listings = await page.query_selector_all(".listing")
        for idx, listing in enumerate(listings, 1):
            # --- Business Name ---
            name_el = await listing.query_selector(".listing__name--link")
            name = (
                await listing.eval_on_selector(".listing__name--link", "el => el.innerText")
                if name_el else "Not found"
            )

            # --- Click and Extract Phone Number ---
            phone = "Not found"
            try:
                phone_btn = await listing.query_selector(".mlr__item--phone a")
                if phone_btn:
                    await phone_btn.click()
                    await page.wait_for_timeout(1000)

                    phone_el = await listing.query_selector(".mlr__submenu h4")
                    if phone_el:
                        phone_text = await phone_el.inner_text()
                        phone = phone_text.strip()
                    else:
                        # Fallback regex search
                        text = await listing.inner_text()
                        match = re.search(r"\(?\d{3}\)?[ -.]?\d{3}[ -.]?\d{4}", text)
                        if match:
                            phone = match.group(0)
            except Exception as e:
                print(f"[{idx}] Phone error for {name}: {e}")

            # --- Website ---
            website = "Not found"
            try:
                website_el = await listing.query_selector('a:has-text("Website")')
                if website_el:
                    raw_href = await website_el.get_attribute("href")
                    if raw_href and "redirect=" in raw_href:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_href).query)
                        website = parsed.get("redirect", ["Not found"])[0]
                    elif raw_href:
                        website = raw_href
            except:
                pass

            results.append({
                "name": name.strip(),
                "phone": phone.strip(),
                "website": website.strip(),
            })
            print(f"[{idx}] {name}: {phone} | {website}")

        await browser.close()
    return results


if __name__ == "__main__":
    async def main():
        url = "https://www.yellowpages.ca/search/si/1/plumber/Toronto,+ON"
        data = await scrape_yp_listing(url)
        print("\nFINAL RESULTS:\n", data)

    asyncio.run(main())
