# Web Link Collector 1000

## About
Easily and automatically collect all your links into a neat txt list from a particular website or an entire section of a multi-page website network!

Web Link Collector 1000 is a simple tool for gathering links from websites with minimal effort. It helps you collect resources for research, create reference lists, or save useful links without manual copying and pasting.

Works on Windows 7 and above.

## Features
- **Two Collection Modes**: Single page or multiple pages of specific website section, or even the entire domain!
- **Smart Filtering**: Include only same-domain links or gather external links too
- **Duplicate Prevention**: Automatically removes duplicate links
- **Website-Friendly**: Uses respectful delays between requests
- **Custom File Naming**: Save your collections with custom meaningful names
- **Modern Interface**: Clean design with status updates
- **Link Normalization**: Standardizes URLs for proper formatting

## How to Use

First, run the 'Web Link Collector 1000.exe'

1. **Name Your Collection**
   - Enter a name for your link list file.
   - Avoid special characters that filenames can't have like <>:"/|?*
   - The ".txt" extension is added automatically.

2. **Choose Your Scraping Mode**
   - **Single Page**: Collects links from one specific webpage only.
   - **Section Crawl**: Follows links within a specific section of a website, collecting links across multiple pages or even the whole domain. Use with caution!

3. **Set Your Filter Preference**
   - Check "Only save links that belong to the same domain" to exclude external links.
   - Uncheck to collect all links, including those to other websites.

4. **Enter the URL**
   - For Single Page mode: Enter the complete URL of the webpage.
   - For Section Crawl mode: Enter the URL of the specific section you want to crawl.

5. **Start Collection**
   - Click "Collect Links" to begin.
   - Progress updates appear as links are discovered.
   - When complete, your link list is saved as a text file into the folder where the exe is.

6. **Managing Collection**
   - Use "Stop" to interrupt the process.
   - The filename field clears after each successful collection.
   
You'll find your completed .txt files in the same folder as the 'Web Link Collector 1000.exe' itself.

### Important Notes on Section Crawl Mode

The Section Crawl mode will only follow links that stay within the initial path you specify. For example:

- If you enter `https://example.com/products/electronics/`.
- The tool will only crawl pages under `/products/electronics/`.
- It will NOT crawl other sections like `/products/` or `/about/`.

If you just enter `https://example.com/, it will crawl the ENTIRE DOMAIN, going on EVERY PAGE and getting EVERY LINK EVER. This can be a BAD IDEA unless you know what you're doing.

The targeted approach helps you focus on specific website sections without collecting links from the entire domain.

Please use Section Crawl responsibly:
- Some websites may have restrictions and automatic defences against automated crawling.
- For large websites, crawling may take considerable time.
- DO NOT use is on something as too broad as 'https://github.com/' or 'https://www.deviantart.com'. You will end up with millions of unnecessary links, take forever and get IP banned in the worst case.
- instead, DO use it on something more focused like 'https://github.com/ReactorcoreGames' or 'https://www.deviantart.com/reactorcore3/art/'. Keep it local, keep it limited to smaller areas of a website.

## Tips for Best Results
- Start with specific section URLs rather than homepages for more targeted results.
- Use descriptive filenames that include the website and date.
- Review collected links after scraping.
- For very large websites, consider using Single Page mode on key pages.

Web Link Collector 1000 is designed for legitimate link collection while respecting website resources.

## Support My Work:

If you enjoyed this release, please buy me an orange to fuel me: 

https://buymeacoffee.com/reactorcoregames

Or join my Patreon for games, assets, design knowledge and tool recommendations: 

https://www.patreon.com/ReactorcoreGames

Check my Itch io page and Follow me there to know when I release cool new stuff! 

https://reactorcore.itch.io/

All my links - I make games, software, assets, lego mechs, AI art and more:

https://linktr.ee/reactorcore

I'm a Prompt Engineer, hire me for work:

mailto:reactorcoregames@gmail.com