import httpx
import logging 
from bot.config import BACKEND_API_URL, BOT_API_SECRET

logger = logging.getLogger(__name__)

class BackendAPIClient:
    
    def __init__(self,  base_url: str = BACKEND_API_URL, secret: str = BOT_API_SECRET):
        self.base_url = base_url.rstrip('/')
        self.headers= {
            "X-Bot-Secret": secret,
            "Content-Type": 'application/json'
        }

    async def confirm_telegram_account(self, token: str, chat_id: int):

        url = f"{self.base_url}/notifications/telegram/confirm/"
        payload = {"token": token, "chat_id": chat_id}


        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                )
                return response
        except Exception as ex:
            logger.error(f"confirm_telegram_account ulanish xatosi: {ex}")
            return None

    async def get_user_events(self, chat_id: int):

        url = f"{self.base_url}/notifications/telegram/my-events/"
        payload = {"chat_id": chat_id}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                return response
        except Exception as ex:
            logger.error(f"get_user_events ulanish xatosi: {ex}")
            return None 


api_client = BackendAPIClient()

        

