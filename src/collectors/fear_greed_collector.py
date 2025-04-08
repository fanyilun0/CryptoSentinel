from collectors.base_collector import BaseDataCollector
import logging
from datetime import datetime, timedelta
import time
from config import MARKET_SENTIMENT, PROXY_URL, USE_PROXY

logger = logging.getLogger(__name__)

class FearGreedCollector(BaseDataCollector):
    """恐惧与贪婪指数历史数据收集器"""
    
    def __init__(self, data_dir="data"):
        """初始化恐惧与贪婪指数数据收集器"""
        super().__init__(data_dir, PROXY_URL, USE_PROXY)
        self.fng_history_file = "fng_history.json"
        self.api_url = MARKET_SENTIMENT['fear_greed_url']
        
        # 恐惧与贪婪指数API需要获取所有历史数据
        if "?" in self.api_url:
            self.api_url += "&limit=0"
        else:
            self.api_url += "?limit=0"
    
    async def get_fear_greed_history(self, days=180):
        """获取恐惧与贪婪指数历史数据"""
        logger.info("正在获取恐惧与贪婪指数历史数据...")
        
        # 尝试从本地文件加载
        fng_data = self.load_from_json(self.fng_history_file)
        if fng_data and "data" in fng_data and len(fng_data["data"]) > 0:
            # 检查数据是否是最新的
            try:
                latest_time = int(fng_data["data"][0]["timestamp"])
                current_time = int(time.time())
                # 如果最新数据在24小时内，直接使用缓存数据
                if (current_time - latest_time) < 24 * 60 * 60:
                    logger.info(f"使用缓存的恐惧与贪婪指数历史数据，最新数据时间: {datetime.fromtimestamp(latest_time)}")
                    return self.format_fng_data(fng_data, days)
                else:
                    logger.info(f"缓存数据已过期，重新获取恐惧与贪婪指数历史数据")
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"检查FNG数据时间出错: {str(e)}")
        
        # 尝试使用代理获取数据
        try:
            # 使用代理
            data = await self.fetch_data(self.api_url, use_proxy=True)
            
            # 如果代理请求失败，尝试不使用代理
            if not data:
                logger.info("使用代理获取恐惧与贪婪指数数据失败，尝试不使用代理...")
                data = await self.fetch_data(self.api_url, use_proxy=False)
            
            if data and "data" in data:
                logger.info(f"成功获取到{len(data['data'])}条恐惧与贪婪指数历史数据")
                
                # 保存到本地文件
                self.save_to_json(data, self.fng_history_file)
                
                # 格式化数据
                return self.format_fng_data(data, days)
            else:
                logger.error("获取恐惧与贪婪指数历史数据失败")
                # 尝试从本地加载旧数据
                raw_data = self.load_from_json(self.fng_history_file)
                if raw_data:
                    return self.format_fng_data(raw_data, days)
                return []
        except Exception as e:
            logger.error(f"获取恐惧与贪婪指数历史数据异常: {str(e)}")
            
            # 尝试从本地加载旧数据
            raw_data = self.load_from_json(self.fng_history_file)
            if raw_data:
                return self.format_fng_data(raw_data, days)
            return []
    
    def format_fng_data(self, data, days=180):
        """格式化恐惧与贪婪指数数据并根据days参数过滤"""
        if not data or "data" not in data:
            return []
        
        formatted_data = []
        today = datetime.now()
        past_date = today - timedelta(days=days)
        
        for item in data["data"]:
            try:
                timestamp = int(item["timestamp"])
                date_obj = datetime.fromtimestamp(timestamp)
                
                # 过滤，只保留指定天数内的数据
                if date_obj >= past_date:
                    formatted_data.append({
                        "timestamp": timestamp,
                        "date": date_obj.strftime('%Y-%m-%d'),
                        "value": int(item["value"]),
                        "value_classification": item["value_classification"]
                    })
            except (KeyError, ValueError) as e:
                logger.error(f"格式化恐惧与贪婪指数数据出错: {str(e)}, 数据: {item}")
        
        # 按照时间戳排序，最新的在前
        formatted_data.sort(key=lambda x: x["timestamp"], reverse=True)
        return formatted_data 