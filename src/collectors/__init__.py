"""
数据收集器模块
包含以下收集器：
- BTC价格数据收集器
- AHR999指数数据收集器
- 恐惧与贪婪指数数据收集器
"""

from collectors.base_collector import BaseDataCollector
from collectors.btc_price_collector import BTCPriceCollector
from collectors.ahr999_collector import AHR999Collector
from collectors.fear_greed_collector import FearGreedCollector

__all__ = [
    'BaseDataCollector',
    'BTCPriceCollector',
    'AHR999Collector',
    'FearGreedCollector'
] 