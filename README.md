# 🔍 加密货币市场监控系统

一个基于Python的自动化加密货币市场监控系统，用于实时跟踪BTC价格、Ethena协议数据和市场情绪指标的变化。

## 📑 目录

- [功能特性](#功能特性)
- [安装说明](#安装说明)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [监控指标](#监控指标)
- [开发说明](#开发说明)
- [注意事项](#注意事项)
- [许可证](#许可证)

## ✨ 功能特性

- 🔄 自动定时监控市场数据
- 📊 多维度数据分析
    - BTC价格追踪
    - Ethena协议数据(TVL、收益率)
    - 市场情绪指标(AHR999、恐慌贪婪指数)
- 📱 实时监控报告推送
- 📈 数据变化分析和投资建议
- 💾 数据持久化存储
- 🔧 支持代理配置

## 🚀 安装说明

1. 克隆仓库:
    ```bash
    git clone https://github.com/yourusername/crypto-market-monitor.git
    cd crypto-market-monitor
    ```

2. 安装依赖:
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ 配置说明

在`config.py`中配置以下参数:

```python
# API配置
DEFILLAMA_API = {
    "base_url": "https://api.defillama.com",
    "ethena_endpoint": "/protocol/xxx"
}

ETHENA_API = {
    "yield_url": "https://api.ethena.com/yield"
}

MARKET_SENTIMENT = {
    "ahr999_url": "https://api.xxx/ahr999",
    "fear_greed_url": "https://api.xxx/fng"
}

# 代理配置(可选)
USE_PROXY = False
PROXY_URL = "http://your-proxy:port"

# 监控间隔(秒)
INTERVAL = 3600
```

配置.env文件
```
WEBHOOK_URL=your_webhook_url
```

## 📖 使用方法

1. 配置完成后，直接运行:
    ```bash
    python main.py
    ```

2. 程序会自动:
    - 定期获取市场数据
    - 分析数据变化
    - 推送监控报告

## 📊 监控指标

### BTC价格监控
- 实时价格追踪
- 价格变化百分比
- 趋势分析

### Ethena协议数据
| 指标 | 说明 |
|------|------|
| 协议收益率 | 当前协议整体收益率 |
| 质押收益率 | 用户质押收益率 |
| TVL | 总锁仓价值 |

### 市场情绪指标

#### AHR999指数
- < 0.45: 抄底区域
- 0.45-1.2: 定投区域
- > 1.2: 谨慎区域

#### 恐慌贪婪指数
- 0-20: 极度恐慌
- 20-40: 恐慌
- 40-60: 中性
- 60-80: 贪婪
- 80-100: 极度贪婪

## 🔧 开发说明

### 技术特点
- 异步编程(asyncio + aiohttp)提高性能
- 模块化设计便于扩展
- 完善的错误处理机制
- 数据持久化存储
- 灵活的代理配置

### 代码示例

监控数据获取:
```python
async def get_market_data():
    async with aiohttp.ClientSession() as session:
        btc_price = await get_btc_price(session)
        ethena_data = await get_ethena_data(session)
        sentiment = await get_market_sentiment(session)
    return btc_price, ethena_data, sentiment
```

## ⚠️ 注意事项

1. **API配置**
    - 确保所有API地址正确
    - 注意API访问频率限制

2. **Webhook配置**
    - webhook URL必须配置正确
    - 测试webhook连接是否正常

3. **代理使用**
    - 建议使用代理提高稳定性
    - 确保代理服务器可用

4. **数据存储**
    - 确保存储路径有写入权限
    - 定期清理历史数据

## 📄 许可证

MIT License
