"""
AI模块 - 提供基于大模型的分析和建议功能

此模块包含:
1. DeepSeek API接口
2. 提示词生成功能
3. 投资建议生成功能
"""

# 导出主要类供外部使用
from ai.deepseek import DeepseekAPI
from ai.advisor import DeepseekAdvisor

# 定义包的公共接口
__all__ = [
    'DeepseekAPI',
    'DeepseekAdvisor',
] 