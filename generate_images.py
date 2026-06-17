import asyncio
import os
from github_stats import Stats
import aiohttp

async def main():
    access_token = os.getenv("ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
    user = os.getenv("GITHUB_ACTOR", "ad1tyq")
    
    if not access_token:
        print("No access token provided, skipping generation.")
        return

    async with aiohttp.ClientSession() as session:
        s = Stats(user, access_token, session)
        langs = await s.languages
        sorted_langs = sorted(langs.items(), key=lambda x: x[1].get('prop', 0), reverse=True)
        
        # Generate languages.svg
        try:
            with open("templates/languages.svg", "r") as f:
                template = f.read()
        except FileNotFoundError:
            template = ""
            
        progress = ""
        lang_list = ""
        for name, data in sorted_langs[:10]:
            color = data.get("color") or "#ccc"
            prop = data.get("prop", 0)
            progress += f'<span class="progress-item" style="background-color: {color}; width: {prop}%;" />\n'
            lang_list += f'<li><svg class="octicon" style="fill: {color};" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8z"></path></svg><span class="lang">{name}</span><span class="percent">{prop:.1f}%</span></li>\n'
            
        if template:
            result = template.replace("{{ progress }}", progress).replace("{{ lang_list }}", lang_list)
            with open("languages.svg", "w") as f:
                f.write(result)
                
        # Generate overview.svg
        try:
            with open("templates/overview.svg", "r") as f:
                overview_template = f.read()
        except FileNotFoundError:
            overview_template = None
            
        if overview_template:
            result = overview_template.replace("{{ stargazers }}", str(await s.stargazers))
            result = result.replace("{{ forks }}", str(await s.forks))
            result = result.replace("{{ contributions }}", str(await s.total_contributions))
            with open("overview.svg", "w") as f:
                f.write(result)

if __name__ == "__main__":
    asyncio.run(main())