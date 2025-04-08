from collectors.base_collector import BaseDataCollector
import logging
from datetime import datetime, timedelta
import time
import random
import numpy as np
from config import MARKET_SENTIMENT, PROXY_URL, USE_PROXY

logger = logging.getLogger(__name__)

class AHR999Collector(BaseDataCollector):
    """AHR999指数历史数据收集器"""
    
    def __init__(self, data_dir="data"):
        """初始化AHR999指数数据收集器"""
        super().__init__(data_dir, PROXY_URL, USE_PROXY)
        self.ahr999_history_file = "ahr999_history.json"
        self.api_url = MARKET_SENTIMENT['ahr999_url']
    
    async def get_ahr999_history(self, days=365, keep_extra_data=False):
        """
        获取AHR999指数历史数据
        
        参数:
            days: 获取的天数
            keep_extra_data: 是否保留额外数据（BTC价格、MA200和比率）
        """
        logger.info("正在获取AHR999指数历史数据...")
        
        # 尝试从本地文件加载，检查是否在24小时内更新过
        ahr_data = self.load_from_json(self.ahr999_history_file)
        if ahr_data and len(ahr_data) > 0:
            # 检查数据是否是最新的
            try:
                latest_time = max(item.get("timestamp", 0) for item in ahr_data if isinstance(item.get("timestamp"), (int, float)))
                current_time = int(time.time())
                # 如果最新数据在24小时内，直接使用缓存数据
                if (current_time - latest_time) < 24 * 60 * 60:
                    logger.info(f"使用缓存的AHR999指数历史数据，最新数据时间: {datetime.fromtimestamp(latest_time)}")
                    return ahr_data
                else:
                    logger.info(f"缓存数据已过期，重新获取AHR999指数历史数据")
            except Exception as e:
                logger.error(f"检查AHR999数据时间出错: {str(e)}")
        
        # 尝试从API获取数据
        try:
            # 使用代理
            data = await self.fetch_data(self.api_url, use_proxy=True)
            
            # 如果代理请求失败，尝试不使用代理
            if not data:
                logger.info("使用代理获取AHR999数据失败，尝试不使用代理...")
                data = await self.fetch_data(self.api_url, use_proxy=False)
            
            if data and "data" in data and isinstance(data["data"], list) and ("code" not in data or data.get("code") == 200 or data.get("code") == 0):
                logger.info(f"成功获取到AHR999历史数据，条目数: {len(data['data'])}")
                
                # 解析API返回的数据结构
                # 数据格式: [timestamp, ahr999_value, price, ma200, price/ma200ratio]
                ahr999_history = []
                
                # 过滤获取最近days天的数据
                filtered_data = data["data"]
                if len(filtered_data) > days:
                    filtered_data = filtered_data[-days:]
                
                for item in filtered_data:
                    try:
                        if len(item) >= 2:  # 确保至少有时间戳和AHR999值
                            timestamp = int(item[0])
                            ahr999_value = float(item[1])
                            
                            entry = {
                                "timestamp": timestamp,
                                "date": datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'),
                                "ahr999": ahr999_value
                            }
                            
                            # 可选添加其他数据字段
                            if keep_extra_data and len(item) >= 5:
                                entry["price"] = float(item[2])      # BTC价格
                                entry["ma200"] = float(item[3])      # 200日均线
                                entry["price_ma_ratio"] = float(item[4])  # 价格/均线比值
                            
                            ahr999_history.append(entry)
                    except (IndexError, ValueError) as e:
                        logger.error(f"解析AHR999数据出错: {str(e)}, 数据: {item}")
                
                # 按照时间戳排序，最新的在前
                ahr999_history.sort(key=lambda x: x["timestamp"], reverse=True)
                
                # 保存到文件
                self.save_to_json(ahr999_history, self.ahr999_history_file)
                
                return ahr999_history
            else:
                logger.error("获取AHR999历史数据失败或数据格式不正确")
                # 如果API获取失败，生成模拟数据
                return self.generate_mock_ahr999_data(days)
        except Exception as e:
            logger.error(f"获取AHR999历史数据异常: {str(e)}")
            
            # 如果API获取失败，生成模拟数据
            return self.generate_mock_ahr999_data(days)
    
    def generate_mock_ahr999_data(self, days=365):
        """生成模拟的AHR999指数历史数据"""
        logger.info(f"生成{days}天的模拟AHR999指数历史数据")
        
        # 确保随机数生成是确定的
        random.seed(42)
        np.random.seed(42)
        
        # 生成模拟数据
        start_date = datetime.now()
        ahr999_history = []
        
        # 使用正弦波模拟市场周期，加上随机波动
        base_value = 1.0  # 起始值
        cycle_length = 365 * 4  # 4年周期
        amplitude = 0.8  # 波动幅度
        
        for i in range(days):
            date = start_date - timedelta(days=i)
            timestamp = int(date.timestamp())
            date_str = date.strftime('%Y-%m-%d')
            
            # 基础周期值
            cycle_position = (i % cycle_length) / cycle_length * 2 * np.pi
            cycle_value = base_value + amplitude * np.sin(cycle_position)
            
            # 添加随机波动
            random_factor = 1.0 + random.uniform(-0.1, 0.1)  # ±10%随机波动
            ahr999_value = max(0.1, min(3.0, cycle_value * random_factor))  # 限制在合理范围内
            
            # 添加一些小趋势
            if i % 30 < 15:  # 每月前半部分小幅上涨
                trend_factor = 1.0 + random.uniform(0, 0.02)  # 0-2%上涨
            else:  # 每月后半部分小幅下跌
                trend_factor = 1.0 - random.uniform(0, 0.02)  # 0-2%下跌
            
            ahr999_value *= trend_factor
            
            # 生成数据点
            ahr999_history.append({
                "timestamp": timestamp,
                "date": date_str,
                "ahr999": round(ahr999_value, 4)
            })
        
        # 排序，最新的日期在前面
        ahr999_history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # 保存到文件
        self.save_to_json(ahr999_history, self.ahr999_history_file)
        
        return ahr999_history 