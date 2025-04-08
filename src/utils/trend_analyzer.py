import os
import json
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """趋势分析器 - 分析历史数据并提供买入/卖出建议"""
    
    def __init__(self, historical_data=None):
        """初始化趋势分析器"""
        self.historical_data = historical_data
        self.analysis_period = 180  # 分析最近180天（约6个月）的数据
    
    def set_historical_data(self, historical_data):
        """设置历史数据"""
        self.historical_data = historical_data
    
    def analyze_btc_price_trend(self):
        """分析BTC价格趋势"""
        logger.info("分析BTC价格趋势...")
        
        if not self.historical_data or "btc_price" not in self.historical_data:
            logger.error("没有BTC价格历史数据可供分析")
            return {
                "status": "error",
                "message": "没有BTC价格历史数据可供分析"
            }
        
        # 获取最近6个月的BTC价格数据
        btc_data = self.historical_data["btc_price"]
        
        # 确保数据按日期降序排序（最新的在前面）
        btc_data = sorted(btc_data, key=lambda x: x.get("timestamp", 0), reverse=True)
        
        # 限制为最近的分析期数据
        btc_data = btc_data[:self.analysis_period]
        
        if not btc_data:
            logger.error("BTC价格数据为空")
            return {
                "status": "error",
                "message": "BTC价格数据为空"
            }
        
        # 提取价格数据
        prices = [item.get("price", 0) for item in btc_data if "price" in item]
        dates = [item.get("date", "") for item in btc_data if "date" in item]
        
        if len(prices) < 7:
            logger.error("BTC价格数据不足，至少需要7天数据")
            return {
                "status": "error",
                "message": f"BTC价格数据不足，只有{len(prices)}天，至少需要7天数据"
            }
        
        # 计算当前价格和各周期平均价格
        current_price = prices[0]
        avg_7d = np.mean(prices[:7]) if len(prices) >= 7 else None
        avg_30d = np.mean(prices[:30]) if len(prices) >= 30 else None
        avg_90d = np.mean(prices[:90]) if len(prices) >= 90 else None
        
        # 计算价格变化百分比
        price_change_1d = ((current_price / prices[1]) - 1) * 100 if len(prices) > 1 else 0
        price_change_7d = ((current_price / prices[6]) - 1) * 100 if len(prices) > 6 else 0
        price_change_30d = ((current_price / prices[29]) - 1) * 100 if len(prices) > 29 else 0
        
        # 计算波动率（价格的标准差 / 平均值）
        volatility_7d = (np.std(prices[:7]) / np.mean(prices[:7]) * 100) if len(prices) >= 7 else 0
        volatility_30d = (np.std(prices[:30]) / np.mean(prices[:30]) * 100) if len(prices) >= 30 else 0
        
        # 确定趋势方向
        trend_7d = "上涨" if price_change_7d > 0 else "下跌"
        trend_30d = "上涨" if price_change_30d > 0 else "下跌"
        
        # 计算RSI指标（14天）
        rsi = self._calculate_rsi(prices, 14) if len(prices) >= 14 else None
        
        # 计算价格处于历史百分位
        min_price = min(prices)
        max_price = max(prices)
        price_percentile = ((current_price - min_price) / (max_price - min_price) * 100) if max_price > min_price else 50
        
        # 判断支撑位和阻力位
        # 这里使用简化的方法，实际中可能需要更复杂的算法
        recent_lows = sorted(prices[:30])[:5]  # 最近30天的最低5个价格
        recent_highs = sorted(prices[:30], reverse=True)[:5]  # 最近30天的最高5个价格
        
        support_level = sum(recent_lows) / len(recent_lows)
        resistance_level = sum(recent_highs) / len(recent_highs)
        
        return {
            "status": "success",
            "current_price": current_price,
            "avg_7d": avg_7d,
            "avg_30d": avg_30d,
            "avg_90d": avg_90d,
            "price_change_1d": price_change_1d,
            "price_change_7d": price_change_7d,
            "price_change_30d": price_change_30d,
            "volatility_7d": volatility_7d,
            "volatility_30d": volatility_30d,
            "trend_7d": trend_7d,
            "trend_30d": trend_30d,
            "rsi_14d": rsi,
            "price_percentile": price_percentile,
            "support_level": support_level,
            "resistance_level": resistance_level,
            "latest_date": dates[0] if dates else None
        }
    
    def analyze_sentiment_trends(self):
        """分析AHR999和恐惧贪婪指数趋势"""
        logger.info("分析市场情绪指标趋势...")
        
        if not self.historical_data:
            logger.error("没有历史数据可供分析")
            return {
                "status": "error",
                "message": "没有历史数据可供分析"
            }
        
        # 分析AHR999指数
        ahr999_analysis = self._analyze_ahr999()
        
        # 分析恐惧与贪婪指数
        fear_greed_analysis = self._analyze_fear_greed()
        
        # 合并分析结果
        return {
            "status": "success" if ahr999_analysis["status"] == "success" or fear_greed_analysis["status"] == "success" else "error",
            "ahr999": ahr999_analysis,
            "fear_greed": fear_greed_analysis
        }
    
    def _analyze_ahr999(self):
        """分析AHR999指数"""
        if not self.historical_data or "ahr999" not in self.historical_data:
            logger.error("没有AHR999指数历史数据可供分析")
            return {
                "status": "error",
                "message": "没有AHR999指数历史数据可供分析"
            }
        
        # 获取AHR999指数数据
        ahr_data = self.historical_data["ahr999"]
        
        # 确保数据按日期降序排序（最新的在前面）
        ahr_data = sorted(ahr_data, key=lambda x: x.get("timestamp", 0), reverse=True)
        
        # 限制为最近的分析期数据
        ahr_data = ahr_data[:self.analysis_period]
        
        if not ahr_data:
            logger.error("AHR999指数数据为空")
            return {
                "status": "error",
                "message": "AHR999指数数据为空"
            }
        
        # 提取AHR999值
        ahr_values = [item.get("ahr999", 0) for item in ahr_data if "ahr999" in item]
        dates = [item.get("date", "") for item in ahr_data if "date" in item]
        
        if len(ahr_values) < 7:
            logger.error(f"AHR999指数数据不足，只有{len(ahr_values)}天，至少需要7天数据")
            return {
                "status": "error",
                "message": f"AHR999指数数据不足，只有{len(ahr_values)}天，至少需要7天数据"
            }
        
        # 计算当前AHR999值和各周期平均值
        current_ahr = ahr_values[0]
        avg_7d = np.mean(ahr_values[:7]) if len(ahr_values) >= 7 else None
        avg_30d = np.mean(ahr_values[:30]) if len(ahr_values) >= 30 else None
        
        # 计算AHR999变化百分比
        ahr_change_1d = ((current_ahr / ahr_values[1]) - 1) * 100 if len(ahr_values) > 1 else 0
        ahr_change_7d = ((current_ahr / ahr_values[6]) - 1) * 100 if len(ahr_values) > 6 else 0
        ahr_change_30d = ((current_ahr / ahr_values[29]) - 1) * 100 if len(ahr_values) > 29 else 0
        
        # 确定趋势方向
        trend_7d = "上涨" if ahr_change_7d > 0 else "下跌"
        trend_30d = "上涨" if ahr_change_30d > 0 else "下跌"
        
        # 计算AHR999处于历史百分位
        min_ahr = min(ahr_values)
        max_ahr = max(ahr_values)
        ahr_percentile = ((current_ahr - min_ahr) / (max_ahr - min_ahr) * 100) if max_ahr > min_ahr else 50
        
        # 根据AHR999值判断市场状态
        market_state = "未知"
        if current_ahr < 0.45:
            market_state = "极度低估"
        elif current_ahr < 0.75:
            market_state = "低估"
        elif current_ahr < 1.0:
            market_state = "价值区间下限"
        elif current_ahr < 1.25:
            market_state = "价值区间上限"
        elif current_ahr < 1.5:
            market_state = "高估"
        else:
            market_state = "极度高估"
        
        return {
            "status": "success",
            "current_value": current_ahr,
            "avg_7d": avg_7d,
            "avg_30d": avg_30d,
            "change_1d": ahr_change_1d,
            "change_7d": ahr_change_7d,
            "change_30d": ahr_change_30d,
            "trend_7d": trend_7d,
            "trend_30d": trend_30d,
            "percentile": ahr_percentile,
            "market_state": market_state,
            "latest_date": dates[0] if dates else None
        }
    
    def _analyze_fear_greed(self):
        """分析恐惧与贪婪指数"""
        if not self.historical_data or "fear_greed" not in self.historical_data:
            logger.error("没有恐惧与贪婪指数历史数据可供分析")
            return {
                "status": "error",
                "message": "没有恐惧与贪婪指数历史数据可供分析"
            }
        
        # 获取恐惧与贪婪指数数据
        fg_data = self.historical_data["fear_greed"]
        
        # 确保数据按日期降序排序（最新的在前面）
        fg_data = sorted(fg_data, key=lambda x: x.get("timestamp", 0), reverse=True)
        
        # 限制为最近的分析期数据
        fg_data = fg_data[:self.analysis_period]
        
        if not fg_data:
            logger.error("恐惧与贪婪指数数据为空")
            return {
                "status": "error",
                "message": "恐惧与贪婪指数数据为空"
            }
        
        # 提取恐惧与贪婪指数值
        fg_values = [item.get("value", 0) for item in fg_data if "value" in item]
        fg_classes = [item.get("value_classification", "") for item in fg_data if "value_classification" in item]
        dates = [item.get("date", "") for item in fg_data if "date" in item]
        
        if len(fg_values) < 7:
            logger.error(f"恐惧与贪婪指数数据不足，只有{len(fg_values)}天，至少需要7天数据")
            return {
                "status": "error",
                "message": f"恐惧与贪婪指数数据不足，只有{len(fg_values)}天，至少需要7天数据"
            }
        
        # 计算当前值和各周期平均值
        current_fg = fg_values[0]
        current_class = fg_classes[0] if fg_classes else "未知"
        avg_7d = np.mean(fg_values[:7]) if len(fg_values) >= 7 else None
        avg_30d = np.mean(fg_values[:30]) if len(fg_values) >= 30 else None
        
        # 计算变化
        fg_change_1d = current_fg - fg_values[1] if len(fg_values) > 1 else 0
        fg_change_7d = current_fg - fg_values[6] if len(fg_values) > 6 else 0
        fg_change_30d = current_fg - fg_values[29] if len(fg_values) > 29 else 0
        
        # 确定趋势方向
        trend_7d = "上涨" if fg_change_7d > 0 else "下跌"
        trend_30d = "上涨" if fg_change_30d > 0 else "下跌"
        
        # 市场状态解释
        market_mood = current_class
        
        # 计算市场情绪变化
        if fg_change_7d > 10:
            mood_change = "情绪明显好转"
        elif fg_change_7d > 5:
            mood_change = "情绪略有好转"
        elif fg_change_7d < -10:
            mood_change = "情绪明显恶化"
        elif fg_change_7d < -5:
            mood_change = "情绪略有恶化"
        else:
            mood_change = "情绪相对稳定"
        
        return {
            "status": "success",
            "current_value": current_fg,
            "current_class": current_class,
            "avg_7d": avg_7d,
            "avg_30d": avg_30d,
            "change_1d": fg_change_1d,
            "change_7d": fg_change_7d,
            "change_30d": fg_change_30d,
            "trend_7d": trend_7d,
            "trend_30d": trend_30d,
            "market_mood": market_mood,
            "mood_change": mood_change,
            "latest_date": dates[0] if dates else None
        }
    
    def _calculate_rsi(self, prices, window=14):
        """计算相对强弱指数 (RSI)"""
        if len(prices) < window + 1:
            return None
        
        # 计算价格变化
        deltas = np.diff(prices[::-1])
        
        # 计算收益和损失
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # 计算初始平均值
        avg_gain = np.mean(gains[:window])
        avg_loss = np.mean(losses[:window])
        
        # 如果没有损失，RSI = 100
        if avg_loss == 0:
            return 100
        
        # 计算相对强度
        rs = avg_gain / avg_loss
        
        # 计算RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_investment_advice(self):
        """生成投资建议"""
        logger.info("生成投资建议...")
        
        # 分析BTC价格趋势
        price_analysis = self.analyze_btc_price_trend()
        if price_analysis["status"] == "error":
            return {
                "status": "error",
                "message": f"无法生成投资建议: {price_analysis['message']}"
            }
        
        # 分析市场情绪指标
        sentiment_analysis = self.analyze_sentiment_trends()
        if sentiment_analysis["status"] == "error":
            logger.warning("市场情绪分析失败，仅基于价格分析生成建议")
        
        # 根据价格趋势生成初步建议
        advice = {
            "status": "success",
            "price_based": self._get_price_based_advice(price_analysis),
            "formatted_output": ""
        }
        
        # 如果有情绪分析数据，则添加相应的建议
        if sentiment_analysis["status"] == "success":
            if "ahr999" in sentiment_analysis and sentiment_analysis["ahr999"]["status"] == "success":
                advice["ahr999_based"] = self._get_ahr999_based_advice(sentiment_analysis["ahr999"])
            
            if "fear_greed" in sentiment_analysis and sentiment_analysis["fear_greed"]["status"] == "success":
                advice["fear_greed_based"] = self._get_fear_greed_based_advice(sentiment_analysis["fear_greed"])
        
        # 综合分析，给出最终建议
        advice["overall"] = self._get_overall_advice(advice)
        
        # 格式化输出
        advice["formatted_output"] = self._format_advice_output(price_analysis, sentiment_analysis, advice)
        
        return advice
    
    def _get_price_based_advice(self, price_analysis):
        """基于价格分析生成建议"""
        current_price = price_analysis["current_price"]
        
        # 基于价格趋势的建议
        if price_analysis["trend_30d"] == "上涨" and price_analysis["trend_7d"] == "上涨":
            if price_analysis["price_change_7d"] > 10:
                return {
                    "action": "观望或小幅减仓",
                    "reason": "短期内价格快速上涨，可能面临回调风险",
                    "confidence": "中"
                }
            else:
                return {
                    "action": "持有",
                    "reason": "价格保持稳定上涨趋势",
                    "confidence": "中"
                }
        elif price_analysis["trend_30d"] == "上涨" and price_analysis["trend_7d"] == "下跌":
            if price_analysis["price_change_7d"] < -7:
                return {
                    "action": "逢低小幅买入",
                    "reason": "短期回调但中期趋势向上，可能是买入机会",
                    "confidence": "中"
                }
            else:
                return {
                    "action": "持有",
                    "reason": "短期小幅回调，中期趋势仍然向上",
                    "confidence": "中"
                }
        elif price_analysis["trend_30d"] == "下跌" and price_analysis["trend_7d"] == "上涨":
            return {
                "action": "谨慎持有",
                "reason": "可能是中期下跌趋势中的短期反弹",
                "confidence": "低"
            }
        else:  # 30天和7天都是下跌
            if price_analysis["price_change_30d"] < -20:
                return {
                    "action": "谨慎小幅买入",
                    "reason": "价格大幅下跌后可能开始筑底",
                    "confidence": "低"
                }
            else:
                return {
                    "action": "观望",
                    "reason": "价格处于下跌趋势，等待稳定信号",
                    "confidence": "中"
                }
    
    def _get_ahr999_based_advice(self, ahr999_analysis):
        """基于AHR999指数分析生成建议"""
        current_ahr = ahr999_analysis["current_value"]
        market_state = ahr999_analysis["market_state"]
        
        if market_state == "极度低估":
            return {
                "action": "大幅买入",
                "reason": f"AHR999指数({current_ahr:.3f})表明市场极度低估",
                "confidence": "高"
            }
        elif market_state == "低估":
            return {
                "action": "定期买入",
                "reason": f"AHR999指数({current_ahr:.3f})表明市场低估",
                "confidence": "中高"
            }
        elif market_state == "价值区间下限":
            return {
                "action": "小幅买入",
                "reason": f"AHR999指数({current_ahr:.3f})表明市场接近合理价值区间下限",
                "confidence": "中"
            }
        elif market_state == "价值区间上限":
            return {
                "action": "持有",
                "reason": f"AHR999指数({current_ahr:.3f})表明市场接近合理价值区间上限",
                "confidence": "中"
            }
        elif market_state == "高估":
            return {
                "action": "小幅减仓",
                "reason": f"AHR999指数({current_ahr:.3f})表明市场高估",
                "confidence": "中高"
            }
        else:  # 极度高估
            return {
                "action": "大幅减仓",
                "reason": f"AHR999指数({current_ahr:.3f})表明市场极度高估",
                "confidence": "高"
            }
    
    def _get_fear_greed_based_advice(self, fear_greed_analysis):
        """基于恐惧与贪婪指数分析生成建议"""
        current_fg = fear_greed_analysis["current_value"]
        market_mood = fear_greed_analysis["market_mood"]
        
        if market_mood == "Extreme Fear":
            return {
                "action": "逐步买入",
                "reason": f"恐惧贪婪指数({current_fg})显示市场极度恐慌，通常是买入时机",
                "confidence": "中高"
            }
        elif market_mood == "Fear":
            return {
                "action": "小幅买入",
                "reason": f"恐惧贪婪指数({current_fg})显示市场恐慌",
                "confidence": "中"
            }
        elif market_mood == "Neutral":
            return {
                "action": "持有",
                "reason": f"恐惧贪婪指数({current_fg})显示市场情绪中性",
                "confidence": "中"
            }
        elif market_mood == "Greed":
            return {
                "action": "谨慎持有",
                "reason": f"恐惧贪婪指数({current_fg})显示市场贪婪",
                "confidence": "中"
            }
        else:  # Extreme Greed
            return {
                "action": "考虑减仓",
                "reason": f"恐惧贪婪指数({current_fg})显示市场极度贪婪，注意风险",
                "confidence": "中高"
            }
    
    def _get_overall_advice(self, advice_dict):
        """综合分析，给出最终建议"""
        # 按照权重组合不同指标的建议
        actions = []
        reasons = []
        confidence_levels = {"低": 1, "中": 2, "中高": 3, "高": 4}
        
        if "price_based" in advice_dict:
            actions.append(advice_dict["price_based"]["action"])
            reasons.append(advice_dict["price_based"]["reason"])
            price_confidence = confidence_levels.get(advice_dict["price_based"]["confidence"], 2)
        else:
            price_confidence = 0
        
        if "ahr999_based" in advice_dict:
            actions.append(advice_dict["ahr999_based"]["action"])
            reasons.append(advice_dict["ahr999_based"]["reason"])
            ahr_confidence = confidence_levels.get(advice_dict["ahr999_based"]["confidence"], 2)
        else:
            ahr_confidence = 0
        
        if "fear_greed_based" in advice_dict:
            actions.append(advice_dict["fear_greed_based"]["action"])
            reasons.append(advice_dict["fear_greed_based"]["reason"])
            fg_confidence = confidence_levels.get(advice_dict["fear_greed_based"]["confidence"], 2)
        else:
            fg_confidence = 0
        
        # 统计每种行动的权重
        action_weights = {}
        for i, action in enumerate(actions):
            confidence = [price_confidence, ahr_confidence, fg_confidence][i]
            if action in action_weights:
                action_weights[action] += confidence
            else:
                action_weights[action] = confidence
        
        # 选择权重最高的行动
        if not action_weights:
            final_action = "观望"
            final_reason = "数据不足，无法给出明确建议"
            final_confidence = "低"
        else:
            final_action = max(action_weights.items(), key=lambda x: x[1])[0]
            
            # 合并相关原因
            relevant_reasons = []
            for i, action in enumerate(actions):
                if action == final_action:
                    relevant_reasons.append(reasons[i])
            
            final_reason = "综合分析：" + "；".join(relevant_reasons)
            
            # 确定最终置信度
            max_weight = max(action_weights.values())
            if max_weight >= 7:
                final_confidence = "高"
            elif max_weight >= 5:
                final_confidence = "中高"
            elif max_weight >= 3:
                final_confidence = "中"
            else:
                final_confidence = "低"
        
        return {
            "action": final_action,
            "reason": final_reason,
            "confidence": final_confidence
        }
    
    def _format_advice_output(self, price_analysis, sentiment_analysis, advice):
        """格式化投资建议输出"""
        output = []
        
        # 添加标题
        output.append("=============== BTC 投资建议分析报告 ===============")
        output.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 价格信息部分
        output.append("【价格信息】")
        if price_analysis["status"] == "success":
            latest_date = price_analysis.get("latest_date", "未知")
            output.append(f"最新数据日期: {latest_date}")
            output.append(f"当前价格: ${price_analysis['current_price']:,.2f}")
            output.append(f"7日均价: ${price_analysis['avg_7d']:,.2f}")
            output.append(f"30日均价: ${price_analysis['avg_30d']:,.2f}")
            output.append(f"90日均价: ${price_analysis['avg_90d']:,.2f}")
            output.append(f"24小时变化: {price_analysis['price_change_1d']:.2f}%")
            output.append(f"7日变化: {price_analysis['price_change_7d']:.2f}%")
            output.append(f"30日变化: {price_analysis['price_change_30d']:.2f}%")
            output.append(f"7日波动率: {price_analysis['volatility_7d']:.2f}%")
            output.append(f"30日波动率: {price_analysis['volatility_30d']:.2f}%")
            
            if price_analysis.get("rsi_14d") is not None:
                output.append(f"14日RSI: {price_analysis['rsi_14d']:.2f}")
            
            output.append(f"支撑位: ${price_analysis['support_level']:,.2f}")
            output.append(f"阻力位: ${price_analysis['resistance_level']:,.2f}")
            output.append(f"当前价格处于{self.analysis_period}日区间的 {price_analysis['price_percentile']:.2f}% 百分位")
        else:
            output.append(f"无法获取价格信息: {price_analysis.get('message', '未知错误')}")
        output.append("")
        
        # 市场情绪指标部分
        output.append("【市场情绪指标】")
        if sentiment_analysis["status"] == "success":
            # AHR999指数
            if "ahr999" in sentiment_analysis and sentiment_analysis["ahr999"]["status"] == "success":
                ahr = sentiment_analysis["ahr999"]
                output.append("AHR999指数:")
                output.append(f"  当前值: {ahr['current_value']:.3f} ({ahr['market_state']})")
                output.append(f"  7日均值: {ahr['avg_7d']:.3f}")
                output.append(f"  30日均值: {ahr['avg_30d']:.3f}")
                output.append(f"  7日趋势: {ahr['trend_7d']} ({ahr['change_7d']:.2f}%)")
                output.append(f"  30日趋势: {ahr['trend_30d']} ({ahr['change_30d']:.2f}%)")
                output.append(f"  历史百分位: {ahr['percentile']:.2f}%")
                output.append("")
            
            # 恐惧与贪婪指数
            if "fear_greed" in sentiment_analysis and sentiment_analysis["fear_greed"]["status"] == "success":
                fg = sentiment_analysis["fear_greed"]
                output.append("恐惧与贪婪指数:")
                output.append(f"  当前值: {fg['current_value']} ({fg['current_class']})")
                output.append(f"  7日均值: {fg['avg_7d']:.2f}")
                output.append(f"  30日均值: {fg['avg_30d']:.2f}")
                output.append(f"  7日趋势: {fg['trend_7d']} ({fg['change_7d']:.2f})")
                output.append(f"  30日趋势: {fg['trend_30d']} ({fg['change_30d']:.2f})")
                output.append(f"  市场情绪: {fg['market_mood']}")
                output.append(f"  情绪变化: {fg['mood_change']}")
                output.append("")
        else:
            output.append(f"无法获取市场情绪指标: {sentiment_analysis.get('message', '未知错误')}")
            output.append("")
        
        # 投资建议部分
        output.append("【投资建议】")
        
        # 分项建议
        if "price_based" in advice:
            pb = advice["price_based"]
            output.append(f"基于价格分析: {pb['action']} (置信度: {pb['confidence']})")
            output.append(f"  原因: {pb['reason']}")
        
        if "ahr999_based" in advice:
            ab = advice["ahr999_based"]
            output.append(f"基于AHR999指数: {ab['action']} (置信度: {ab['confidence']})")
            output.append(f"  原因: {ab['reason']}")
        
        if "fear_greed_based" in advice:
            fb = advice["fear_greed_based"]
            output.append(f"基于恐惧贪婪指数: {fb['action']} (置信度: {fb['confidence']})")
            output.append(f"  原因: {fb['reason']}")
        
        output.append("")
        
        # 综合建议
        if "overall" in advice:
            ov = advice["overall"]
            output.append("综合建议:")
            output.append(f"  行动: {ov['action']}")
            output.append(f"  原因: {ov['reason']}")
            output.append(f"  置信度: {ov['confidence']}")
        
        output.append("\n=============== 报告结束 ===============")
        
        return "\n".join(output) 