import os
import re
from urllib.parse import urlparse
import requests
from flask import Flask, request

app = Flask(__name__)

# Read the blocklist file name from the environment variable
blocklist_file_name = os.environ.get('BLOCKLIST_FILE_NAME', 'custom-blocklist.txt')

# Define the full path to the blocklist file within the /data directory
blocklist_file = f'/data/{blocklist_file_name}'

# Define a list of domains to exclude (e.g., Google)
excluded_domains = ['google.com']

# Read the Telegram bot token and user chat ID from environment variables
telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', 'your_telegram_bot_token')
authorized_user_chat_id = os.environ.get('AUTHORIZED_USER_CHAT_ID', 'your_authorized_user_chat_id')

@app.route('/addblockdomain', methods=['POST'])
def add_block_domain():
    # Get the domain(s) from the request JSON
    data = request.get_json()

    # Extract the text from the message
    message_text = data.get('message', {}).get('text', '')

    # Extract the user's chat ID
    user_chat_id = data.get('message', {}).get('chat', {}).get('id')

    # Check if the message is from the authorized user
    if user_chat_id != authorized_user_chat_id:
        send_telegram_message(user_chat_id, 'You are not authorized.')
    else:
        # Extract URLs from the text using a regular expression
        urls = re.findall(r'https?://\S+', message_text)

        if not urls:
            send_telegram_message(authorized_user_chat_id, 'No URLs found in the message.')
        else:
            try:
                # Extract and append domains from the found URLs, excluding specified domains
                extracted_domains = []
                for url in urls:
                    domain = extract_domain_from_url(url)
                    if domain and domain not in excluded_domains:
                        extracted_domains.append(domain)

                if not extracted_domains:
                    send_telegram_message(authorized_user_chat_id, 'No valid domains found in the URLs.')
                else:
                    # Append the extracted domains to the blocklist file
                    with open(blocklist_file, 'a') as f:
                        for domain in extracted_domains:
                            f.write(domain + '\n')

                    send_telegram_message(authorized_user_chat_id, f'Domains added to the blocklist file: {", ".join(extracted_domains)}')
            except Exception as e:
                send_telegram_message(authorized_user_chat_id, str(e))

    return 'OK', 200  # Return success (200) to acknowledge receipt

def extract_domain_from_url(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc:
        return parsed_url.netloc
    else:
        return None

def send_telegram_message(chat_id, text):
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, data=data)

if __name__ == '__main__':
    app.run(debug=True)
