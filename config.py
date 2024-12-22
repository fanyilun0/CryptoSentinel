# Webhook配置
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 添加默认值和类型检查
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')  # 设置默认空字符串

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
    'btc_price_url': 'https://api.coindesk.com/v1/bpi/currentprice.json',
    'fear_greed_alerts': {
        'extreme_fear': 20,  # 极度恐慌阈值
        'extreme_greed': 80  # 极度贪婪阈值
    },
    'fear_greed_suggestions': {
        'extreme_fear': {
            'range': [0, 20],
            'desc': '市场极度恐慌,可能是较好的买入机会'
        },
        'fear': {
            'range': [20, 40],
            'desc': '市场恐慌,可考虑逐步买入'
        },
        'neutral': {
            'range': [40, 60],
            'desc': '市场情绪中性,可以考虑定投'
        },
        'greed': {
            'range': [60, 80],
            'desc': '市场贪婪,注意风险,可以考虑减仓'
        },
        'extreme_greed': {
            'range': [80, 100],
            'desc': '市场极度贪婪,建议谨慎,可考虑逐步卖出'
        }
    }
}

# 代理配置
PROXY_URL = 'http://localhost:7890'
USE_PROXY = True
ALWAYS_SEND = True

# 时间配置
INTERVAL = 14400 # 每天检查一次
TIME_OFFSET = 0

# 数据监控配置
MONITOR_CONFIG = {
    'ethena': {
        'enabled': True,
        'min_apy_alert': 10.0,  # APY低于此值时报警
        'min_tvl_alert': 100000000  # TVL低于此值时报警(单位:美元)
    },
    'market_sentiment': {
        'enabled': True,
        'ahr999_extreme_values': {
            'oversold': 0.45,  # 超卖阈值
            'overbought': 1.2   # 超买阈值
        },
        'ahr999_suggestions': {
            'bottom_zone': {
                'range': [0, 0.45],
                'desc': '当前处于抄底区域,建议适量买入'
            },
            'dca_zone': {
                'range': [0.45, 1.2],
                'desc': '当前处于价值区间,适合定投操作'  
            },
            'high_zone': {
                'range': [1.2, float('inf')],
                'desc': '当前币价较高,不适合操作'
            }
        },
        'fear_greed_alerts': {
            'extreme_fear': 20,  # 极度恐慌阈值
            'extreme_greed': 80  # 极度贪婪阈值
        },
        'fear_greed_suggestions': {
            'extreme_fear': {
                'range': [0, 20],
                'desc': '市场极度恐慌,可能是较好的买入机会'
            },
            'fear': {
                'range': [20, 40],
                'desc': '市场恐慌,可考虑逐步买入'
            },
            'neutral': {
                'range': [40, 60],
                'desc': '市场情绪中性,可以考虑定投'
            },
            'greed': {
                'range': [60, 80],
                'desc': '市场贪婪,注意风险,可以考虑减仓'
            },
            'extreme_greed': {
                'range': [80, 100],
                'desc': '市场极度贪婪,建议谨慎,可考虑逐步卖出'
            }
        }
    }
}
