"""
提示词生成模块 - 为DeepSeek API提供各种场景的提示词模板

此模块负责:
1. 定义和管理各种提示词模板
2. 根据输入参数生成格式化的提示词
3. 提供通用的提示词工具函数
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

# 导入配置
from config import DATA_DIRS

# 设置日志
logger = logging.getLogger(__name__)

def get_investment_advice_template(current_date: str, last_position: int = 0, 
                                  last_cost_basis: str = "尚未建仓", 
                                  last_action: str = "首次建仓建议", 
                                  data_json: str = "", 
                                  total_budget: float = 1000.0) -> str:
    """生成投资建议的提示词模板
    
    Args:
        current_date: 当前日期
        last_position: 上次仓位百分比
        last_cost_basis: 上次成本基础
        last_action: 上次操作描述
        data_json: 市场数据JSON
        total_budget: 总投资预算（美元）
        
    Returns:
        格式化后的提示词模板
    """
    # 计算当前已投资金额
    current_invested = (last_position / 100) * total_budget
    available_cash = total_budget - current_invested
    
    return f"""你是我的专业比特币投资顾问，拥有深厚的加密货币市场分析经验和严谨的风险管理能力。请基于当前市场数据({current_date})提供完整的分析和具体可执行的投资建议。

# TL;DR (核心摘要)
请在开头提供50字以内的核心摘要，包含：
- 当前市场状态：【牛市/熊市/震荡市】
- 投资决策：【加仓/减仓/满仓/清仓/持有】
- 关键理由：【主要支撑原因】

当前投资组合状态:
- 总投资预算：${total_budget:.0f}
- 当前比特币仓位：{last_position}% (已投资${current_invested:.0f})
- 可用现金：${available_cash:.0f}
- 当前成本基础: {last_cost_basis}
- 风险偏好：中等（愿意承担合理波动，但需控制最大回撤不超过30%）
- 投资周期：中长期（6-18个月）

上次投资建议: {last_action}

请基于以下历史数据分析市场状况，并给出明确的操作建议：

以下是历史市场数据（JSON格式，按日期从旧到新排列）：
{data_json}

**数据说明**：提供的历史数据按照时间顺序从旧到新排列，第一条是最早的数据，最后一条是最新的数据。

请按照以下结构提供全面分析和精确建议：

## 一、市场周期分析
（150字以内）
[分析当前市场周期位置（积累期/上升期/分配期/下跌期），关键支撑阻力位，AHR999指标和恐惧贪婪指数的意义，以及市场情绪状态。明确判断当前处于牛市还是熊市阶段。仅使用提供的数据进行分析。]

## 二、技术指标解读
1. 价格趋势：[分析BTC近期价格趋势、均线系统状态、成交量变化]
2. 市场估值：[解读当前AHR999和恐惧贪婪指数的含义，以及处于历史什么水平]
3. 周期阶段：[结合现有数据判断当前所处的市场周期阶段，牛熊转换信号]

## 三、投资决策建议
1. 仓位调整：[明确使用"加仓/减仓/满仓/清仓/持有"等关键字，说明调整的具体百分比和金额，精确到5%]
2. 入场/出场价位：[给出明确的价格区间，包括理想入场点和分批建仓/减仓区间]
3. 止损设置：[明确的止损价格，以及止损后的重新入场条件]
4. 获利目标：[短期（1-3个月）和中期（3-6个月）的目标价格，达到后的策略]

## 四、仓位管理追踪与利润计算
上次建议：{last_action}
本次建议：[新建议的核心内容，使用标准决策关键字]
仓位变化：[执行建议后的仓位百分比变化，从{last_position}%变为多少]

资金分配：
- 当前已投资：${current_invested:.0f} ({last_position}%)
- 本次操作金额：$XXX
- 操作后已投资：$XXX (XX%)
- 剩余可用现金：$XXX

成本基础计算：
- 当前成本基础：{last_cost_basis}
- 新交易价格：$XXX
- 操作后平均成本：$XXX

预期收益计算：
- 短期目标收益：$XXX (+XX%)
- 中期目标收益：$XXX (+XX%)
- 总投资组合收益率：XX%

## 五、风险分析
[列出2-3个基于提供数据观察到的市场风险因素，每个50字以内，附带具体应对措施]
1. [主要风险1及应对策略]
2. [主要风险2及应对策略]
3. [可选风险3及应对策略]

## 六、未来观察指标
[列出3个需要特别关注的指标或价格水平，每个带有明确的临界值和触发条件，以及触发后应采取的具体行动建议]
1. [关键指标1：临界值、意义和触发后的行动]
2. [关键指标2：临界值、意义和触发后的行动]
3. [关键指标3：临界值、意义和触发后的行动]

## 七、结构化决策数据
```json
{{
  "date": "{current_date}",
  "market_state": "牛市/熊市/震荡市",
  "decision_keyword": "加仓/减仓/满仓/清仓/持有",
  "position": 数字,
  "position_change": "增加/减少/维持X%",
  "action": "建仓/减仓/持有/清仓",
  "entry_price": "价格区间或具体数值",
  "stop_loss": 数字,
  "target_short": 数字,
  "target_mid": 数字,
  "cost_basis": 数字,
  "portfolio": {{
    "total_budget": {total_budget},
    "current_invested": 数字,
    "available_cash": 数字,
    "operation_amount": 数字
  }},
  "profit_calculation": {{
    "short_term_profit": 数字,
    "mid_term_profit": 数字,
    "short_term_return_pct": "百分比",
    "mid_term_return_pct": "百分比",
    "portfolio_return_pct": "百分比"
  }},
  "market_cycle": "积累期/上升期/分配期/下跌期",
  "risks": ["风险1", "风险2", "风险3"],
  "key_levels": ["水平1", "水平2", "水平3"]
}}
```

**重要格式要求**：
1. 必须严格按照上述Markdown格式输出，使用"## 一、"、"## 二、"等作为子标题
2. **禁止**在回复中使用"---"分隔符或其他横线分隔符
3. 必须在开头提供TL;DR摘要，明确牛熊状态和决策关键字
4. 必须先提供详细的六个部分分析内容，然后才提供JSON格式的决策数据
5. 仓位调整必须使用标准关键字：加仓/减仓/满仓/清仓/持有
6. 所有金额计算基于总投资预算${total_budget:.0f}
7. 提供具体的利润计算，包括美元金额和百分比
8. 所有建议必须基于已提供的数据，不要引用未提供的指标或信息
9. 给出具体可执行的策略而非模糊建议
10. 考虑当前持仓状态和成本基础做出建议
11. 提供明确的数值和百分比，避免模糊表述
12. 确保每个风险因素都有相应的应对策略
13. 所有历史数据比较需具体说明数值和时间点
14. 历史数据是按时间从旧到新排列的，最后一条是最新数据
"""

def prepare_investment_advice_params(current_date: Optional[str] = None, 
                                   last_advice: Optional[Dict] = None,
                                   total_budget: float = 1000.0) -> Dict[str, Any]:
    """准备投资建议的参数
    
    Args:
        current_date: 当前日期，如果为None则使用当前日期
        last_advice: 上次建议的JSON数据，如果为None则使用默认值
        total_budget: 总投资预算
        
    Returns:
        包含所有参数的字典
    """
    if not current_date:
        current_date = datetime.now().strftime('%Y-%m-%d')
    
    # 默认参数
    params = {
        "current_date": current_date,
        "last_position": 0,
        "last_cost_basis": "尚未建仓",
        "last_action": "首次建仓建议",
        "total_budget": total_budget
    }
    
    # 如果有上次建议，更新参数
    if last_advice:
        params["last_position"] = last_advice.get("position", 0)
        params["last_cost_basis"] = last_advice.get("cost_basis", "尚未建仓")
        
        # 获取上次的决策关键字
        last_decision = last_advice.get("decision_keyword", "建仓")
        last_entry_price = last_advice.get("entry_price", "N/A")
        last_stop_loss = last_advice.get("stop_loss", "N/A")
        
        params["last_action"] = f"{last_decision}至{params['last_position']}%，入场价位{last_entry_price}，止损价位{last_stop_loss}"
    
    return params

def calculate_portfolio_metrics(current_position: int, current_cost_basis: float,
                              new_position: int, new_price: float,
                              total_budget: float = 1000.0) -> Dict[str, Any]:
    """计算投资组合指标
    
    Args:
        current_position: 当前仓位百分比
        current_cost_basis: 当前成本基础
        new_position: 新仓位百分比
        new_price: 新交易价格
        total_budget: 总预算
        
    Returns:
        包含投资组合计算结果的字典
    """
    current_invested = (current_position / 100) * total_budget
    new_invested = (new_position / 100) * total_budget
    operation_amount = new_invested - current_invested
    
    # 计算新的平均成本
    if new_position > 0:
        if current_position > 0:
            # 加仓情况：计算加权平均成本
            total_btc_old = current_invested / current_cost_basis if current_cost_basis > 0 else 0
            total_btc_new = abs(operation_amount) / new_price if operation_amount != 0 else 0
            
            if operation_amount > 0:  # 加仓
                new_cost_basis = (current_invested + abs(operation_amount)) / (total_btc_old + total_btc_new)
            else:  # 减仓
                new_cost_basis = current_cost_basis  # 成本基础不变
        else:
            # 首次建仓
            new_cost_basis = new_price
    else:
        new_cost_basis = 0
    
    return {
        "current_invested": current_invested,
        "new_invested": new_invested,
        "operation_amount": operation_amount,
        "available_cash": total_budget - new_invested,
        "new_cost_basis": new_cost_basis,
        "operation_type": "加仓" if operation_amount > 0 else "减仓" if operation_amount < 0 else "持有"
    }

def save_prompt_for_debug(prompt: str) -> str:
    """保存提示词到文件用于调试
    
    Args:
        prompt: 提示词文本
        
    Returns:
        保存的文件路径
    """
        
    # 确保调试目录存在
    prompts_dir = DATA_DIRS['prompts']
    os.makedirs(prompts_dir, exist_ok=True)
    
    # 创建文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"prompt_{timestamp}.txt"
    
    # 保存到提示词目录
    prompt_path = os.path.join(prompts_dir, filename)
    
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    logger.info(f"已保存提示词到: {prompt_path}")
    return prompt_path

def extract_json_from_text(text: str) -> Optional[Dict]:
    """从文本中提取JSON数据
    
    Args:
        text: 包含JSON的文本
        
    Returns:
        解析后的JSON字典，如果解析失败则返回None
    """
    import re
    import json
    
    json_match = re.search(r'```json\s*({[\s\S]*?})\s*```', text)
    if not json_match:
        return None
        
    try:
        json_str = json_match.group(1)
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"解析JSON失败: {str(e)}")
        return None 