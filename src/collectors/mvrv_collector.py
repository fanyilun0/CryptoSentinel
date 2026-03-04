from collectors.base_collector import BaseDataCollector
import logging
from datetime import datetime, timedelta
import time
import random
import numpy as np
from config import MARKET_SENTIMENT, PROXY_URL, USE_PROXY

logger = logging.getLogger(__name__)


class MVRVCollector(BaseDataCollector):
    """MVRV（已实现市值比率）历史数据收集器
    
    数据源: CoinMetrics Community API (免费, 无需API Key)
    指标: CapMVRVCur - 当前市场市值与已实现市值的比率
    """
    
    def __init__(self, data_dir="data"):
        super().__init__(data_dir, PROXY_URL, USE_PROXY)
        self.mvrv_history_file = "mvrv_history.json"
        self.api_url = MARKET_SENTIMENT['mvrv_url']
        self.page_size = 1000
    
    async def get_mvrv_history(self, days=365):
        """获取MVRV比率历史数据"""
        logger.info("正在获取MVRV比率历史数据...")
        
        cached = self.load_from_json(self.mvrv_history_file)
        if cached and len(cached) > 0:
            try:
                latest_time = max(
                    item.get("timestamp", 0) for item in cached
                    if isinstance(item.get("timestamp"), (int, float))
                )
                if (int(time.time()) - latest_time) < 24 * 60 * 60:
                    logger.info(f"使用缓存的MVRV历史数据，最新数据时间: {datetime.fromtimestamp(latest_time)}")
                    return cached
                else:
                    logger.info("缓存数据已过期，重新获取MVRV历史数据")
            except Exception as e:
                logger.error(f"检查MVRV数据时间出错: {str(e)}")
        
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            params = {
                'assets': 'btc',
                'metrics': 'CapMVRVCur',
                'frequency': '1d',
                'page_size': str(self.page_size),
                'start_time': start_date
            }
            
            all_data = []
            url = self.api_url
            current_params = params.copy()
            
            while True:
                data = await self.fetch_data(url, params=current_params, use_proxy=False)
                
                if not data and self.use_proxy:
                    logger.info("直连获取MVRV数据失败，尝试使用代理...")
                    data = await self.fetch_data(url, params=current_params, use_proxy=True)
                
                if not data or 'data' not in data:
                    break
                
                all_data.extend(data['data'])
                
                if 'next_page_token' in data and data['next_page_token']:
                    current_params = {'next_page_token': data['next_page_token']}
                    current_params.update({
                        'assets': 'btc',
                        'metrics': 'CapMVRVCur',
                        'frequency': '1d',
                        'page_size': str(self.page_size),
                    })
                else:
                    break
            
            if all_data:
                logger.info(f"成功获取到MVRV历史数据，条目数: {len(all_data)}")
                mvrv_history = self._parse_coinmetrics_data(all_data)
                mvrv_history.sort(key=lambda x: x["timestamp"], reverse=True)
                self.save_to_json(mvrv_history, self.mvrv_history_file)
                return mvrv_history
            else:
                logger.error("获取MVRV历史数据失败或数据为空")
                return self._generate_mock_mvrv_data(days)
                
        except Exception as e:
            logger.error(f"获取MVRV历史数据异常: {str(e)}")
            return self._generate_mock_mvrv_data(days)
    
    def _parse_coinmetrics_data(self, raw_data: list) -> list:
        """解析CoinMetrics API返回的数据"""
        mvrv_history = []
        for item in raw_data:
            try:
                time_str = item.get('time', '')
                mvrv_value = item.get('CapMVRVCur')
                if not time_str or mvrv_value is None:
                    continue
                
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                date_str = dt.strftime('%Y-%m-%d')
                timestamp = int(dt.timestamp())
                
                mvrv_history.append({
                    "timestamp": timestamp,
                    "date": date_str,
                    "mvrv": round(float(mvrv_value), 6)
                })
            except (ValueError, TypeError) as e:
                logger.error(f"解析MVRV数据出错: {str(e)}, 数据: {item}")
        
        return mvrv_history
    
    def _generate_mock_mvrv_data(self, days=365):
        """生成模拟的MVRV历史数据（API不可用时的降级方案）"""
        logger.info(f"生成{days}天的模拟MVRV历史数据")
        
        random.seed(42)
        np.random.seed(42)
        
        start_date = datetime.now()
        mvrv_history = []
        
        base_value = 1.5
        cycle_length = 365 * 4
        amplitude = 1.2
        
        for i in range(days):
            date = start_date - timedelta(days=i)
            timestamp = int(date.timestamp())
            date_str = date.strftime('%Y-%m-%d')
            
            cycle_position = (i % cycle_length) / cycle_length * 2 * np.pi
            cycle_value = base_value + amplitude * np.sin(cycle_position)
            
            random_factor = 1.0 + random.uniform(-0.05, 0.05)
            mvrv_value = max(0.5, min(4.0, cycle_value * random_factor))
            
            mvrv_history.append({
                "timestamp": timestamp,
                "date": date_str,
                "mvrv": round(mvrv_value, 6)
            })
        
        mvrv_history.sort(key=lambda x: x["timestamp"], reverse=True)
        self.save_to_json(mvrv_history, self.mvrv_history_file)
        return mvrv_history
