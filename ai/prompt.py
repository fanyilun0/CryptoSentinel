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
                                  data_json: str = "") -> str:
    """生成投资建议的提示词模板
    
    Args:
        current_date: 当前日期
        last_position: 上次仓位百分比
        last_cost_basis: 上次成本基础
        last_action: 上次操作描述
        data_json: 市场数据JSON
        
    Returns:
        格式化后的提示词模板
    """
    return f"""你是我的专业比特币投资顾问，拥有深厚的加密货币市场分析经验和严谨的风险管理能力。请基于当前市场数据({current_date})提供完整的分析和具体可执行的投资建议。

当前投资状态:
- 当前比特币仓位：{last_position}%
- 投资预算: 小额投资 (1000美元)
- 当前成本基础: {last_cost_basis}
- 风险偏好：中等（愿意承担合理波动，但需控制最大回撤不超过30%）
- 投资周期：中长期（6-18个月）

上次投资建议: {last_action}

请基于以下历史数据分析市场状况，并给出明确的操作建议：

以下是历史市场数据（JSON格式）：
{data_json}

请按照以下结构提供全面分析和精确建议：

一、市场周期分析（150字以内）
[分析当前市场周期位置（积累期/上升期/分配期/下跌期），关键支撑阻力位，AHR999指标和恐惧贪婪指数的意义，以及市场情绪状态。仅使用提供的数据进行分析。]

二、技术指标解读
1. 价格趋势：[分析BTC近期价格趋势、均线系统状态、成交量变化]
2. 市场估值：[解读当前AHR999和恐惧贪婪指数的含义，以及处于历史什么水平]
3. 周期阶段：[结合现有数据判断当前所处的市场周期阶段]

三、投资决策建议
1. 仓位调整：[明确说明应增加/减少/维持多少百分比的仓位，精确到5%]
2. 入场/出场价位：[给出明确的价格区间，包括理想入场点和分批建仓/减仓区间]
3. 止损设置：[明确的止损价格，以及止损后的重新入场条件]
4. 获利目标：[短期（1-3个月）和中期（3-6个月）的目标价格，达到后的策略]

四、仓位管理追踪
上次建议：{last_action}
本次建议：[新建议的核心内容]
仓位变化：[执行建议后的仓位百分比变化，从{last_position}%变为多少]
新成本基础：[如执行建议后的平均持仓成本计算]
预期回报率：[基于目标价格的潜在回报率]

五、风险分析
[列出2-3个基于提供数据观察到的市场风险因素，每个50字以内，附带具体应对措施]
1. [主要风险1及应对策略]
2. [主要风险2及应对策略]
3. [可选风险3及应对策略]

六、未来观察指标
[列出3个需要特别关注的指标或价格水平，每个带有明确的临界值和触发条件，以及触发后应采取的具体行动建议]
1. [关键指标1：临界值、意义和触发后的行动]
2. [关键指标2：临界值、意义和触发后的行动]
3. [关键指标3：临界值、意义和触发后的行动]

七、结构化决策数据
```json
{{
  "date": "{current_date}",
  "position": 数字,
  "position_change": "增加/减少/维持X%",
  "action": "建仓/减仓/持有",
  "entry_price": "价格区间或具体数值",
  "stop_loss": 数字,
  "target_short": 数字,
  "target_mid": 数字,
  "cost_basis": 数字,
  "expected_return": "百分比",
  "market_cycle": "积累期/上升期/分配期/下跌期",
  "risks": ["风险1", "风险2", "风险3"],
  "key_levels": ["水平1", "水平2", "水平3"]
}}
```

重要提示：
1. 必须先提供详细的六个部分分析内容，然后才提供JSON格式的决策数据
2. 所有建议必须基于已提供的数据，不要引用未提供的指标或信息
3. 给出具体可执行的策略而非模糊建议
4. 考虑当前持仓状态和成本基础做出建议
5. 提供明确的数值和百分比，避免模糊表述
6. 确保每个风险因素都有相应的应对策略
7. 所有历史数据比较需具体说明数值和时间点
"""

def prepare_investment_advice_params(current_date: Optional[str] = None, last_advice: Optional[Dict] = None) -> Dict[str, Any]:
    """准备投资建议的参数
    
    Args:
        current_date: 当前日期，如果为None则使用当前日期
        last_advice: 上次建议的JSON数据，如果为None则使用默认值
        
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
        "last_action": "首次建仓建议"
    }
    
    # 如果有上次建议，更新参数
    if last_advice:
        params["last_position"] = last_advice.get("position", 0)
        params["last_cost_basis"] = last_advice.get("cost_basis", "尚未建仓")
        last_entry_price = last_advice.get("entry_price", "N/A")
        last_stop_loss = last_advice.get("stop_loss", "N/A")
        params["last_action"] = f"调整仓位至{params['last_position']}%，入场价位{last_entry_price}，止损价位{last_stop_loss}"
    
    return params

def save_prompt_for_debug(prompt: str, current_date: str = None) -> str:
    """保存提示词到文件用于调试
    
    Args:
        prompt: 提示词文本
        current_date: 当前日期，用于文件名
        
    Returns:
        保存的文件路径
    """
    if current_date is None:
        current_date = datetime.now().strftime('%Y-%m-%d')
        
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