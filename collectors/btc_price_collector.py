from collectors.base_collector import BaseDataCollector
import logging
from datetime import datetime
import time
import os
from config import MARKET_SENTIMENT, PROXY_URL, USE_PROXY

logger = logging.getLogger(__name__)

class BTCPriceCollector(BaseDataCollector):
    """BTC价格历史数据收集器"""
    
    def __init__(self, data_dir="data"):
        """初始化BTC价格数据收集器"""
        super().__init__(data_dir, PROXY_URL, USE_PROXY)
        self.btc_history_file = "btc_price_history.json"
        self.api_url = MARKET_SENTIMENT['btc_price_url']
    
    async def get_price_history(self, days=180):
        """获取BTC价格历史数据"""
        logger.info(f"正在获取{days}天的BTC价格历史数据...")
        
        # 尝试先从本地文件加载
        btc_data = self.load_from_json(self.btc_history_file)
        if btc_data and len(btc_data) > 0:
            # 检查数据是否是最新的
            latest_time = max(int(item.get("timestamp", 0)) for item in btc_data)
            current_time = int(time.time() * 1000)
            # 如果最新数据在24小时内，直接使用缓存数据
            if (current_time - latest_time) < 24 * 60 * 60 * 1000:
                logger.info(f"使用缓存的BTC价格历史数据，最新数据时间: {datetime.fromtimestamp(latest_time/1000)}")
                return btc_data
            else:
                logger.info(f"缓存数据已过期，最新数据时间: {datetime.fromtimestamp(latest_time/1000)}")
        
        # 尝试从API获取数据
        try:
            # Binance K线数据参数
            params = {
                "symbol": "BTCUSDT",
                "interval": "1d",
                "limit": min(days, 1000)  # Binance API限制最多1000条
            }
            
            # 首先尝试使用代理
            data = await self.fetch_data(self.api_url, params, use_proxy=True)
            
            # 如果代理请求失败，尝试不使用代理
            if not data:
                logger.info("使用代理获取BTC价格数据失败，尝试不使用代理...")
                data = await self.fetch_data(self.api_url, params, use_proxy=False)
            
            if data and isinstance(data, list):
                logger.info(f"成功获取到{len(data)}条BTC价格历史数据")
                
                # 解析Binance K线数据
                # K线格式: [开盘时间, 开盘价, 最高价, 最低价, 收盘价, 成交量, 收盘时间, 成交额, 成交笔数, 主动买入成交量, 主动买入成交额, 忽略]
                btc_history = []
                for item in data:
                    try:
                        timestamp = int(item[0])  # 开盘时间
                        close_price = float(item[4])  # 收盘价
                        
                        btc_history.append({
                            "timestamp": timestamp,
                            "date": datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d'),
                            "price": close_price
                        })
                    except (IndexError, ValueError) as e:
                        logger.error(f"解析BTC价格数据出错: {str(e)}, 数据: {item}")
                
                # 按照时间戳排序
                btc_history.sort(key=lambda x: x["timestamp"], reverse=True)
                
                # 保存到文件
                self.save_to_json(btc_history, self.btc_history_file)
                
                return btc_history
            else:
                logger.error("获取BTC价格历史数据失败")
                # 尝试从本地加载旧数据
                return self.load_from_json(self.btc_history_file) or []
        except Exception as e:
            logger.error(f"获取BTC价格历史数据异常: {str(e)}")
            # 尝试从本地加载旧数据
            return self.load_from_json(self.btc_history_file) or [] 