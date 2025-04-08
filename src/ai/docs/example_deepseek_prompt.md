# Example Deepseek R1 Prompt for Crypto Investment Analysis

This is an example of the prompt template used when calling the Deepseek R1 model for cryptocurrency investment advice based on historical data.

```
你是一位专业的加密货币投资顾问，擅长分析比特币市场和提供投资建议。
我会提供过去几个月的BTC价格、AHR999指数和恐惧贪婪指数数据，请基于这些数据为我提供详细的投资分析和建议。

今天的日期是: 2025-04-07

请考虑以下因素：
1. BTC价格趋势、支撑位和阻力位
2. AHR999指数，它是衡量比特币价值的指标：
   - <0.45: 极度低估
   - 0.45-0.75: 低估
   - 0.75-1.0: 价值区间下限
   - 1.0-1.25: 价值区间上限
   - 1.25-1.5: 高估
   - >1.5: 极度高估
3. 恐惧贪婪指数及其分类（Extreme Fear, Fear, Neutral, Greed, Extreme Greed）
4. 市场周期的阶段判断
5. 近期的重要价格变动和波动性

请提供以下内容：
1. 市场状况摘要和当前所处周期阶段
2. 技术分析（包括趋势、支撑/阻力位和关键指标）
3. 情绪分析（基于AHR999和恐惧贪婪指数）
4. 短期（1-4周）、中期（1-3个月）和长期（3-6个月）的价格预测
5. 针对不同类型投资者的详细投资策略建议：
   a. 保守型投资者
   b. 平衡型投资者
   c. 激进型投资者
6. 风险因素和需要关注的关键事件
7. 总结你对当前是应该买入、持有还是卖出的最终建议及理由

以下是历史数据（JSON格式）：
[
  {
    "date": "2024-10-07",
    "btc_price": 61453.28,
    "ahr999": 0.5521,
    "fear_greed": 55,
    "fear_greed_classification": "Greed"
  },
  {
    "date": "2024-10-08",
    "btc_price": 62786.43,
    "ahr999": 0.5732,
    "fear_greed": 58,
    "fear_greed_classification": "Greed"
  },
  ...
  {
    "date": "2025-04-06",
    "btc_price": 78430.0,
    "ahr999": 0.7603,
    "fear_greed": 34,
    "fear_greed_classification": "Fear"
  },
  {
    "date": "2025-04-07",
    "btc_price": 76877.98,
    "ahr999": 0.6603,
    "fear_greed": 23,
    "fear_greed_classification": "Extreme Fear"
  }
]

请注意，你的建议将被用于真实的投资决策，请务必全面分析，提供详尽、平衡的建议，并强调可能的风险。
```

## API Call Configuration

When making the API call, the following parameters are used:

* **Model**: `deepseek-reasoner`
* **Temperature**: 0.3 (for more deterministic responses)
* **Max Tokens**: 4000 (allows for comprehensive analysis)

## Example Output Structure

The model's response typically includes:

1. Market status summary and cycle stage assessment
2. Technical analysis of BTC price trends
3. Sentiment analysis based on AHR999 and Fear & Greed indices
4. Price predictions for short, medium, and long term
5. Investment strategies for different investor types
6. Risk factors and key events to monitor
7. Final buy/hold/sell recommendation with reasoning

## Usage

This prompt is used by the `DeepseekAdvisor` class in the `utils/ai_advisor.py` module, which:
1. Loads reorganized historical data 
2. Formats it into JSON
3. Integrates it into this prompt
4. Calls the Deepseek R1 API
5. Saves and returns the generated investment advice 