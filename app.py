from flask import Flask, request, render_template
import instaloader
import asyncio
import aiohttp
from aiohttp import ClientSession
from functools import partial
from pathlib import Path

app = Flask(__name__)
L = instaloader.Instaloader()

# Define function to download reel
async def download_reel(session, reel_url):
    try:
        post = instaloader.Post.from_shortcode(L.context, reel_url.split("/")[-2])
        L.download_post(post, target=str(Path(post.owner_username)))

        # Delete all files except .mp4 in the post.owner_username directory
        for file in Path(post.owner_username).glob('*'):
            if not file.name.endswith('.mp4'):
                file.unlink()

        return True
    except Exception as e:
        print(f"Error downloading reel: {e}")
        return False

async def download_reels(reel_urls):
    tasks = []
    async with ClientSession() as session:
        for reel_url in reel_urls:
            task = asyncio.ensure_future(download_reel(session, reel_url))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        reel_urls = request.form['urls'].split('\n')
        results = asyncio.run(download_reels(reel_urls))
        if all(results):
            return render_template('success.html')
        else:
            return render_template('error.html')
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run()
