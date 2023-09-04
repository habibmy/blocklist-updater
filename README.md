
# Blocklist Updater

Add domains to be blocked using pi-hole with Telegram Bot.

## Getting Started

### Using Docker

1. **Pull the Docker Image**:

   To get started, you can pull the Blocklist Updater Docker image from Docker Hub:

   ```bash
   docker pull habibmy/blocklist-updater

2. **Run the Docker Container**:

	Run the Docker container, specifying any necessary environment variables. Be sure to mount a volume to `/data` to ensure persistence of the blocklist file. Replace `/your/local/data/folder` with the path to your local data folder:
	```bash
	docker run -d \
	  --name blocklist-updater \
	  -v /path/to/directory/containing/custom-blocklist-file:/data \
	  -e BLOCKLIST_FILE_NAME=custom-blocklist.txt \
	  -e TELEGRAM_BOT_TOKEN=your_telegram_bot_token \
	  -e AUTHORIZED_USER_CHAT_ID=your_authorized_user_chat_id 
	  

Replace the environment variable values (`BLOCKLIST_FILE_NAME`, `TELEGRAM_BOT_TOKEN`, `AUTHORIZED_USER_CHAT_ID`) with your specific configuration.

-   `BLOCKLIST_FILE_NAME`: The name of the blocklist file.
-   `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
-   `AUTHORIZED_USER_CHAT_ID`: Your telegram user's chat ID.

### Commit the custom-blocklist.txt to github
Add this to your cron file.

`0 4 * * * cd /path/to/your/blocklist.txt && git add blocklist.txt && git commit -m "Auto commit $(date +\%Y-\%m-\%d)" && git push origin main
`
