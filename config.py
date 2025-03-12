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
PROXY_URL = 'http://host.docker.internal:7890' if IS_DOCKER else 'http://localhost:7890'
USE_PROXY = True
ALWAYS_SEND = True

# 时间配置
INTERVAL = 86400  # 改为24小时检查一次
TIME_OFFSET = 0

# DeFi 数据源配置
DEFILLAMA_API = {
    'base_url': 'https://api.llama.fi',
    'ethena_endpoint': '/protocol/ethena'
}

ETHENA_API = {
    'yield_url': 'https://ethena.fi/api/yields/protocol-and-staking-yield'
}

# 市场情绪指标配置
MARKET_SENTIMENT = {
    'ahr999_url': 'https://dncapi.flink1.com/api/v2/index/arh999',
    'ahr999_params': {
        'code': 'bitcoin',
        'webp': 1
    },
    'fear_greed_url': 'https://api.alternative.me/fng/',
    'btc_price_apis': {
        'primary': {
            'name': 'Binance',
            'url': 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT',
            'price_key_path': ['price']  # 用于从响应中提取价格的键路径
        },
        'backup': {
            'name': 'CoinGecko',
            'url': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
            'price_key_path': ['bitcoin', 'usd']  # 用于从响应中提取价格的键路径
        }
    },
    # 阈值配置
    'thresholds': {
        'fear_greed': {
            'extreme_fear': 20,  # 极度恐慌阈值
            'fear': 40,          # 恐慌阈值
            'neutral': 60,       # 中性阈值
            'greed': 80          # 贪婪阈值
        },
        'ahr999': {
            'extreme_value': 0.25,  # 极度超卖阈值
            'oversold': 0.45,       # 超卖阈值
            'fair_value': 0.8,      # 公允价值阈值
            'overbought': 1.2,      # 超买阈值
            'extreme_bubble': 1.8   # 极度泡沫阈值
        }
    },
    # 市场建议配置 - 整合后的建议
    'suggestions': {
        'ahr999': {
            'extreme_value_zone': {
                'range': [0, 0.25],
                'desc': '极度低估，强烈买入信号'
            },
            'bottom_zone': {
                'range': [0.25, 0.45],
                'desc': '明显低估，适量买入'
            },
            'accumulation_zone': {
                'range': [0.45, 0.8],
                'desc': '轻微低估，可定投积累'  
            },
            'fair_value_zone': {
                'range': [0.8, 1.2],
                'desc': '接近公允价值，谨慎定投'
            },
            'profit_taking_zone': {
                'range': [1.2, 1.8],
                'desc': '轻微高估，可考虑获利了结'
            },
            'bubble_zone': {
                'range': [1.8, float('inf')],
                'desc': '明显泡沫，建议减仓观望'
            }
        },
        'fear_greed': {
            'extreme_fear': {
                'range': [0, 20],
                'desc': '极度恐慌，可能是买入机会'
            },
            'fear': {
                'range': [20, 40],
                'desc': '市场恐慌，考虑逐步买入'
            },
            'neutral': {
                'range': [40, 60],
                'desc': '情绪中性，可定投'
            },
            'greed': {
                'range': [60, 80],
                'desc': '市场贪婪，注意风险'
            },
            'extreme_greed': {
                'range': [80, 100],
                'desc': '极度贪婪，谨慎操作'
            }
        }
    }
}
