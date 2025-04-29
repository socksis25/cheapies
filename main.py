
import os
import json
import asyncio
import requests
from bs4 import BeautifulSoup
from discord import Embed, Client, Intents
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Discord client
intents = Intents.default()
client = Client(intents=intents)

# Channel ID to send deals to
CHANNEL_ID = 1366636217873076225

# Store seen posts
SEEN_POSTS_FILE = 'seen_posts.json'

def load_seen_posts():
    try:
        with open(SEEN_POSTS_FILE, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_seen_posts(seen_posts):
    with open(SEEN_POSTS_FILE, 'w') as f:
        json.dump(list(seen_posts), f)

async def check_cheapies():
    seen_posts = load_seen_posts()
    
    while True:
        try:
            # Fetch and parse the page
            response = requests.get('https://www.cheapies.nz/deals')
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all deal posts
            posts = soup.find_all('div', class_='node-deal')
            
            for post in posts:
                # Extract post details
                title_elem = post.find('h2', class_='title')
                if not title_elem:
                    continue
                    
                link = 'https://www.cheapies.nz' + title_elem.find('a')['href']
                
                # Skip if already seen
                if link in seen_posts:
                    continue
                
                title = title_elem.text.strip()
                description = post.find('div', class_='content').text.strip()[:200] + '...'
                author = post.find('span', class_='username').text.strip()
                
                # Create and send embed
                channel = client.get_channel(CHANNEL_ID)
                embed = Embed(title=title, url=link, description=description)
                embed.set_footer(text=f"Posted by {author}")
                
                await channel.send(embed=embed)
                
                # Mark as seen
                seen_posts.add(link)
                save_seen_posts(seen_posts)
                
        except Exception as e:
            print(f"Error: {e}")
            
        # Wait 5 minutes before checking again
        await asyncio.sleep(300)

@client.event
async def on_ready():
    print(f'Bot is ready as {client.user}')
    client.loop.create_task(check_cheapies())

# Start the bot
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        raise ValueError("Please set DISCORD_TOKEN in environment variables")
    client.run(TOKEN)
