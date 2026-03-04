# BTC每日监控指标分析与AI投资建议

基于历史数据分析BTC价格、MVRV比率和恐惧贪婪指数，提供买入/卖出建议。

## 功能特点

- ✅ 获取并保存BTC价格历史数据（支持代理配置）
- ✅ 获取并解析MVRV（已实现市值比率）历史数据
- ✅ 获取恐惧与贪婪指数历史数据
- ✅ 基于6个月历史数据分析市场趋势
- ✅ 综合多项指标生成投资建议报告
- ✅ 提供用户友好的菜单界面
- ✅ 按日期整合多个数据源为统一JSON格式
- ✅ 使用Deepseek R1 AI模型提供高级投资分析建议

## 系统要求

- Python 3.7+
- 互联网连接（用于获取最新数据）
- 如果需要使用代理，请确保配置正确
- 使用AI顾问功能需要Deepseek API密钥

## 安装

1. 克隆本仓库：

```bash
git clone https://github.com/yourusername/CryptoSentinel.git
cd CryptoSentinel
```

2. 安装依赖包：

```bash
pip install -r requirements.txt
```

3. (可选) 设置Deepseek API密钥：

```bash
# Linux/macOS
export DEEPSEEK_API_KEY=your_api_key_here

# Windows (CMD)
set DEEPSEEK_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:DEEPSEEK_API_KEY="your_api_key_here"
```

## 使用方法

### 通过菜单界面使用（推荐）

运行以下命令启动菜单界面：

```bash
python main.py -m
```

在菜单中选择相应的功能：

1. **生成分析报告**：使用缓存的历史数据生成分析报告
2. **更新数据并生成分析报告**：强制更新所有历史数据并生成报告
3. **运行MVRV数据获取工具**：专门用于获取MVRV历史数据
4. **查看最新报告**：查看最近一次生成的分析报告
5. **使用AI顾问**：使用Deepseek R1模型获取高级投资建议
6. **退出程序**

### 通过命令行直接使用

```bash
# 生成分析报告（使用缓存数据）
python main.py

# 强制更新数据并生成分析报告
python main.py --force

# 运行MVRV数据获取工具
python main.py --decode

# 使用AI顾问获取投资建议
python main.py --ai

# 使用专用的AI顾问工具（更多选项）
python ai_advisor_cli.py
```

### AI顾问专用工具

AI顾问命令行工具提供了更多选项：

```bash
python ai_advisor_cli.py --help
```

常用选项：
- `-k/--api-key` - 指定Deepseek API密钥
- `-m/--months` - 设置要分析的月数（默认：6）
- `-v/--view` - 在终端显示完整AI建议
- `-s/--skip-reorganize` - 跳过数据重组步骤，直接使用现有的按日期整合数据

## 数据来源

- BTC价格：Binance API
- MVRV比率：CoinMetrics Community API (免费，无需API Key)
- 恐惧与贪婪指数：Alternative.me API

## 分析指标说明

### BTC价格分析

- 当前价格与7/30/90日均价比较
- 价格变化百分比（1日/7日/30日）
- 价格波动率（7日/30日）
- 价格趋势方向（7日/30日）
- RSI指标（14日）
- 支撑位和阻力位预估
- 价格历史百分位

### MVRV比率分析

MVRV（Market Value to Realized Value）是比特币市场市值与已实现市值的比率，反映全网持有者的平均未实现盈亏水平，可作为市场估值的参考维度之一。

- 当前值与7/30日均值比较
- 变化百分比（1日/7日/30日）
- 趋势方向（7日/30日）
- 市场估值状态参考

### 恐惧与贪婪指数分析

恐惧与贪婪指数是一个0-100的指标，代表市场情绪：

- 0-24：极度恐惧
- 25-49：恐惧
- 50：中性
- 51-74：贪婪
- 75-100：极度贪婪

分析包括：
- 当前值与7/30日均值比较
- 指数变化（1日/7日/30日）
- 趋势方向（7日/30日）
- 市场情绪变化评估

## 投资建议生成

系统提供两种投资建议：

### 1. 传统技术分析

基于以下因素综合生成投资建议：

- 基于价格趋势的建议
- 基于MVRV比率的建议
- 基于恐惧与贪婪指数的建议

每项建议都附带置信度评估（低/中/中高/高），最终建议将综合考量所有因素。

### 2. AI驱动的高级分析

使用Deepseek R1大型语言模型提供的深度分析，包括：

- 市场状况摘要和当前所处周期阶段
- 详细技术分析（趋势、支撑/阻力位和关键指标）
- 估值与情绪分析（基于MVRV比率和恐惧贪婪指数）
- 短期、中期和长期的价格预测
- 针对不同类型投资者的详细投资策略建议
- 风险因素和需要关注的关键事件
- 最终买入/持有/卖出建议及理由

## 数据整合

系统可以将多个数据源（BTC价格、MVRV比率和恐惧贪婪指数）按日期整合到一个统一的JSON文件中，便于分析和使用其他工具处理。

```bash
# 使用数据整合功能
python reorganize_data.py
```

## 代理设置

如果需要通过代理访问API，请在`historical_data.py`文件中修改以下代码：

```python
# 修改为你的代理地址
self.proxy = "http://127.0.0.1:7890"
```

## 注意事项

- 本系统仅提供技术分析参考，不构成投资建议
- 加密货币市场风险较大，请谨慎投资
- API可能会有访问限制，请合理控制请求频率
- 使用AI顾问功能需要Deepseek API密钥，请确保API密钥可用

## 许可证

MIT License 