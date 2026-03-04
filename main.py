import os
import sys
import json
import asyncio
import logging
import argparse
import platform
from datetime import datetime

from webhook import send_message_async

src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.append(src_dir)

from config import DATA_DIRS
from src.utils.historical_data import HistoricalDataCollector
from src.utils.trend_analyzer import TrendAnalyzer
from src.utils.data_reorganizer import reorganize_data
from src.ai.advisor import DeepseekAdvisor

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
    mvrv_count = len(historical_data.get("mvrv", []))
    fg_count = len(historical_data.get("fear_greed", []))
    
    logger.info(f"获取到的历史数据: BTC价格({btc_count}条), MVRV比率({mvrv_count}条), 恐惧贪婪指数({fg_count}条)")
    
    # 初始化趋势分析器
    analyzer = TrendAnalyzer(historical_data)
    
    # 生成投资建议
    advice = analyzer.generate_investment_advice()
    
    if advice.get("status") == "error":
        logger.error(f"生成投资建议失败: {advice.get('message', '未知错误')}")
        return False
    
    # 获取格式化的输出结果
    report = advice.get("formatted_output", "")
    
    # 构建推送消息
    push_message = "🔔 BTC投资建议分析报告\n\n"
    push_message += f"{report}"
    
    # 推送消息
    await send_message_async(push_message)
    
    # 保存报告到文件
    report_file = f"{DATA_DIRS['reports']}/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"分析报告已保存到: {report_file}")
    
    # 打印报告
    print("\n" + report)
    
    return True, report_file

async def get_ai_investment_advice(debug_only=False):
    """获取AI投资建议（使用DeepSeek R1模型）
    
    Args:
        debug_only: 仅生成提示词用于调试，不调用AI接口
    """
    if debug_only:
        print("=== 调试模式: 仅生成提示词，不调用AI ===\n")
    else:
        print("=== AI投资顾问 (DeepSeek R1) ===\n")
    
    data_file = "data/daily_data.json"
    if not os.path.exists(data_file):
        print("错误: 未找到整合后的数据文件，请先运行数据重组工具")
        return
    
    months = 6
    print(f"将分析最近{months}个月的数据")
    
    if debug_only:
        from ai.prompt import get_investment_advice_template, prepare_investment_advice_params, save_prompt_for_debug
        from ai.deepseek import DeepseekAPI
        
        api = DeepseekAPI.__new__(DeepseekAPI)
        last_record, _ = api.load_latest_investment_record()
        last_advice = None
        if last_record:
            last_advice = last_record.get("advice_data") or None
            if last_advice:
                print(f"已加载上次建议: 仓位 {last_advice.get('position', 'N/A')}%")
            else:
                from ai.prompt import extract_json_from_text
                last_advice = extract_json_from_text(last_record.get("recommendation", ""))
        
        if not last_advice:
            print("无历史建议记录，将使用首次建仓参数")
        
        advisor = DeepseekAdvisor.__new__(DeepseekAdvisor)
        advisor.advice_dir = DATA_DIRS['advices']
        filtered_data = advisor._prepare_data_for_ai(data_file, months)
        if not filtered_data:
            print("错误: 准备数据失败")
            return
        
        data_json = json.dumps(filtered_data, ensure_ascii=False)
        params = prepare_investment_advice_params(last_advice=last_advice)
        prompt = get_investment_advice_template(**params, data_json=data_json)
        prompt_path = save_prompt_for_debug(prompt)
        
        mvrv_count = sum(1 for item in filtered_data if 'mvrv' in item)
        price_count = sum(1 for item in filtered_data if 'price' in item)
        fng_count = sum(1 for item in filtered_data if 'fear_greed_value' in item)
        
        print(f"\n{'='*50}")
        print(f"提示词诊断报告")
        print(f"{'='*50}")
        print(f"数据条目总数: {len(filtered_data)}")
        print(f"  有price字段: {price_count}")
        print(f"  有mvrv字段:  {mvrv_count}")
        print(f"  有fear_greed_value字段: {fng_count}")
        print(f"数据时间范围: {filtered_data[0].get('date','?')} ~ {filtered_data[-1].get('date','?')}")
        print(f"仓位状态: {params['last_position']}%")
        print(f"成本基础: {params['last_cost_basis']}")
        print(f"上次操作: {params['last_action']}")
        print(f"提示词字符数: {len(prompt)}")
        print(f"提示词包含MVRV说明: {'MVRV' in prompt}")
        print(f"提示词包含AHR999: {'ahr999' in prompt.lower()}")
        print(f"提示词文件: {prompt_path}")
        print(f"{'='*50}")
        
        print(f"\n最新3条数据:")
        for item in filtered_data[-3:]:
            print(f"  {item}")
        
        if mvrv_count == 0:
            print("\n⚠️  警告: 数据中没有mvrv字段! 请检查数据采集链路")
        if 'ahr999' in prompt.lower():
            print("⚠️  警告: 提示词中仍包含ahr999引用!")
        
        return
    
    advisor = DeepseekAdvisor()
    max_retries = 2
    retry_delay = 2.0
    
    try:
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                print("注意: 正在准备数据格式以供AI处理...")
                wrapped_data = {"responses": data}
                temp_file = data_file + ".temp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(wrapped_data, f, ensure_ascii=False, indent=2)
                data_file = temp_file
                print("数据格式已调整，继续处理...")
        except Exception as e:
            logger.warning(f"读取数据文件时出错: {str(e)}")
            print(f"警告: 读取数据文件时出错: {str(e)}，将继续尝试处理")
        
        print("\n正在获取AI投资建议，请稍候...\n")
        print(f"已配置最大重试次数: {max_retries}，重试间隔: {retry_delay}秒")
        
        advice = advisor.get_investment_advice(
            data_file=data_file, 
            months=months, 
            max_retries=max_retries, 
            retry_delay=retry_delay
        )
        
        if advice:
            print("\n成功获取AI投资建议:")
            print(advice)
            
            push_message = "🤖 AI投资顾问建议\n\n"
            push_message += f"{advice}"
            await send_message_async(push_message)
        else:
            print("错误: 获取AI投资建议失败")
            print("可能原因: API服务器连接问题、API密钥无效或请求超时")
            print("建议: 检查网络连接、API密钥设置和服务器状态")
    
    except KeyError as e:
        logger.error(f"AI投资建议处理过程中出现键错误: {str(e)}")
        print(f"错误: AI投资建议处理过程中缺少必要的数据键 '{str(e)}'")
        
        if str(e) == "'responses'":
            print("\n提示: DeepseekAdvisor需要'responses'字段。您的JSON数据结构可能需要调整。")
            print("建议格式: { \"responses\": [ ... 您的数据数组 ... ] }")
    
    except Exception as e:
        logger.error(f"AI投资建议处理过程中出错: {str(e)}")
        print(f"错误: {str(e)}")    
        print("尝试获取详细错误信息...")
        import traceback
        error_details = traceback.format_exc()
        logger.debug(error_details)
        print(f"错误详情已记录到日志文件")

async def update_and_reorganize_data():
    """执行数据采集和重组（步骤1+2），返回是否成功"""
    # 1. 更新历史数据
    try:
        await generate_analysis_report(force_update=False)
    except Exception as e:
        logger.error(f"生成分析报告时出错: {str(e)}")
        print(f"生成分析报告时出错: {str(e)}")
    
    # 2. 整合数据
    try:
        data_dir = DATA_DIRS['data']
        input_file = os.path.join(data_dir, "historical_data.json")
        output_file = os.path.join(data_dir, "daily_data.json")
        
        os.makedirs(data_dir, exist_ok=True)
        
        if not os.path.exists(input_file):
            logger.error(f"输入文件不存在: {input_file}")
            print(f"错误: 输入文件不存在: {input_file}")
            return False
        
        print("正在整合数据为按日期组织的格式...\n")
        success = reorganize_data(input_file, output_file)
        
        if success:
            print(f"数据整合成功！已生成按日期组织的数据文件: {output_file}")
            print(f"数据文件处理完成: {output_file}\n")
        else:
            print("数据整合失败，请检查日志获取详细信息\n")
        return success
    except Exception as e:
        print(f"数据整合过程中出错: {str(e)}")
        logger.error(f"数据整合过程中出错: {str(e)}")
        return False


async def main(debug_mode=False):
    """主函数
    
    Args:
        debug_mode: 调试模式，仅采集数据并生成提示词，不调用AI接口
    """
    try:
        print("\n====== 加密货币监控系统 ======")
        print("支持分析: BTC价格、MVRV比率和恐惧贪婪指数")
        if debug_mode:
            print("[调试模式] 仅生成提示词，不调用AI接口")
        
        print("正在检查数据更新，请稍候...\n")
        
        await update_and_reorganize_data()
        
        if debug_mode:
            await get_ai_investment_advice(debug_only=True)
        else:
            try:
                print("正在生成AI投资建议...\n")
                await get_ai_investment_advice()
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


def parse_args():
    parser = argparse.ArgumentParser(description='CryptoSentinel - BTC投资分析与AI顾问')
    parser.add_argument('--debug', action='store_true',
                        help='调试模式：执行数据采集和重组，生成提示词文件，但不调用AI接口')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    exit_code = asyncio.run(main(debug_mode=args.debug))
    sys.exit(exit_code)

