import asyncio
import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

from collectors import BTCPriceCollector, AHR999Collector, FearGreedCollector
from config import PROXY_URL, USE_PROXY

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HistoricalDataCollector:
    """历史数据收集器，整合BTC价格、恐慌贪婪指数和AHR999指数的历史数据"""
    
    def __init__(self, data_dir="data"):
        """初始化历史数据收集器"""
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, "historical_data.json")
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化各个专用收集器
        self.btc_collector = BTCPriceCollector(data_dir)
        self.ahr999_collector = AHR999Collector(data_dir)
        self.fng_collector = FearGreedCollector(data_dir)
    
    async def collect_historical_data(self, days=180) -> Dict[str, Any]:
        """收集所有历史数据"""
        logger.info(f"开始收集{days}天的历史数据...")
        
        # 并行获取所有数据
        btc_task = asyncio.create_task(self.btc_collector.get_price_history(days))
        ahr_task = asyncio.create_task(self.ahr999_collector.get_ahr999_history(days))
        fng_task = asyncio.create_task(self.fng_collector.get_fear_greed_history(days))
        
        # 等待所有任务完成
        btc_history = await btc_task
        ahr_history = await ahr_task
        fng_history = await fng_task
        
        # 整合数据
        historical_data = {
            "btc_price": btc_history,
            "ahr999": ahr_history,
            "fear_greed": fng_history,
            "last_updated": int(time.time())
        }
        
        # 保存整合数据
        self.save_historical_data(historical_data)
        
        return historical_data
    
    def save_historical_data(self, data: Dict[str, Any]) -> bool:
        """保存历史数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"历史数据已保存到: {self.data_file}")
            return True
        except Exception as e:
            logger.error(f"保存历史数据出错: {str(e)}")
            return False
    
    def load_historical_data(self) -> Optional[Dict[str, Any]]:
        """加载历史数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"从本地文件加载历史数据: {self.data_file}")
                return data
            else:
                logger.warning(f"历史数据文件不存在: {self.data_file}")
                return None
        except Exception as e:
            logger.error(f"加载历史数据出错: {str(e)}")
            return None
    
    def merge_historical_data(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """合并历史数据"""
        if not old_data:
            return new_data
        
        if not new_data:
            return old_data
        
        merged_data = {}
        
        # 合并BTC价格数据
        if "btc_price" in old_data and "btc_price" in new_data:
            old_btc = {item["date"]: item for item in old_data["btc_price"]} if old_data.get("btc_price") else {}
            new_btc = {item["date"]: item for item in new_data["btc_price"]} if new_data.get("btc_price") else {}
            old_btc.update(new_btc)  # 新数据覆盖旧数据
            merged_data["btc_price"] = list(old_btc.values())
            merged_data["btc_price"].sort(key=lambda x: x["timestamp"], reverse=True)
        else:
            merged_data["btc_price"] = new_data.get("btc_price", old_data.get("btc_price", []))
        
        # 合并AHR999数据
        if "ahr999" in old_data and "ahr999" in new_data:
            old_ahr = {item["date"]: item for item in old_data["ahr999"]} if old_data.get("ahr999") else {}
            new_ahr = {item["date"]: item for item in new_data["ahr999"]} if new_data.get("ahr999") else {}
            old_ahr.update(new_ahr)  # 新数据覆盖旧数据
            merged_data["ahr999"] = list(old_ahr.values())
            merged_data["ahr999"].sort(key=lambda x: x["timestamp"], reverse=True)
        else:
            merged_data["ahr999"] = new_data.get("ahr999", old_data.get("ahr999", []))
        
        # 合并恐惧与贪婪指数数据
        if "fear_greed" in old_data and "fear_greed" in new_data:
            old_fng = {item["date"]: item for item in old_data["fear_greed"]} if old_data.get("fear_greed") else {}
            new_fng = {item["date"]: item for item in new_data["fear_greed"]} if new_data.get("fear_greed") else {}
            old_fng.update(new_fng)  # 新数据覆盖旧数据
            merged_data["fear_greed"] = list(old_fng.values())
            merged_data["fear_greed"].sort(key=lambda x: x["timestamp"], reverse=True)
        else:
            merged_data["fear_greed"] = new_data.get("fear_greed", old_data.get("fear_greed", []))
        
        # 更新时间戳
        merged_data["last_updated"] = int(time.time())
        
        return merged_data
    
    async def update_historical_data(self, force=False) -> Dict[str, Any]:
        """更新历史数据，如果需要的话"""
        # 加载旧数据
        old_data = self.load_historical_data()
        
        # 如果没有旧数据或强制更新，则收集新数据
        if not old_data or force:
            logger.info("没有现有历史数据或强制更新，收集新数据...")
            return await self.collect_historical_data()
        
        # 检查数据是否过期（超过12小时）
        last_updated = old_data.get("last_updated", 0)
        current_time = int(time.time())
        if (current_time - last_updated) >= 12 * 60 * 60:
            logger.info(f"历史数据已过期，上次更新时间: {datetime.fromtimestamp(last_updated)}")
            new_data = await self.collect_historical_data()
            return self.merge_historical_data(old_data, new_data)
        else:
            logger.info(f"历史数据未过期，上次更新时间: {datetime.fromtimestamp(last_updated)}")
            return old_data


# 示例使用代码
async def main():
    collector = HistoricalDataCollector()
    data = await collector.update_historical_data()
    print(f"共获取到 {len(data.get('btc_price', []))} 条BTC价格数据")
    print(f"共获取到 {len(data.get('ahr999', []))} 条AHR999指数数据")
    print(f"共获取到 {len(data.get('fear_greed', []))} 条恐惧与贪婪指数数据")


if __name__ == "__main__":
    asyncio.run(main()) 