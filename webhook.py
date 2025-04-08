import aiohttp
from config import WEBHOOK_URL, PROXY_URL, USE_PROXY

async def send_message_async(message_content):
    """发送消息到webhook"""
    # 打印消息内容
    print("\n发送的消息内容:")
    print("="*50)
    print(message_content)
    print("="*50)
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "msgtype": "text",
        "text": {
            "content": message_content
        }
    }
    
    proxy = PROXY_URL if USE_PROXY else None
    async with aiohttp.ClientSession() as session:
        async with session.post(WEBHOOK_URL, json=payload, headers=headers, proxy=proxy) as response:
            if response.status == 200:
                print("消息发送成功!")
            else:
                print(f"消息发送失败: {response.status}, {await response.text()}")