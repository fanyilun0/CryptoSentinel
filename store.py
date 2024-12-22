import json
from datetime import datetime, timedelta
import os

class DataStore:
    def __init__(self, file_path="data/market_data.txt", max_days=30):
        """
        初始化数据存储
        :param file_path: 数据文件路径
        :param max_days: 保留最近多少天的数据
        """
        self.file_path = file_path
        self.max_days = max_days
        self._data_cache = []  # 添加数据缓存
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 如果文件不存在则创建
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('')
        else:
            # 初始化时读取数据到缓存
            self._load_data()
    
    def _load_data(self):
        """从文件加载数据到缓存"""
        try:
            self._data_cache = []
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        self._data_cache.append(record)
                    except json.JSONDecodeError:
                        print(f"解析数据行失败: {line}")
                        continue
            print(f"成功加载 {len(self._data_cache)} 条历史数据")
        except Exception as e:
            print(f"加载数据失败: {str(e)}")
            self._data_cache = []

    def save_data(self, ethena_data, market_data):
        """保存新的数据记录"""
        print("\n准备保存新数据...")
        
        # 数据有效性检查
        if not any([ethena_data, market_data]):
            print("没有有效数据需要保存")
            return False
        
        try:
            current_time = datetime.now()
            data_record = {
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'ethena': ethena_data if ethena_data else {},
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
            
            # 打印保存的数据内容
            print("\n保存的数据内容:")
            print("="*50)
            print(f"时间: {data_record['timestamp']}")
            
            if ethena_data:
                print("\nEthena数据:")
                print(f"📈 协议收益率: {ethena_data['protocol_yield']:.2f}%")
                print(f"📊 质押收益率: {ethena_data['staking_yield']:.2f}%")
                print(f"💎 TVL: ${ethena_data['tvl']:,.2f}")
            
            if market_data:
                print("\nBTC数据:")
                if market_data.get('btc_price'):
                    print(f"💰 BTC价格: ${market_data['btc_price']:,.2f}")
                
                print("\n市场情绪数据:")
                if market_data.get('ahr999'):
                    print(f"📉 AHR999指数: {market_data['ahr999']:.4f}")
                if market_data.get('fear_greed'):
                    print(f"😱 恐慌贪婪指数: {market_data['fear_greed']}")
            print("="*50)
            
            # 追加到文件
            with open(self.file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data_record) + '\n')
            
            # 更新缓存
            self._data_cache.append(data_record)
            print("数据已成功保存到文件和缓存")
            return True
            
        except Exception as e:
            print(f"保存数据时出错: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return False

    def get_latest_data(self):
        """获取最新一条数据"""
        if self._data_cache:
            return self._data_cache[-1]
        return None

    def get_historical_data(self, days=7):
        """获取历史数据"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            record for record in self._data_cache
            if datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S') >= cutoff_date
        ]

    def _cleanup_old_data(self):
        """清理旧数据"""
        cutoff_date = datetime.now() - timedelta(days=self.max_days)
        
        # 过滤保留需要的数据
        filtered_data = [
            record for record in self._data_cache
            if datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S') >= cutoff_date
        ]
        
        # 更新文件
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                for record in filtered_data:
                    f.write(json.dumps(record) + '\n')
            
            # 更新缓存
            self._data_cache = filtered_data
            print(f"清理完成，保留 {len(filtered_data)} 条数据")
            
        except Exception as e:
            print(f"清理旧数据失败: {str(e)}")

    def get_yesterday_last_data(self):
        """获取昨天最后一条数据"""
        yesterday = datetime.now().date() - timedelta(days=1)
        yesterday_data = None
        
        for record in reversed(self._data_cache):
            try:
                record_time = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S')
                if record_time.date() == yesterday:
                    yesterday_data = record
                    break
            except Exception as e:
                print(f"处理数据时出错: {str(e)}")
                continue
        
        return yesterday_data

    def get_data_analysis(self):
        """
        获取数据分析结果
        """
        data = self.get_historical_data(days=7)  # 分析最近7天数据
        if not data:
            return None
            
        analysis = {
            'protocol_yield': {
                'current': None,
                'trend': None,
                'avg_7d': None
            },
            'tvl': {
                'current': None,
                'trend': None,
                'avg_7d': None
            }
        }
        
        # 提取数据进行分析
        try:
            # 获取最新数据
            latest = data[-1]['ethena']
            analysis['protocol_yield']['current'] = latest.get('protocol_yield')
            analysis['tvl']['current'] = latest.get('tvl')
            
            # 计算7天平均值
            protocol_yields = [d['ethena'].get('protocol_yield', 0) for d in data if 'ethena' in d]
            tvls = [d['ethena'].get('tvl', 0) for d in data if 'ethena' in d]
            
            if protocol_yields:
                analysis['protocol_yield']['avg_7d'] = sum(protocol_yields) / len(protocol_yields)
                analysis['protocol_yield']['trend'] = 'up' if latest.get('protocol_yield', 0) > analysis['protocol_yield']['avg_7d'] else 'down'
            
            if tvls:
                analysis['tvl']['avg_7d'] = sum(tvls) / len(tvls)
                analysis['tvl']['trend'] = 'up' if latest.get('tvl', 0) > analysis['tvl']['avg_7d'] else 'down'
                
        except Exception as e:
            print(f"据分析失败: {str(e)}")
            
        return analysis

    def calculate_changes(self, old_data, new_data):
        """计算数据变化"""
        if not old_data or not new_data:
            return None
        
        changes = {
            'ethena': {},
            'market': {
                'btc': {},
                'sentiment': {}
            }
        }
        
        # Ethena数据变化
        if 'ethena' in old_data and 'ethena' in new_data:
            old_ethena = old_data['ethena']
            new_ethena = new_data['ethena']
            
            for key in ['protocol_yield', 'staking_yield', 'tvl']:
                if key in old_ethena and key in new_ethena:
                    old_value = old_ethena[key]
                    new_value = new_ethena[key]
                    change_pct = ((new_value - old_value) / old_value * 100) if old_value != 0 else 0
                    
                    changes['ethena'][key] = {
                        'old': old_value,
                        'new': new_value,
                        'change_pct': change_pct,
                        'trend': '📈' if new_value > old_value else '📉' if new_value < old_value else '➡️'
                    }
        
        # BTC价格变化
        if ('market' in old_data and 'market' in new_data and
            'btc' in old_data['market'] and 'btc' in new_data['market']):
            old_btc = old_data['market']['btc'].get('price')
            new_btc = new_data['market']['btc'].get('price')
            
            if old_btc and new_btc:
                change_pct = ((new_btc - old_btc) / old_btc * 100)
                changes['market']['btc']['price'] = {
                    'old': old_btc,
                    'new': new_btc,
                    'change_pct': change_pct,
                    'trend': '📈' if new_btc > old_btc else '📉' if new_btc < old_btc else '➡️'
                }
        
        # 市场情绪数据变化
        if ('market' in old_data and 'market' in new_data and
            'sentiment' in old_data['market'] and 'sentiment' in new_data['market']):
            old_sentiment = old_data['market']['sentiment']
            new_sentiment = new_data['market']['sentiment']
            
            for key in ['ahr999', 'fear_greed']:
                if key in old_sentiment and key in new_sentiment:
                    old_value = old_sentiment[key]
                    new_value = new_sentiment[key]
                    if old_value and new_value:
                        change_pct = ((new_value - old_value) / old_value * 100) if old_value != 0 else 0
                        changes['market']['sentiment'][key] = {
                            'old': old_value,
                            'new': new_value,
                            'change_pct': change_pct,
                            'trend': '📈' if new_value > old_value else '📉' if new_value < old_value else '➡️'
                        }
        
        return changes
