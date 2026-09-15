# Blocklist Updater

Add domains to be blocked using Pi-hole via **Telegram Bot** or the **Android Web Share Target** interface.

---

## Features

- **Telegram Bot Integration**: Forward or share links directly to your bot.
- **Android Web Share Target (PWA)**: Add domains right from your Android device's native system Share Sheet without needing Telegram.
- **Automatic Deduplication**: Prevents duplicate domains from bloating your blocklist.
- **Exclusion Filters**: Ignores common system and search engine domains (e.g., Google).

---

## Project Structure

```text
blocklist-updater/
├── app.py
├── Dockerfile
├── requirements.txt
├── README.md
└── public/
    ├── index.html
    ├── style.css
    ├── app.js
    ├── sw.js
    └── manifest.webmanifest
```

---

## Getting Started

### Using Docker

1. **Pull or Build the Docker Image**:

   Pull from Docker Hub:

   ```bash
   docker pull habibmy/blocklist-updater:latest
   ```

   Or build locally:

   ```bash
   docker build -t blocklist-updater:latest .
   ```

2. **Run the Docker Container**:

   Run the container, specifying your environment variables and mounting a volume to `/data` to persist your blocklist file:

   ```bash
   docker run -d \
     --name blocklist-updater \
     -p 5000:5000 \
     -v /path/to/directory/containing/custom-blocklist-file:/data \
     -e BLOCKLIST_FILE_NAME=custom-blocklist.txt \
     -e TELEGRAM_BOT_TOKEN=your_telegram_bot_token \
     -e AUTHORIZED_USER_CHAT_ID=your_authorized_user_chat_id \
     blocklist-updater:latest
   ```

### Docker Compose Example

```yaml
services:
  blocklist-updater:
    image: blocklist-updater:latest
    container_name: blocklist-updater
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - /path/to/directory/containing/custom-blocklist-file:/data
    environment:
      - BLOCKLIST_FILE_NAME=custom-blocklist.txt
      - TELEGRAM_BOT_TOKEN=your_telegram_bot_token
      - AUTHORIZED_USER_CHAT_ID=your_authorized_user_chat_id
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.blocklist.rule=Host(`yourdomain.com`) && PathPrefix(`/addblockdomain`)"
      - "traefik.http.services.blocklist.loadbalancer.server.port=5000"
```

---

## Environment Variables

| Variable                  | Description                                      | Default                        |
| :------------------------ | :----------------------------------------------- | :----------------------------- |
| `BLOCKLIST_FILE_NAME`     | The name of the blocklist file stored in `/data` | `custom-blocklist.txt`         |
| `TELEGRAM_BOT_TOKEN`      | Your Telegram bot token from @BotFather          | `your_telegram_bot_token`      |
| `AUTHORIZED_USER_CHAT_ID` | Your Telegram user's numeric chat ID             | `your_authorized_user_chat_id` |

---

## Usage

### Option 1: Android Share Sheet (PWA)

1. Open `https://<your-domain>/addblockdomain` in Chrome on your Android tablet or phone.
2. Tap the three dots $\rightarrow$ **Install app** (or **Add to Home screen**).
3. Whenever you are browsing, tap **Share** in Chrome or any other app and select **Block Site**.
4. The domain is automatically extracted, deduplicated, appended to your blocklist file, and sent as a notification to your Telegram chat.

### Option 2: Telegram Bot

1. Set your Telegram webhook to point to your endpoint:
   ```bash
   curl -F "url=https://<your-domain>/addblockdomain" [https://api.telegram.org/bot](https://api.telegram.org/bot)<TELEGRAM_BOT_TOKEN>/setWebhook
   ```
2. Send or share any link containing a domain directly to your Telegram bot.

---

### Commit the custom-blocklist.txt to GitHub

Add this to your cron file to automatically commit and push changes:

```cron
0 4 * * * cd /path/to/your/blocklist/folder && git add custom-blocklist.txt && git commit -m "Auto commit $(date +\%Y-\%m-\%d)" && git push origin main
```
