# "Internship Scanner"
Originally, the intention was that the program would send me a message on Discord
when an internship application page changed. However, this quickly became a "Send me
a message whenever {url} content changes" application.

## Setup
Create `discord_hook.txt`. Paste a Discord webhook URL inside.
Set `TARGET_URL` at the top of `scrape.py` to the target URL to scan.
If needed, change the `soup.select_one` call in `scrape()` to filter content to a single element.
