import os
import re
from urllib.parse import urlparse
import requests
from flask import Flask, request, render_template_string, Response

app = Flask(__name__)

# Read the blocklist file name from the environment variable
data_dir = '/data' if os.path.exists('/data') else '.'
blocklist_file_name = os.environ.get('BLOCKLIST_FILE_NAME', 'custom-blocklist.txt')

# Define the full path to the blocklist file within the /data directory
blocklist_file = f'/data/{blocklist_file_name}'

# Define a list of domains to exclude (e.g., Google)
excluded_domains = ['google.com']

# Read the Telegram bot token and user chat ID from environment variables
telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', 'your_telegram_bot_token')
authorized_user_chat_id = int(os.environ.get('AUTHORIZED_USER_CHAT_ID', 'your_authorized_user_chat_id'))

@app.route('/addblockdomain', methods=['POST'])
def add_block_domain():
    # Get the domain(s) from the request JSON
    data = request.get_json()

    # Extract the text from the message
    message_text = data.get('message', {}).get('text', '')

    # Extract the user's chat ID
    user_chat_id = data.get('message', {}).get('chat', {}).get('id')
    
    # authorized_user_chat_id=int(authorized_user_chat_id)

    try:
        user_chat_id = int(user_chat_id)
    except ValueError:
        print("Chat ID : " + user_chat_id)
        return 'Invalid user chat ID.', 200  # Return success (200) to acknowledge receipt


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

@app.route('/addblockdomain', methods=['GET'])
def test_block_page():
    # Android share sheet might place the URL inside 'url' or 'text'
    raw_input = request.args.get('url') or request.args.get('text') or ''
    status_msg = ""
    domain = None

    if raw_input:
        match = re.search(r'https?://\S+', raw_input)
        target = match.group(0) if match else raw_input
        domain = extract_domain_from_url(target)

        if domain and domain not in excluded_domains:
            try:
                with open(blocklist_file, 'a') as f:
                    f.write(domain + '\n')
                status_msg = f"Added: {domain}"
                if telegram_bot_token and authorized_user_chat_id:
                    send_telegram_message(authorized_user_chat_id, f"Added via Web: {domain}")
            except Exception as e:
                status_msg = f"Error: {str(e)}"
        else:
            status_msg = f"Skipped: {domain or 'Invalid'}"

    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Block Site</title>
      <link rel="manifest" href="/addblockdomain/manifest.webmanifest">
      <style>
        body { font-family: sans-serif; background: #181818; color: #fff; padding: 24px; text-align: center; }
        input[type="text"] { width: 90%; max-width: 400px; padding: 10px; margin: 12px 0; border-radius: 6px; border: 1px solid #444; }
        button { padding: 10px 20px; border-radius: 6px; border: none; background: #e53935; color: white; font-weight: bold; cursor: pointer; }
        .status { margin-top: 20px; font-weight: bold; color: #4caf50; font-size: 1.2rem; }
      </style>
    </head>
    <body>
      <h2>Block Site</h2>
      <form method="GET" action="/addblockdomain">
        <input type="text" name="url" placeholder="https://example.com" value="{{ url }}" required>
        <br>
        <button type="submit">Block Domain</button>
      </form>
      {% if status %}
        <p class="status">{{ status }}</p>
      {% endif %}

      <script>
        if ('serviceWorker' in navigator) {
          navigator.serviceWorker.register('/addblockdomain/sw.js', { scope: '/addblockdomain' });
        }
        // Auto-close if shared from Android
        const params = new URLSearchParams(window.location.search);
        if (params.has('url') || params.has('text')) {
          setTimeout(() => window.close(), 1500);
        }
      </script>
    </body>
    </html>
    """
    return render_template_string(html, url=raw_input, status=status_msg)

@app.route('/addblockdomain/manifest.webmanifest')
def share_manifest():
    manifest_data = """{
      "name": "Blocklist",
      "short_name": "Block Site",
      "start_url": "/addblockdomain",
      "scope": "/addblockdomain",
      "display": "standalone",
      "background_color": "#181818",
      "theme_color": "#181818",
      "icons": [
        {
          "src": "https://cdn-icons-png.flaticon.com/512/564/564619.png",
          "sizes": "512x512",
          "type": "image/png"
        }
      ],
      "share_target": {
        "action": "/addblockdomain",
        "method": "GET",
        "params": {
          "title": "title",
          "text": "text",
          "url": "url"
        }
      }
    }"""
    return Response(manifest_data, mimetype='application/manifest+json')

@app.route('/addblockdomain/sw.js')
def service_worker():
    sw_data = """
    self.addEventListener('install', e => self.skipWaiting());
    self.addEventListener('activate', e => clients.claim());
    self.addEventListener('fetch', e => e.respondWith(fetch(e.request)));
    """
    return Response(sw_data, mimetype='application/javascript')

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
