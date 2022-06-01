import os


BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print('You have forgot to set BOT_TOKEN')
    quit()

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')


# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT'))


# https://stackoverflow.com/questions/43452544/what-is-https-i-instagram-com-api-v1
# https://github.com/ohld/igbot
# https://instagram.api-docs.io/1.0/media/JQFw3CS3GKfLs2ukL

# from settings import (BOT_TOKEN,HEROKU_APP_NAME,WEBHOOK_URL, WEBHOOK_PATH,WEBAPP_HOST, WEBAPP_PORT)


async def on_startup(dp):
    logging.warning(
        'Starting connection. ')
    await bot.set_webhook(WEBHOOK_URL,drop_pending_updates=True)

if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)
    '''start_webhook(dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )'''