"""
数据重组模块 - 将历史数据按日期重新组织

提供功能将BTC价格、AHR999指数和恐惧贪婪指数数据
按照日期合并，生成一个新的daily_data.json文件。
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_historical_data(file_path: str) -> Dict[str, Any]:
    """加载历史数据"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"从{file_path}加载了数据")
            return data
        else:
            logger.error(f"文件不存在: {file_path}")
            return {}
    except Exception as e:
        logger.error(f"加载数据出错: {str(e)}")
        return {}

def reorganize_by_date(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """按日期重新组织数据"""
    if not data:
        return {}
    
    # 获取各种数据源
    btc_price_data = data.get('btc_price', [])
    ahr999_data = data.get('ahr999', [])
    fear_greed_data = data.get('fear_greed', [])
    
    # 创建按日期索引的字典
    daily_data = {}
    
    # 处理BTC价格数据
    for item in btc_price_data:
        date = item.get('date')
        if not date:
            continue
            
        if date not in daily_data:
            daily_data[date] = {'date': date}
            
        daily_data[date]['price'] = item.get('price')
        # daily_data[date]['market_cap'] = item.get('market_cap')
        # daily_data[date]['volume'] = item.get('volume')
        # daily_data[date]['btc_timestamp'] = item.get('timestamp')
    
    # 处理AHR999指数数据
    for item in ahr999_data:
        date = item.get('date')
        if not date:
            continue
            
        if date not in daily_data:
            daily_data[date] = {'date': date}
            
        daily_data[date]['ahr999'] = item.get('ahr999')
        # for field in ['ma200', 'price_ma_ratio', 'ahr999_signal']:
        #     if field in item:
        #         daily_data[date][field] = item.get(field)
        # daily_data[date]['ahr999_timestamp'] = item.get('timestamp')
    
    # 处理恐惧与贪婪指数数据
    for item in fear_greed_data:
        date = item.get('date')
        if not date:
            continue
            
        if date not in daily_data:
            daily_data[date] = {'date': date}
            
        daily_data[date]['fear_greed_value'] = item.get('value')
        # daily_data[date]['fear_greed_classification'] = item.get('classification')
        # daily_data[date]['fear_greed_timestamp'] = item.get('timestamp')
    
    logger.info(f"按日期重组了{len(daily_data)}天的数据")
    return daily_data

def save_daily_data(daily_data: Dict[str, Dict[str, Any]], file_path: str) -> bool:
    """保存按日期组织的数据"""
    try:
        # 将字典转换为列表，并按日期排序
        data_list = list(daily_data.values())
        data_list.sort(key=lambda x: x['date'])
        
        # 创建包含元数据的完整数据结构
        complete_data = {
            "data": data_list,
            "count": len(data_list),
            "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "description": "Daily combined BTC price, AHR999 index and Fear & Greed index data"
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, indent=2, ensure_ascii=False)
        logger.info(f"数据已保存到: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存数据出错: {str(e)}")
        return False

def reorganize_data(input_file: str, output_file: str) -> bool:
    """重新组织数据主函数"""
    logger.info(f"开始重组数据: 从 {input_file} 到 {output_file}")
    
    # 确保数据目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 加载历史数据
    historical_data = load_historical_data(input_file)
    if not historical_data:
        logger.error("无法加载历史数据，退出函数")
        return False
    
    # 按日期重新组织数据
    daily_data = reorganize_by_date(historical_data)
    if not daily_data:
        logger.error("重组数据失败，退出函数")
        return False
    
    # 保存按日期组织的数据
    success = save_daily_data(daily_data, output_file)
    if success:
        logger.info(f"数据重组成功！已生成按日期组织的数据文件: {output_file}")
        logger.info(f"共处理了 {len(daily_data)} 天的数据")
        return True
    else:
        logger.error("数据重组失败")
        return False

def fix_data_file(data_file: str) -> bool:
    """修复数据文件格式问题
    
    Args:
        data_file: 数据文件路径
        
    Returns:
        是否成功修复
    """
    try:
        if not os.path.exists(data_file):
            logger.error(f"文件不存在: {data_file}")
            return False
            
        # 读取文件内容
        with open(data_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 尝试解析JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            logger.error("文件不是有效的JSON格式")
            return False
            
        # 验证数据格式并修复
        fixed = False
        
        # 如果是字符串，尝试再次解析
        if isinstance(data, str):
            try:
                data = json.loads(data)
                fixed = True
                logger.info("修复了JSON字符串嵌套问题")
            except:
                logger.error("无法解析嵌套的JSON字符串")
                return False
                
        # 如果是字典但不是列表，尝试提取数据数组
        if isinstance(data, dict) and not isinstance(data, list):
            if 'data' in data and isinstance(data['data'], list):
                data = data['data']
                fixed = True
                logger.info("从字典中提取了数据数组")
            else:
                # 转换为列表格式
                data = [data]
                fixed = True
                logger.info("将单个字典转换为列表")
                
        # 确保每个项都有日期字段
        items_to_remove = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                items_to_remove.append(i)
                continue
                
            if 'date' not in item or not item['date']:
                items_to_remove.append(i)
                continue
                
        # 从后向前移除无效项
        for i in sorted(items_to_remove, reverse=True):
            data.pop(i)
            fixed = True
            
        if items_to_remove:
            logger.info(f"移除了 {len(items_to_remove)} 个无效数据项")
            
        # 如果进行了修复，保存修复后的文件
        if fixed:
            backup_file = f"{data_file}.bak"
            os.rename(data_file, backup_file)
            logger.info(f"已备份原始文件: {backup_file}")
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"成功修复并保存数据文件: {data_file}")
            
        return True
        
    except Exception as e:
        logger.error(f"修复数据文件时出错: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return False