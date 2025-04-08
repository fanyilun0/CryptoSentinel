#!/usr/bin/env python
"""
加密货币监控系统 - 基于历史数据分析并提供买入/卖出建议
支持分析BTC价格、AHR999指数和恐惧贪婪指数
"""

import os
import sys
import json
import asyncio
import logging
import platform
from datetime import datetime

# 导入自定义模块
from config import DATA_DIRS
from utils.historical_data import HistoricalDataCollector
from utils.trend_analyzer import TrendAnalyzer
from utils.data_reorganizer import reorganize_data

# 从新的AI模块导入DeepseekAdvisor
from ai.advisor import DeepseekAdvisor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('crypto_monitor.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# 确保reports目录存在
os.makedirs("reports", exist_ok=True)

async def generate_analysis_report(force_update=False):
    """生成分析报告，基于历史数据提供买入/卖出建议"""
    logger.info("开始生成分析报告...")
    
    # 创建数据目录
    os.makedirs(DATA_DIRS['data'], exist_ok=True)
    
    # 初始化历史数据收集器
    collector = HistoricalDataCollector(data_dir=DATA_DIRS['data'])
    
    # 获取/更新历史数据
    if force_update:
        logger.info("强制更新历史数据...")
        historical_data = await collector.collect_historical_data()
    else:
        logger.info("检查并更新历史数据...")
        historical_data = await collector.update_historical_data()
    
    if not historical_data:
        logger.error("获取历史数据失败，无法生成分析报告")
        return False
    
    # 数据统计信息
    btc_count = len(historical_data.get("btc_price", []))
    ahr_count = len(historical_data.get("ahr999", []))
    fg_count = len(historical_data.get("fear_greed", []))
    
    logger.info(f"获取到的历史数据: BTC价格({btc_count}条), AHR999指数({ahr_count}条), 恐惧贪婪指数({fg_count}条)")
    
    # 初始化趋势分析器
    analyzer = TrendAnalyzer(historical_data)
    
    # 生成投资建议
    advice = analyzer.generate_investment_advice()
    
    if advice.get("status") == "error":
        logger.error(f"生成投资建议失败: {advice.get('message', '未知错误')}")
        return False
    
    # 获取格式化的输出结果
    report = advice.get("formatted_output", "")
    
    # 保存报告到文件
    report_file = f"{DATA_DIRS['reports']}/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"分析报告已保存到: {report_file}")
    
    # 打印报告
    print("\n" + report)
    
    return True, report_file

def get_ai_investment_advice():
    """获取AI投资建议（使用DeepSeek R1模型）"""
    print("=== AI投资顾问 (DeepSeek R1) ===\n")
    
    # 检查是否存在整合后的数据
    data_file = "data/daily_data.json"
    if not os.path.exists(data_file):
        print("错误: 未找到整合后的数据文件，请先运行数据重组工具")
        return
    
    # 初始化AI顾问
    advisor = DeepseekAdvisor()
    
    # 设置分析月数
    months = 6
    print(f"将分析最近{months}个月的数据")
    
    try:
        # 尝试读取数据文件，检查是否包含'responses'键
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 如果数据是直接的列表(不是包含responses的字典)，需要进行处理
            if isinstance(data, list):
                print("注意: 正在准备数据格式以供AI处理...")
                # 将数据包装在responses键下，这是DeepseekAdvisor可能期望的格式
                wrapped_data = {"responses": data}
                
                # 创建临时文件
                temp_file = data_file + ".temp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(wrapped_data, f, ensure_ascii=False, indent=2)
                
                # 使用临时文件代替原始文件
                data_file = temp_file
                print("数据格式已调整，继续处理...")
        except Exception as e:
            logger.warning(f"读取数据文件时出错: {str(e)}")
            print(f"警告: 读取数据文件时出错: {str(e)}，将继续尝试处理")
        
        # 获取投资建议
        print("\n正在获取AI投资建议，请稍候...\n")
        advice = advisor.get_investment_advice(data_file, months)
        
        if advice:
            print("\n成功获取AI投资建议:")
            print(advice)
        else:
            print("错误: 获取AI投资建议失败")
    
    except KeyError as e:
        logger.error(f"AI投资建议处理过程中出现键错误: {str(e)}")
        print(f"错误: AI投资建议处理过程中缺少必要的数据键 '{str(e)}'")
        
        # 特别处理'responses'键错误
        if str(e) == "'responses'":
            print("\n提示: DeepseekAdvisor需要'responses'字段。您的JSON数据结构可能需要调整。")
            print("建议格式: { \"responses\": [ ... 您的数据数组 ... ] }")
    
    except Exception as e:
        logger.error(f"AI投资建议处理过程中出错: {str(e)}")
        print(f"错误: {str(e)}")

async def main():
    """主函数
    
    执行流程:
    - 更新历史数据
    - 整合数据
    - 调用AI建议功能
    """
    try:
        # 显示欢迎信息
        print("\n====== 加密货币监控系统 ======")
        print("支持分析: BTC价格、AHR999指数和恐惧贪婪指数")
        print("==============================\n")

        # 执行基本流程：更新数据+AI建议
        print("正在检查数据更新，请稍候...\n")
        
        # 1. 更新历史数据
        try:
            await generate_analysis_report(force_update=False)
        except Exception as e:
            logger.error(f"生成分析报告时出错: {str(e)}")
            print(f"生成分析报告时出错: {str(e)}")
            # 继续执行后续步骤
        
        # 2. 整合数据
        try:
            data_dir = DATA_DIRS['data']
            input_file = os.path.join(data_dir, "historical_data.json")
            output_file = os.path.join(data_dir, "daily_data.json")
            
            # 确保数据目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 确保输入文件存在
            if not os.path.exists(input_file):
                logger.error(f"输入文件不存在: {input_file}")
                print(f"错误: 输入文件不存在: {input_file}")
                return 1
            
            # 调用重组数据函数
            print("正在整合数据为按日期组织的格式...\n")
            success = reorganize_data(input_file, output_file)
            
            if success:
                print(f"数据整合成功！已生成按日期组织的数据文件: {output_file}")
                print(f"数据文件处理完成: {output_file}\n")
            else:
                print("数据整合失败，请检查日志获取详细信息\n")
                # 继续执行后续步骤
        except Exception as e:
            print(f"数据整合过程中出错: {str(e)}")
            logger.error(f"数据整合过程中出错: {str(e)}")
            # 继续执行后续步骤
        
        # 3. 调用AI建议
        try:
            print("正在生成AI投资建议...\n")
            get_ai_investment_advice()
        except Exception as e:
            logger.error(f"生成AI投资建议过程中出错: {str(e)}")
            print(f"生成AI投资建议过程中出错: {str(e)}")
        
        print("\n处理完成，程序退出")

    except KeyboardInterrupt:
        print("\n程序被用户中断")
        return 1
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1

    return 0

if __name__ == "__main__":
    """程序入口"""
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 
