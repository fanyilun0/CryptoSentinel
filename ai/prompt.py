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
from typing import Dict, Any, Optional

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
    return f"""你是我的个人比特币投资顾问，拥有专业的加密货币市场分析能力。请提供完整的市场分析和具体的投资建议。

今天的日期是: {current_date}

当前投资状态:
- 我的当前比特币仓位：{last_position}%
- 投资预算: 小额投资 (1000美元)
- 当前成本基础: {last_cost_basis}
- 风险偏好：中等（愿意承担合理波动，但需控制最大回撤不超过30%）

上次投资建议: {last_action}

请基于下列历史数据分析市场状况，并给出明确的操作建议：

以下是历史数据（JSON格式）：
{data_json}

请按照以下固定格式提供你的完整分析和建议：

一、市场状况简报（150字以内）
[简述当前市场所处周期阶段、关键价格点位、AHR999和恐惧贪婪指数，以及最重要的市场信号。严格限制在提供的数据范围内分析，不要提及链上数据或其他未提供的指标。]

二、本周操作建议
1. 仓位调整：[明确说明应增加/减少/维持多少百分比的仓位，精确到5%]
2. 入场/出场价位：[给出明确的价格区间或具体数值]
3. 止损设置：[明确的止损价格，以及止损后的行动计划]
4. 获利目标：[短期和中期的目标价格，达到后应采取的行动]

三、仓位变动追踪
上次建议：[简述上次的建议，如无历史记录则说明"首次建仓建议"]
本次建议：[新建议]
仓位变化：[计算如果执行建议后的仓位百分比变化]
成本基础：[如执行建议后的平均持仓成本]

四、风险警报
[列出1-2个基于提供数据可观察到的市场风险因素，每个50字以内，附带具体应对措施。不要提及监管风险、黑天鹅事件或未在数据中体现的风险。]

五、下周关注重点
[列出1-3个需要特别关注的指标或价格水平，每个30字以内，仅限于已提供数据中的指标]

六、结构化数据
在完成以上所有分析后，请在最后提供一个JSON格式的操作摘要，格式如下：
```json
{{
  "position": 数字,
  "action": "建仓/减仓/持有",
  "entry_price": "价格区间或具体数值",
  "stop_loss": 数字,
  "target_short": 数字,
  "target_mid": 数字,
  "cost_basis": 数字,
  "risks": ["风险1", "风险2"],
  "indicators": ["指标1", "指标2", "指标3"]
}}
```

重要提示：你必须首先提供完整的五个部分分析内容，然后才在最后提供JSON格式的操作摘要。不要只回复JSON数据，必须先提供完整分析。

操作记录ID：BTI-{current_date.replace('-', '')}
[请在回复的最后包含此ID]

免责声明：简短说明投资风险，限制在30字以内。"""

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

def save_prompt_for_debug(prompt: str, current_date: str, debug_dir: str = 'debug_prompts') -> str:
    """保存提示词到调试目录
    
    Args:
        prompt: 提示词内容
        current_date: 当前日期
        debug_dir: 调试目录路径
        
    Returns:
        保存的文件路径
    """
    os.makedirs(debug_dir, exist_ok=True)
    debug_file = os.path.join(debug_dir, f"prompt_{current_date.replace('-', '')}.txt")
    
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    logger.info(f"调试模式：已保存完整提示词到 {debug_file}")
    return debug_file

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