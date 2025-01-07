import asyncio
import aiohttp
from datetime import datetime, timedelta
import json
from store import DataStore
from config import (
    DEFILLAMA_API, 
    ETHENA_API, 
    MARKET_SENTIMENT, 
    WEBHOOK_URL,
    PROXY_URL,
    USE_PROXY,
    MONITOR_CONFIG,
    INTERVAL
)

async def fetch_data(session, url, params=None):
    """通用数据获取函数"""
    try:
        proxy = PROXY_URL if USE_PROXY else None
        async with session.get(url, params=params, proxy=proxy) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"请求失败: {url}, 状态码: {response.status}")
                return None
    except Exception as e:
        print(f"获取数据出错: {url}, 错误: {str(e)}")
        return None

async def get_ethena_data(session):
    """获取Ethena协议数据"""
    try:
        # 获取收益率数据
        yield_data = await fetch_data(session, ETHENA_API['yield_url'])
        
        # 获取TVL数据
        tvl_url = f"{DEFILLAMA_API['base_url']}{DEFILLAMA_API['ethena_endpoint']}"
        tvl_data = await fetch_data(session, tvl_url)
        
        if yield_data and tvl_data:
            return {
                'protocol_yield': yield_data['protocolYield']['value'],
                'staking_yield': yield_data['stakingYield']['value'],
                'tvl': tvl_data['tvl'][-1]['totalLiquidityUSD']
            }
    except Exception as e:
        print(f"获取Ethena数据出错: {str(e)}")
    return None

async def get_btc_price(session):
    """获取BTC当前价格"""
    try:
        price_data = await fetch_data(session, MARKET_SENTIMENT['btc_price_url'])
        if price_data and 'bpi' in price_data:
            return price_data['bpi']['USD']['rate_float']
    except Exception as e:
        print(f"获取BTC价格数据出错: {str(e)}")
    return None

async def get_market_sentiment(session):
    """获取市场情绪指标"""
    try:
        # 获取AHR999指数
        ahr999_data = await fetch_data(
            session, 
            MARKET_SENTIMENT['ahr999_url'], 
            MARKET_SENTIMENT['ahr999_params']
        )
        
        # 获取恐慌贪婪指数
        fear_greed_data = await fetch_data(session, MARKET_SENTIMENT['fear_greed_url'])
        
        # 获取BTC价格
        btc_price = await get_btc_price(session)
        
        # 更安全的数据提取方式
        ahr999_value = None
        fear_greed_value = None
        
        # 处理AHR999数据
        if ahr999_data and isinstance(ahr999_data, dict):
            try:
                if ('data' in ahr999_data and 
                    isinstance(ahr999_data['data'], list) and 
                    len(ahr999_data['data']) > 0):
                    # 获取最后一条记录的第二个值
                    ahr999_value = float(ahr999_data['data'][-1][1])
            except (ValueError, TypeError, IndexError) as e:
                print(f"处理AHR999数据时出错: {str(e)}")
                ahr999_value = None
        
        # 处理Fear & Greed数据
        if fear_greed_data and isinstance(fear_greed_data, dict):
            if 'data' in fear_greed_data and fear_greed_data['data']:
                try:
                    fear_greed_value = int(fear_greed_data['data'][0]['value'])
                except (ValueError, TypeError, KeyError, IndexError) as e:
                    print(f"处理Fear & Greed数据时出错: {str(e)}")
                    fear_greed_value = None
        
        return {
            'ahr999': ahr999_value,
            'fear_greed': fear_greed_value,
            'btc_price': btc_price
        }
    except Exception as e:
        print(f"获取市场情绪数据出错: {str(e)}")
        return None

def analyze_market_data(data):
    """分析市场数据并生成建议"""
    analysis = {
        'ahr999': None,
        'fear_greed': None
    }
    
    if not data:
        return analysis
    
    # AHR999分析
    if 'ahr999' in data:
        ahr999 = data['ahr999']
        if ahr999 < 0.45:
            analysis['ahr999'] = "💡 当前处于抄底区域，可以考虑买入"
        elif ahr999 < 1.2:
            analysis['ahr999'] = "💡 当前处于适合定投区域"
        else:
            analysis['ahr999'] = "💡 当前币价较高，需要谨慎"
    
    # 恐慌贪婪指数分析
    if 'fear_greed' in data:
        fear_greed = data['fear_greed']
        if fear_greed < 20:
            analysis['fear_greed'] = "💡 市场极度恐慌，可能是买入机会"
        elif fear_greed > 80:
            analysis['fear_greed'] = "💡 市场极度贪婪，注意风险"
    
    return analysis

def format_btc_price(price_data, is_change=False):
    """格式化BTC价格信息"""
    if not price_data:
        return []
    
    message_parts = []
    if is_change:
        trend = "📈" if price_data['change_pct'] > 0 else "📉"
        message_parts.append("💰 BTC价格变化:")
        message_parts.append(
            f"当前价格: ${price_data['new']:,.2f} {trend} ({price_data['change_pct']:+.2f}%)\n"
            f"上次价格: ${price_data['old']:,.2f}"
        )
    else:
        message_parts.append("💰 BTC市场状态:")
        message_parts.append(f"当前价格: ${price_data:,.2f}")
    
    message_parts.append("")
    return message_parts

def format_number_to_readable(number):
    """将大数字转换为易读格式（B/M）"""
    billion = 1_000_000_000
    million = 1_000_000
    
    if number >= billion:
        return f"${number/billion:.2f}B"
    elif number >= million:
        return f"${number/million:.2f}M"
    else:
        return f"${number:,.2f}"

def format_ethena_data(ethena_data, is_change=False):
    """格式化Ethena数据"""
    if not ethena_data:
        return []
    
    message_parts = []
    message_parts.append("💰 Ethena协议" + ("数据变化:" if is_change else "当前状态:"))
    
    if is_change:
        for key, ch in ethena_data.items():
            trend = "📈" if ch['change_pct'] > 0 else "📉"
            if key == 'protocol_yield':
                message_parts.append(
                    f"📈 协议收益率: {ch['old']:.2f}% ➡️ {ch['new']:.2f}% {trend} ({ch['change_pct']:+.2f}%)"
                )
            elif key == 'staking_yield':
                message_parts.append(
                    f"📊 质押收益率: {ch['old']:.2f}% ➡️ {ch['new']:.2f}% {trend} ({ch['change_pct']:+.2f}%)"
                )
            elif key == 'tvl':
                old_tvl = format_number_to_readable(ch['old'])
                new_tvl = format_number_to_readable(ch['new'])
                message_parts.append(
                    f"💎 TVL: {old_tvl} ➡️ {new_tvl} {trend} ({ch['change_pct']:+.2f}%)"
                )
    else:
        message_parts.append(f"📈 协议收益率: {ethena_data['protocol_yield']:.2f}%")
        message_parts.append(f"📊 质押收益率: {ethena_data['staking_yield']:.2f}%")
        message_parts.append(f"💎 TVL: {format_number_to_readable(ethena_data['tvl'])}")
    
    message_parts.append("")
    return message_parts

def format_sentiment_data(sentiment_data, analysis, is_change=False):
    """格式化市场情绪数据"""
    if not sentiment_data:
        return []
    
    message_parts = []
    message_parts.append("🎯 市场情绪指标" + ("变化:" if is_change else ":"))
    
    if is_change:
        if 'ahr999' in sentiment_data:
            ch = sentiment_data['ahr999']
            trend = "📈" if ch['new'] > ch['old'] else "📉"
            message_parts.append(
                f"📉 AHR999指数: {ch['old']:.2f} ➡️ {ch['new']:.2f} {trend}"
            )
            if analysis['ahr999']:
                message_parts.append(analysis['ahr999'])
        
        if 'fear_greed' in sentiment_data:
            ch = sentiment_data['fear_greed']
            trend = "📈" if ch['new'] > ch['old'] else "📉"
            message_parts.append(
                f"😱 恐慌贪婪指数: {ch['old']} ➡️ {ch['new']} {trend}"
            )
            if analysis['fear_greed']:
                message_parts.append(analysis['fear_greed'])
    else:
        message_parts.append(f"AHR999指数: {sentiment_data['ahr999']:.4f}")
        if analysis['ahr999']:
            message_parts.append(analysis['ahr999'])
        
        message_parts.append(f"恐慌贪婪指数: {sentiment_data['fear_greed']}")
        if analysis['fear_greed']:
            message_parts.append(analysis['fear_greed'])
    
    message_parts.append("")
    return message_parts

def generate_monitor_message(ethena_data, market_data, data_store=None, is_first_run=False):
    """生成监控消息
    
    Args:
        ethena_data: Ethena协议数据
        market_data: 市场数据
        data_store: 数据存储对象,用于计算变化(可选)
        is_first_run: 是否为首次运行(默认False)
    """
    now = datetime.now()
    next_update = now + timedelta(seconds=INTERVAL)
    
    # 计算数据变化(如果不是首次运行且提供了data_store)
    changes = None
    if not is_first_run and data_store:
        previous_data = data_store.get_last_data()
        current_data = {
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
            'ethena': ethena_data,
            'market': {
                'btc': {
                    'price': market_data.get('btc_price')
                },
                'sentiment': {
                    'ahr999': market_data.get('ahr999'),
                    'fear_greed': market_data.get('fear_greed')
                }
            }
        }
        changes = data_store.calculate_changes(previous_data, current_data)
    
    # 生成市场分析
    analysis = analyze_market_data({
        'ahr999': market_data.get('ahr999'),
        'fear_greed': market_data.get('fear_greed')
    })
    
    # 构建消息
    message_parts = [
        f"📊 【{'市场监控初始化报告' if is_first_run else '每日市场监控报告'}】",
        f"🕐 时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"⏰ 下次更新时间: {next_update.strftime('%Y-%m-%d %H:%M:%S')}"
    ]
    
    # BTC价格信息
    if changes and 'market' in changes and 'btc' in changes['market']:
        btc_changes = changes['market']['btc']
        if 'price' in btc_changes:
            message_parts.extend(format_btc_price(btc_changes['price'], True))
    elif market_data and market_data.get('btc_price'):
        message_parts.extend(format_btc_price(market_data['btc_price']))
    
    # Ethena数据
    if changes and 'ethena' in changes:
        message_parts.extend(format_ethena_data(changes['ethena'], True))
    elif ethena_data:
        message_parts.extend(format_ethena_data(ethena_data))
    
    # 市场情绪数据
    if changes and 'market' in changes and 'sentiment' in changes['market']:
        message_parts.extend(format_sentiment_data(
            changes['market']['sentiment'], 
            analysis, 
            True
        ))
    elif market_data:
        sentiment_data = {
            'ahr999': market_data.get('ahr999'),
            'fear_greed': market_data.get('fear_greed')
        }
        message_parts.extend(format_sentiment_data(sentiment_data, analysis))
    
    return "\n".join(message_parts)

async def send_message_async(message_content):
    """发送消息到webhook"""
    # 打印消息内容
    print("\n发送的消息内容:")
    print("="*50)
    print(message_content)
    print("="*50)
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "msgtype": "text",
        "text": {
            "content": message_content
        }
    }
    
    proxy = PROXY_URL if USE_PROXY else None
    async with aiohttp.ClientSession() as session:
        async with session.post(WEBHOOK_URL, json=payload, headers=headers, proxy=proxy) as response:
            if response.status == 200:
                print("消息发送成功!")
            else:
                print(f"消息发送失败: {response.status}, {await response.text()}")

async def daily_monitor():
    """每日监控主函数"""
    print("启动每日市场监控...")
    data_store = DataStore()
    last_update_time = None
    
    while True:
        try:
            current_time = datetime.now()
            
            # 检查是否需���更新
            if last_update_time:
                time_diff = (current_time - last_update_time).total_seconds()
                if time_diff < INTERVAL:
                    await asyncio.sleep(1)
                    continue
            
            print(f"\n开始新一轮数据获取... {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            async with aiohttp.ClientSession() as session:
                # 获取数据
                print("正在获取Ethena数据...")
                ethena_data = await get_ethena_data(session)
                if ethena_data:
                    print(f"成功获取Ethena数据: {json.dumps(ethena_data, indent=2)}")
                else:
                    print("获取Ethena数据失败")
                    continue
                
                print("\n正在获取市场情绪数据...")
                sentiment_data = await get_market_sentiment(session)
                if sentiment_data:
                    print(f"成功获取市场情绪数据: {json.dumps(sentiment_data, indent=2)}")
                else:
                    print("获取市场情绪数据失败")
                    continue
                
                # 获取上次的数据
                previous_data = data_store.get_last_data()

                # 生成消��
                if previous_data:
                    print("生成数据对比消息...")
                    message = generate_monitor_message(
                        ethena_data, 
                        sentiment_data,
                        data_store=data_store
                    )
                else:
                    print("首次运行，生成初始状态消息...")
                    message = generate_monitor_message(
                            ethena_data,
                            sentiment_data,
                            is_first_run=True
                        )
                    
                # 发送消息
                if message:
                    await send_message_async(message)
                
                # 保存新数据
                if data_store.save_data(ethena_data, sentiment_data):
                    print("\n数据保存成功")
                    
                else:
                    print("数据保存失败")
                
                last_update_time = current_time
                
        except Exception as e:
            print(f"监控过程出错: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
        
        print(f"\n等待{INTERVAL}秒后进行下一轮检查...")
        await asyncio.sleep(1)

if __name__ == "__main__":
    print("正在始化监控程序...")
    asyncio.run(daily_monitor()) 
