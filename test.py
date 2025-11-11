import asyncio
from tools import scrape_yp_listing

async def main():
    result = await scrape_yp_listing("https://www.yellowpages.ca/search/si/1/plumber/Toronto,+ON")
    print(result)

asyncio.run(main())
