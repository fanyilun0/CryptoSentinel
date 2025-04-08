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
import argparse

# 导入自定义模块
from utils.historical_data import HistoricalDataCollector
from utils.trend_analyzer import TrendAnalyzer
from utils.data_reorganizer import reorganize_data, fix_data_file

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

def clear_screen():
    """清除屏幕"""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def print_menu():
    """打印菜单"""
    print("\n--- 主菜单 ---")
    print("1. 生成分析报告 (使用缓存数据)")
    print("2. 更新数据并生成分析报告")
    print("3. 运行AHR999数据获取工具")
    print("4. 查看最新报告")
    print("5. 使用AI顾问 (Deepseek R1模型)")
    print("6. 退出程序")
    print("-------------\n")

async def generate_analysis_report(force_update=False):
    """生成分析报告，基于历史数据提供买入/卖出建议"""
    logger.info("开始生成分析报告...")
    
    # 创建数据目录
    os.makedirs("data", exist_ok=True)
    
    # 初始化历史数据收集器
    collector = HistoricalDataCollector(data_dir="data")
    
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
    report_file = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"分析报告已保存到: {report_file}")
    
    # 打印报告
    print("\n" + report)
    
    return True, report_file

async def run_ahr999_tool():
    """运行AHR999数据获取工具"""
    try:
        logger.info("运行AHR999数据收集器...")
        
        # 确保data目录存在
        os.makedirs("data", exist_ok=True)
        
        print("AHR999数据获取工具")
        print("=" * 50)
        
        # 使用专用的AHR999收集器
        from collectors import AHR999Collector
        collector = AHR999Collector(data_dir="data")
        
        # 获取AHR999数据
        ahr999_data = await collector.get_ahr999_history(days=365, keep_extra_data=True)
        
        if ahr999_data and len(ahr999_data) > 0:
            print(f"\n成功获取AHR999数据! 共 {len(ahr999_data)} 条记录")
            
            # 打印最新数据
            latest = ahr999_data[0]
            print(f"\n最新数据 ({latest['date']}):")
            print(f"AHR999指数: {latest['ahr999']:.4f}")
            if "price" in latest:
                print(f"BTC价格: ${latest['price']:,.2f}")
            if "ma200" in latest:
                print(f"200日均线: ${latest['ma200']:,.2f}")
            if "price_ma_ratio" in latest:
                print(f"价格/均线比值: {latest['price_ma_ratio']:.4f}")
            
            return True
        else:
            print("\n无法获取AHR999数据")
            return False

    except Exception as e:
        logger.error(f"运行AHR999数据获取工具出错: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return False

def get_latest_report():
    """获取最新的报告文件"""
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        return None
        
    reports = [f for f in os.listdir(reports_dir) if f.startswith("report_") and f.endswith(".txt")]
    if not reports:
        return None
    
    # 按文件名排序，最新的在最后
    reports.sort()
    return os.path.join(reports_dir, reports[-1])

def view_report(report_file):
    """查看报告内容"""
    try:
        # 尝试使用UTF-8编码读取文件
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果UTF-8失败，尝试GBK编码
            with open(report_file, "r", encoding="gbk") as f:
                content = f.read()
        
        print("\n" + "=" * 40)
        print(f"正在查看: {report_file}")
        print("=" * 40)
        print(content)
        print("=" * 40 + "\n")
    except Exception as e:
        print(f"读取报告文件出错: {str(e)}")

def get_ai_investment_advice():
    """获取AI投资建议（使用DeepSeek R1模型）"""
    print("=== AI投资顾问 (DeepSeek R1) ===\n")
    
    # 检查是否存在整合后的数据
    data_file = "data/daily_data.json"
    if not os.path.exists(data_file):
        print("错误: 未找到整合后的数据文件，请先运行数据重组工具")
        input("\n按Enter键返回主菜单...")
        return

    # 修复数据文件，确保格式正确
    print("正在检查并修复数据文件格式...")
    if not fix_data_file(data_file):
        print("警告: 数据文件可能存在格式问题，但将继续尝试处理")

    # 初始化AI顾问
    advisor = DeepseekAdvisor()
    
    # 设置分析月数
    months = 6
    print(f"将分析最近{months}个月的数据")
    
    try:
        # 获取投资建议
        print("\n正在获取AI投资建议，请稍候...\n")
        advice = advisor.get_investment_advice(data_file, months)
        
        if advice:
            print("\n成功获取AI投资建议:")
            print("-" * 40)
            print(advice)
            print("-" * 40)
            
            print("\n投资建议已保存到'reports/ai_advice'目录")
        else:
            print("错误: 获取AI投资建议失败")
    
    except Exception as e:
        print(f"错误: {str(e)}")
    
    input("\n按Enter键返回主菜单...")

async def main():
    """主函数
    
    当无参数直接运行时:
    - 自动检查更新历史数据（当天有缓存则跳过）
    - 整合数据
    - 调用AI建议功能
    
    命令行参数:
    -f/--force: 强制更新历史数据
    -d/--decode: 运行AHR999数据获取工具
    -m/--menu: 显示交互式菜单界面
    -a/--ai: 只使用Deepseek R1 AI顾问(不更新数据)
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="加密货币监控系统 - 基于历史数据分析并提供买入/卖出建议")
    parser.add_argument("-f", "--force", action="store_true", help="强制更新历史数据")
    parser.add_argument("-d", "--decode", action="store_true", help="运行AHR999数据获取工具")
    parser.add_argument("-m", "--menu", action="store_true", help="显示交互式菜单界面")
    parser.add_argument("-a", "--ai", action="store_true", help="只使用Deepseek R1 AI顾问(不更新数据)")
    args = parser.parse_args()

    try:
        # 显示欢迎信息
        print("\n====== 加密货币监控系统 ======")
        print("支持分析: BTC价格、AHR999指数和恐惧贪婪指数")
        print("==============================\n")


        # 默认流程：更新数据+AI建议
        print("正在检查数据更新，请稍候...\n")
        
        # 1. 更新历史数据
        await generate_analysis_report(force_update=args.force)
        
        # 2. 整合数据
        try:
            data_dir = "data"
            input_file = os.path.join(data_dir, "historical_data.json")
            output_file = os.path.join(data_dir, "daily_data.json")
            
            # 确保数据目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 调用重组数据函数
            print("正在整合数据为按日期组织的格式...\n")
            success = reorganize_data(input_file, output_file)
            
            if success:
                print(f"数据整合成功！已生成按日期组织的数据文件: {output_file}")
                
                # 修复数据文件格式
                print("正在检查并修复数据文件格式...\n")
                fix_data_file(output_file)
                
                print(f"数据文件处理完成: {output_file}\n")
            else:
                print("数据整合失败，请检查日志获取详细信息\n")
                return 1
        except Exception as e:
            print(f"数据整合过程中出错: {str(e)}")
            logger.error(f"数据整合过程中出错: {str(e)}")
            return 1
        
        # 3. 调用AI建议
        print("正在生成AI投资建议...\n")
        get_ai_investment_advice()

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
