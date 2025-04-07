import json
import os
from datetime import datetime

# 创建records目录（如果不存在）
records_dir = 'investment_records'
os.makedirs(records_dir, exist_ok=True)

# AI回复内容
ai_response = """一、市场状况简报

当前比特币价格76,877美元，AHR999指数0.66（接近历史低位），恐惧贪婪指数23（极端恐惧）。市场处于深度回调阶段，价格较2024年11月峰值（106,058美元）回撤27.5%。关键支撑位75,000美元已反复测试，若失守可能触发恐慌抛售。AHR999低于0.8显示超卖，但未达历史极端抄底区间（0.45以下）。

二、本周操作建议

仓位调整：建仓25%（250美元）
入场/出场价位：75,000-78,000美元区间分批买入
止损设置：严格止损53,814美元（-30%回撤线），触发后暂停操作等待市场企稳
获利目标：
短期：86,000美元（前低反弹位），达目标减持50%
中期：90,000美元（心理阻力位），全部平仓
三、仓位变动追踪

上次建议：首次建仓建议

本次建议：新建25%仓位

仓位变化：0% → 25%

成本基础：约76,500美元（按区间中值计算）

四、风险警报

流动性风险：当前恐惧指数23接近2025-02-25极端值（25），若AHR999跌破0.45可能引发踩踏。应对：仅用预算25%试仓，保留75%备用资金。
假性反弹风险：3月多次反弹受阻88,000美元。应对：突破83,000美元前不加仓。
五、下周关注重点

AHR999能否回升至0.75以上
恐惧贪婪指数突破40中性阈值
日线收盘价是否站稳78,000美元

```json
{
  "position": 25,
  "action": "建仓",
  "entry_price": "75000-78000",
  "stop_loss": 53814,
  "target_short": 86000,
  "target_mid": 90000,
  "cost_basis": 76500,
  "risks": ["AHR999继续下探", "反弹动能不足"],
  "indicators": ["AHR999", "恐惧贪婪指数", "78000阻力位"]
}
```

操作记录ID：BTI-20250407

免责声明：加密货币波动剧烈，本金可能部分或全部损失。"""

# 解析JSON部分
import re
advice_data = {}
json_match = re.search(r'```json\s*({[\s\S]*?})\s*```', ai_response)
if json_match:
    try:
        advice_json = json_match.group(1)
        advice_data = json.loads(advice_json)
    except json.JSONDecodeError as e:
        print(f"解析JSON失败: {str(e)}")

# 创建记录
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
record_id = "BTI-20250407"  # 使用AI提供的ID

record = {
    "id": record_id,
    "timestamp": timestamp,
    "date": datetime.now().strftime('%Y-%m-%d'),
    "recommendation": ai_response,
    "advice_data": advice_data
}

# 保存到文件
filename = f"{record_id}.json"
filepath = os.path.join(records_dir, filename)

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(record, f, ensure_ascii=False, indent=2)

print(f"已保存投资建议记录: {filepath}")