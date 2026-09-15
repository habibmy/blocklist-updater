import os
import re
from urllib.parse import urlparse
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='public')

blocklist_file_name = os.environ.get('BLOCKLIST_FILE_NAME', 'custom-blocklist.txt')
data_dir = '/data' if os.path.exists('/data') else '.'
blocklist_file = os.path.join(data_dir, blocklist_file_name)

excluded_domains = ['google.com', 'www.google.com']

telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
raw_chat_id = os.environ.get('AUTHORIZED_USER_CHAT_ID', '0')
try:
    authorized_user_chat_id = int(raw_chat_id)
except ValueError:
    authorized_user_chat_id = 0

def extract_domain_from_url(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc or parsed_url.path
    if netloc:
        return netloc.split(':')[0].strip().lower()
    return None

def append_domains_to_blocklist(domains):
    os.makedirs(os.path.dirname(os.path.abspath(blocklist_file)), exist_ok=True)
    existing = set()
    if os.path.exists(blocklist_file):
        with open(blocklist_file, 'r', encoding='utf-8') as f:
            existing = {line.strip().lower() for line in f if line.strip()}

    added = []
    with open(blocklist_file, 'a', encoding='utf-8') as f:
        for d in domains:
            if d and d not in excluded_domains and d not in existing:
                f.write(d + '\n')
                existing.add(d)
                added.append(d)
    return added

# -------------------------------------------------------------------
# Static Files & PWA Routes (all kept under /addblockdomain)
# -------------------------------------------------------------------

@app.route('/addblockdomain', methods=['GET'])
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/addblockdomain/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/addblockdomain/api', methods=['POST'])
def add_block_api():
    data = request.get_json(silent=True) or {}
    domain = data.get('domain', '').strip().lower()

    if not domain or '.' not in domain or domain in excluded_domains:
        return jsonify({'status': 'error', 'message': f'Invalid domain: {domain}'}), 400

    added = append_domains_to_blocklist([domain])

    if telegram_bot_token and authorized_user_chat_id:
        msg = f"Web added: {domain}" if added else f"Web shared: {domain} (already in list)"
        send_telegram_message(authorized_user_chat_id, msg)

    if not added:
        return jsonify({'status': 'exists', 'domain': domain})

    return jsonify({'status': 'success', 'domain': domain})

# -------------------------------------------------------------------
# Telegram Webhook Handler (Existing)
# -------------------------------------------------------------------

@app.route('/addblockdomain', methods=['POST'])
def add_block_telegram():
    data = request.get_json(silent=True) or {}
    message_text = data.get('message', {}).get('text', '')
    user_chat_id = data.get('message', {}).get('chat', {}).get('id')

    try:
        user_chat_id = int(user_chat_id)
    except (ValueError, TypeError):
        return 'Invalid chat ID.', 200

    if user_chat_id != authorized_user_chat_id:
        send_telegram_message(user_chat_id, 'You are not authorized.')
        return 'OK', 200

    urls = re.findall(r'https?://\S+', message_text)
    if not urls:
        send_telegram_message(user_chat_id, 'No URLs found.')
        return 'OK', 200

    extracted = [extract_domain_from_url(u) for u in urls]
    valid_domains = [d for d in extracted if d]

    try:
        added = append_domains_to_blocklist(valid_domains)
        if added:
            send_telegram_message(user_chat_id, f'Added: {", ".join(added)}')
        else:
            send_telegram_message(user_chat_id, 'Already blocked or excluded.')
    except Exception as e:
        send_telegram_message(user_chat_id, f'Error: {str(e)}')

    return 'OK', 200

def send_telegram_message(chat_id, text):
    try:
        url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
        requests.post(url, data={'chat_id': chat_id, 'text': text}, timeout=5)
    except Exception as e:
        print(f"Telegram alert failed: {e}")

if __name__ == '__main__':
    app.run(debug=True)