#!/usr/bin/env python
"""
AI投资顾问命令行工具 - 使用DeepSeek R1模型获取加密货币投资建议

此工具可以:
1. 将BTC价格、AHR999指数和恐惧贪婪指数数据按日期整合到一个JSON文件中
2. 调用DeepSeek R1模型，使用整合后的数据获取投资建议
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# 导入AI顾问模块
from ai.advisor import DeepseekAdvisor

# 添加对数据重组器的导入
try:
    from utils.data_reorganizer import reorganize_data
except ImportError:
    # 如果找不到，尝试直接导入
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.data_reorganizer import reorganize_data

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('crypto_ai_advisor.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AI加密货币投资顾问")
    
    parser.add_argument("-k", "--api-key", 
                       help="DeepSeek API密钥 (也可通过环境变量DEEPSEEK_API_KEY设置)")
    
    parser.add_argument("-u", "--api-url", 
                       help="DeepSeek API URL (也可通过环境变量DEEPSEEK_API_URL设置)")
    
    parser.add_argument("-i", "--input-file", default="data/historical_data.json",
                       help="历史数据文件路径 (默认: data/historical_data.json)")
    
    parser.add_argument("-o", "--output-file", default="data/daily_data.json",
                       help="按日期整合的数据输出文件路径 (默认: data/daily_data.json)")
    
    parser.add_argument("-m", "--months", type=int, default=6,
                       help="分析的月数 (默认: 6)")
    
    parser.add_argument("-v", "--view", action="store_true",
                       help="在屏幕上显示生成的建议")
    
    parser.add_argument("-s", "--skip-reorganize", action="store_true",
                       help="跳过数据重组步骤，直接使用现有的按日期整合数据")
    
    parser.add_argument("--report-dir", default="reports/ai_advice",
                       help="AI建议报告保存目录 (默认: reports/ai_advice)")
    
    parser.add_argument("--offline", action="store_true",
                       help="离线模式：不调用实际API，仅保存提示词到本地")
    
    parser.add_argument("--prompts-dir", default="prompts",
                       help="离线模式下保存提示词的目录 (默认: prompts)")
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    # 设置API密钥环境变量（如果提供了）
    if args.api_key:
        os.environ["DEEPSEEK_API_KEY"] = args.api_key
    
    # 设置API URL环境变量（如果提供了）
    if args.api_url:
        os.environ["DEEPSEEK_API_URL"] = args.api_url
    
    # 设置离线模式环境变量
    if args.offline:
        os.environ["DEEPSEEK_OFFLINE_MODE"] = "true"
        # 确保提示词目录存在
        os.makedirs(args.prompts_dir, exist_ok=True)
    
    print("\n===== AI加密货币投资顾问 =====")
    print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    if args.offline:
        print(f"运行模式: 离线 (提示词将保存到: {args.prompts_dir})")
    else:
        print("运行模式: 在线 (将调用DeepSeek API)")
    
    # 步骤1: 按日期整合数据
    if not args.skip_reorganize:
        print("\n步骤1: 正在按日期整合BTC价格、AHR999和恐惧贪婪指数数据...")
        
        if not os.path.exists(args.input_file):
            print(f"错误: 历史数据文件不存在: {args.input_file}")
            print("请先收集历史数据，或指定正确的数据文件路径")
            return 1
        
        success = reorganize_data(args.input_file, args.output_file)
        if not success:
            print("错误: 数据整合失败，请检查日志获取详细信息")
            return 1
        
        print(f"数据已按日期整合并保存到: {args.output_file}")
    else:
        print("\n已跳过数据重组步骤，将使用现有的按日期整合数据")
        if not os.path.exists(args.output_file):
            print(f"错误: 按日期整合的数据文件不存在: {args.output_file}")
            print("请先运行数据整合步骤，或指定正确的数据文件路径")
            return 1
    
    # 步骤2: 调用DeepSeek R1获取投资建议
    print("\n步骤2: 正在" + ("准备" if args.offline else "调用") + " DeepSeek R1模型获取投资建议...")
    
    # 确保报告目录存在
    os.makedirs(args.report_dir, exist_ok=True)
    
    # 初始化AI顾问
    advisor = DeepseekAdvisor(offline_mode=args.offline)
    
    # 在非离线模式下检查API密钥
    if not args.offline and not os.environ.get("DEEPSEEK_API_KEY"):
        print("警告: 未设置DeepSeek API密钥")
        print("请通过-k/--api-key参数或设置环境变量DEEPSEEK_API_KEY提供API密钥")
        return 1
    
    # 获取投资建议
    advice = advisor.get_investment_advice(args.output_file, args.months)
    if not advice:
        print("错误: 获取投资建议失败，请检查日志获取详细信息")
        return 1
    
    # 打印建议
    if args.view:
        print("\n===== DeepSeek R1投资建议 =====")
        print(advice)
        print("===============================\n")
    else:
        if args.offline:
            print("\n提示词已成功保存")
            print(f"提示词目录: {args.prompts_dir}")
        else:
            print("\n投资建议已生成并保存到报告文件")
            print(f"报告目录: {args.report_dir}")
        print("使用 -v/--view 参数可在终端查看内容")
    
    print("\n处理完成!\n")
    return 0

if __name__ == "__main__":
    """程序入口"""
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        import traceback
        logger.exception("异常详情:")
        sys.exit(1) 