# Webhook配置
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 添加默认值和类型检查
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')  # 设置默认空字符串

# 根据环境变量判断是否在Docker中运行
IS_DOCKER = os.getenv('IS_DOCKER', 'false').lower() == 'true'

# 根据运行环境选择代理地址
PROXY_URL = 'http://host.docker.internal:7890' if IS_DOCKER else 'http://127.0.0.1:7890'
USE_PROXY = True
ALWAYS_SEND = True

# 时间配置
INTERVAL = 86400  # 改为24小时检查一次
TIME_OFFSET = 0

# 阈值配置
# 'thresholds': {
#     'fear_greed': {
#         'extreme_fear': 20,  # 极度恐慌阈值
#         'fear': 40,          # 恐慌阈值
#         'neutral': 60,       # 中性阈值
#         'greed': 80          # 贪婪阈值
#     },
#     'ahr999': {
#         'extreme_value': 0.25,  # 极度超卖阈值
#         'oversold': 0.45,       # 超卖阈值
#         'fair_value': 0.8,      # 公允价值阈值
#         'overbought': 1.2,      # 超买阈值
#         'extreme_bubble': 1.8   # 极度泡沫阈值
#     }
# }

# 市场情绪指标配置
MARKET_SENTIMENT = {
    # API端点
    'fear_greed_url': 'https://api.alternative.me/fng/',  # 不带limit参数，在代码中添加
    'ahr999_url': 'https://dncapi.flink1.com/api/v2/index/arh999?code=bitcoin&webp=1',  # 使用当前实际工作的API
    'btc_price_url': 'https://api.binance.com/api/v3/klines',
}
