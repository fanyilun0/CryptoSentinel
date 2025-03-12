import json
import os
from datetime import datetime

class DataStore:
    def __init__(self):
        """初始化数据存储"""
        self.data_file = "data/last_data.json"
        self.history_file = "data/history.txt"  # 新增历史记录文件
        print(f"\n初始化数据存储...")
        print(f"数据文件路径: {os.path.abspath(self.data_file)}")
        print(f"历史记录文件路径: {os.path.abspath(self.history_file)}")
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        try:
            data_dir = os.path.dirname(self.data_file)
            if not os.path.exists(data_dir):
                print(f"创建数据目录: {data_dir}")
                os.makedirs(data_dir)
            else:
                print(f"数据目录已存在: {data_dir}")
        except Exception as e:
            print(f"创建数据目录出错: {str(e)}")
    
    def get_last_data(self):
        """获取上次数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    if self.validate_data(data):
                        print(f"获取到上次数据: {data['timestamp']}")
                        return data
            print("没有历史数据")
            return None
        except Exception as e:
            print(f"获取上次数据出错: {str(e)}")
            return None
    
    def save_data(self, ethena_data, market_data):
        """保存新数据"""
        try:
            print("\n准备保存新数据...")
            
            # 构建数据结构
            data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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
            
            # 打印保存的数据
            print("\n保存的数据内容:")
            print("="*50)
            print(f"时间: {data['timestamp']}\n")
            
            # 打印Ethena数据
            if data['ethena']:
                print("Ethena数据:")
                print(f"📈 协议收益率: {data['ethena']['protocol_yield']:.2f}%")
                print(f"📊 质押收益率: {data['ethena']['staking_yield']:.2f}%")
                print(f"💎 TVL: ${data['ethena']['tvl']:,.2f}\n")
            else:
                print("Ethena数据: 无\n")
            
            # 打印BTC数据
            if data['market']['btc']['price'] is not None:
                print("BTC数据:")
                print(f"💰 BTC价格: ${data['market']['btc']['price']:,.2f}\n")
            else:
                print("BTC数据: 无\n")
            
            # 打印市场情绪数据
            print("市场情绪数据:")
            if data['market']['sentiment']['ahr999'] is not None:
                print(f"📉 AHR999指数: {data['market']['sentiment']['ahr999']:.4f}")
            else:
                print("📉 AHR999指数: 无")
                
            if data['market']['sentiment']['fear_greed'] is not None:
                print(f"😱 恐慌贪婪指数: {data['market']['sentiment']['fear_greed']}")
            else:
                print("😱 恐慌贪婪指数: 无")
            print("="*50)
            
            # 保存到JSON文件
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # 保存到历史记录文件
            self.save_to_history_file(data)
            
            print("数据已成功保存\n")
            return True
        except Exception as e:
            print(f"保存数据出错: {str(e)}")
            return False
    
    def save_to_history_file(self, data):
        """将数据保存到历史记录文件，在文件最前方插入一条记录"""
        try:
            # 格式化数据为易读的文本格式
            timestamp = data['timestamp']
            record_lines = [
                f"===== {timestamp} ====="
            ]
            
            # BTC数据
            if data['market']['btc']['price'] is not None:
                record_lines.append(f"BTC: ${data['market']['btc']['price']:,.0f}")
            else:
                record_lines.append("BTC: 无数据")
            
            # Ethena数据
            if data['ethena']:
                record_lines.append(f"Ethena协议收益: {data['ethena']['protocol_yield']:.2f}%")
                record_lines.append(f"Ethena质押收益: {data['ethena']['staking_yield']:.2f}%")
                record_lines.append(f"Ethena TVL: ${data['ethena']['tvl']:,.0f}")
            else:
                record_lines.append("Ethena: 无数据")
            
            # 市场情绪数据
            if data['market']['sentiment']['ahr999'] is not None:
                record_lines.append(f"AHR999: {data['market']['sentiment']['ahr999']:.2f}")
            else:
                record_lines.append("AHR999: 无数据")
            
            if data['market']['sentiment']['fear_greed'] is not None:
                record_lines.append(f"恐慌贪婪: {data['market']['sentiment']['fear_greed']}")
            else:
                record_lines.append("恐慌贪婪: 无数据")
            
            record_lines.append("=" * 30)
            record_text = "\n".join(record_lines) + "\n\n"
            
            # 读取现有文件内容
            existing_content = ""
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # 将新记录插入到文件最前方
            with open(self.history_file, 'w', encoding='utf-8') as f:
                f.write(record_text + existing_content)
            
            print(f"历史记录已保存到: {self.history_file}")
            return True
        except Exception as e:
            print(f"保存历史记录出错: {str(e)}")
            return False
    
    def validate_data(self, data):
        """验证数据格式"""
        try:
            required_fields = {
                'timestamp': str,
                'ethena': dict,
                'market': dict
            }
            
            for field, field_type in required_fields.items():
                if field not in data:
                    print(f"缺少必需字段: {field}")
                    return False
                if not isinstance(data[field], field_type):
                    print(f"字段类型错误 {field}: 期望 {field_type}, 实际 {type(data[field])}")
                    return False
            return True
        except Exception as e:
            print(f"验证数据格式出错: {str(e)}")
            return False
    
    def calculate_changes(self, old_data, new_data):
        """计算数据变化"""
        if not old_data:
            return None
        
        changes = {}
        
        # 计算Ethena数据变化
        if 'ethena' in old_data and 'ethena' in new_data:
            ethena_changes = {}
            for key in ['protocol_yield', 'staking_yield', 'tvl']:
                if key in old_data['ethena'] and key in new_data['ethena']:
                    old_val = float(old_data['ethena'][key])
                    new_val = float(new_data['ethena'][key])
                    change_pct = ((new_val - old_val) / old_val) * 100
                    ethena_changes[key] = {
                        'old': old_val,
                        'new': new_val,
                        'change_pct': change_pct
                    }
            if ethena_changes:
                changes['ethena'] = ethena_changes
        
        # 计算市场数据变化
        if 'market' in old_data and 'market' in new_data:
            market_changes = {}
            
            # BTC价格变化
            if ('btc' in old_data['market'] and 'btc' in new_data['market'] and
                'price' in old_data['market']['btc'] and 'price' in new_data['market']['btc'] and
                old_data['market']['btc']['price'] is not None and new_data['market']['btc']['price'] is not None):
                old_price = float(old_data['market']['btc']['price'])
                new_price = float(new_data['market']['btc']['price'])
                change_pct = ((new_price - old_price) / old_price) * 100
                market_changes['btc'] = {
                    'price': {
                        'old': old_price,
                        'new': new_price,
                        'change_pct': change_pct
                    }
                }
            
            # 情绪指标变化
            if 'sentiment' in old_data['market'] and 'sentiment' in new_data['market']:
                sentiment_changes = {}
                for key in ['ahr999', 'fear_greed']:
                    if (key in old_data['market']['sentiment'] and 
                        key in new_data['market']['sentiment'] and
                        old_data['market']['sentiment'][key] is not None and 
                        new_data['market']['sentiment'][key] is not None):
                        old_val = float(old_data['market']['sentiment'][key])
                        new_val = float(new_data['market']['sentiment'][key])
                        sentiment_changes[key] = {
                            'old': old_val,
                            'new': new_val
                        }
                if sentiment_changes:
                    market_changes['sentiment'] = sentiment_changes
            
            if market_changes:
                changes['market'] = market_changes
        
        return changes if changes else None
