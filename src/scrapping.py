from telethon import TelegramClient
from dotenv import load_dotenv
from telethon.errors import FloodWaitError, SessionExpiredError
import asyncio
# import nest_asyncio
import os
import sys
import logging
import json
import csv

# logging set up
logging.basicConfig(
    filename='../logs/scrapping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# load enivornment
load_dotenv()
api_id = os.getenv('TG_API_ID')
api_hash = os.getenv('TG_API_HASH')
phone = os.getenv('phone')


# load channels
def load_channels(path):
    try:
        with open(path, 'r') as file:
            data = json.load(file)
            return data.get('channels', []), data.get('comments', []) 
        
    except Exception as e:
        logging.error(f"Error reading channels from json: {e}")
        return [], []

# get channels last id(the place scrapping stopped)
def get_last_processed_id(channel_username):
    try:
        with open(f'{channel_username}_last_id.json', 'r') as file:
            return json.load(file).get('last_id', 0)
        
    except FileNotFoundError:
        logging.warning(f'No last ID file found for {channel_username}. Starting from 0')
        return 0
    
# save the last process id
def save_last_processed_id(channel_username, last_id):
    with open(f'{channel_username}_last_id.json', 'w') as file:
        json.dump({'last_id': last_id}, file)
        logging.info(f"Saved last processed ID {last_id} for {channel_username}.")



# collect the data
async def scrape_channel(client, channel_username, writer, media_dir,num_messages_to_scrape):
    try:
        entity = await client.get_entity(channel_username)
        channel_tittle = entity.title      # channel tittle

        last_id = get_last_processed_id(channel_username)
        message_count = 0

        async for message in client.iter_messages(entity, limit = 500):
            if message_count >= num_messages_to_scrape:
                break

            media_path = None
            if message.media:
                filename = f"{channel_username}_{message.id}.{message.media.document.mime_type.split('/')[-1]}" if hasattr(message.media, 'document') else f"{channel_username}_{message.id}.jpg"
                media_path = os.path.join(media_dir, filename)

                await client.download_media(message.media, media_path)
                logging.info(f"Downloaded media for message ID {message.id}.")

            writer.writerow([channel_tittle, channel_username, message.id, message.message, message.date, media_path])
            logging.info(f"Processed message ID {message.id} from {channel_username}.")

            last_id = message.id
            message_count += 1

        # save the id in their specified channel file
        save_last_processed_id(channel_username, last_id)

        if message_count == 0:
                logging.info(f"No messages found for {channel_username}.")

    except Exception as e:
        logging.error(f"Error while scraping {channel_username}: {e}")


async def main():
    try:
        async with TelegramClient('scrapping_session', api_id, api_hash) as client:
            await client.start(phone=phone)
            logging.info('Client started successfully')

            # directory for photo files
            media_dir = 'photos'
            os.makedirs(media_dir,exist_ok=True)

            # load channels
            channels, comments = load_channels('../src/channels.json')

            num_messages_to_scrape = 50 # number of messages to scrape
            
            for channel in channels: 
                filename = f'{channel[13:]}_data.csv'
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Channel Title', 'Channel Username', 'ID', 'Message', 'Date', 'Media Path'])  # header

                    await scrape_channel(client, channel[13:], writer, media_dir, num_messages_to_scrape)
                    logging.info(f"Scraped data from {channel}.")

            # Log commented channels
            if comments:
                logging.info(f"Commented channels: {', '.join(comments)}")

        
    except FloodWaitError as e:
        logging.error(f"FloodWaitError: Please wait for {e.seconds} seconds before retrying.")

    except SessionExpiredError as e:
        logging.error(f"SessionExpiredError: Session has expired. You may need to reauthenticate.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


