#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推文发送工具
从每日建议中提取市场周期分析并发送推文
"""

import re
import json
import os
import requests
from datetime import datetime
from pathlib import Path


class TweetSender:
    """推文发送器"""
    
    def __init__(self, tweet_api_url="http://localhost:8000/tweet"):
        """
        初始化推文发送器
        
        Args:
            tweet_api_url: 推文API的URL
        """
        self.tweet_api_url = tweet_api_url
        self.coinglass_url = "https://www.coinglass.com/zh/pro/i/FearGreedIndex"
        
    def extract_market_cycle_analysis(self, markdown_content):
        """
        从markdown内容中提取市场周期分析部分
        
        Args:
            markdown_content: markdown文件内容
            
        Returns:
            提取的市场周期分析文本，如果未找到则返回None
        """
        # 匹配 "## 一、市场周期分析" 部分的内容
        pattern = r'##\s+一、市场周期分析\s*\n(.*?)(?=\n##|\Z)'
        match = re.search(pattern, markdown_content, re.DOTALL)
        
        if match:
            # 提取内容并清理多余的空行
            content = match.group(1).strip()
            return content
        
        return None
    
    def get_latest_advice_file(self, advices_dir="advices"):
        """
        获取最新的建议文件
        
        Args:
            advices_dir: 建议文件所在目录
            
        Returns:
            最新建议文件的路径，如果没有找到则返回None
        """
        advices_path = Path(advices_dir)
        
        if not advices_path.exists():
            print(f"目录不存在: {advices_dir}")
            return None
        
        # 获取所有advice_开头的md文件
        advice_files = list(advices_path.glob("advice_*.md"))
        
        if not advice_files:
            print(f"未找到任何建议文件")
            return None
        
        # 按修改时间排序，返回最新的
        latest_file = max(advice_files, key=lambda p: p.stat().st_mtime)
        return latest_file
    
    def compose_tweet(self, market_analysis):
        """
        组合推文内容
        
        Args:
            market_analysis: 市场周期分析文本
            
        Returns:
            组合好的推文内容
        """
        # 构建推文内容
        tweet_parts = [
            f"📊 {datetime.now().strftime('%Y-%m-%d')} BTC市场周期分析",
            "",
            market_analysis,
            "",
            f"🔗 恐惧贪婪指数: {self.coinglass_url}",
            "",
            "#BTC #Bitcoin #加密货币 #市场分析 #FearGreedIndex #Bot"
        ]
        
        return "\n".join(tweet_parts)
    
    def send_tweet(self, content):
        """
        发送推文到API
        
        Args:
            content: 推文内容
            
        Returns:
            API响应结果
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "content": content
            }
            
            print(f"正在发送推文到: {self.tweet_api_url}")
            print(f"推文内容:\n{'-'*50}\n{content}\n{'-'*50}")
            
            response = requests.post(
                self.tweet_api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            print(f"✅ 推文发送成功!")
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.content else None
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 推文发送失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_and_send(self, advice_file_path=None):
        """
        处理建议文件并发送推文
        
        Args:
            advice_file_path: 建议文件路径，如果为None则自动获取最新的
            
        Returns:
            执行结果
        """
        # 如果没有指定文件，则获取最新的
        if advice_file_path is None:
            advice_file_path = self.get_latest_advice_file()
            
        if advice_file_path is None:
            return {
                "success": False,
                "error": "未找到建议文件"
            }
        
        print(f"📄 正在处理文件: {advice_file_path}")
        
        # 读取文件内容
        try:
            with open(advice_file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        except Exception as e:
            return {
                "success": False,
                "error": f"读取文件失败: {e}"
            }
        
        # 提取市场周期分析
        market_analysis = self.extract_market_cycle_analysis(markdown_content)
        
        if market_analysis is None:
            return {
                "success": False,
                "error": "未能从文件中提取市场周期分析"
            }
        
        print(f"✅ 成功提取市场周期分析")
        
        # 组合推文
        tweet_content = self.compose_tweet(market_analysis)
        
        # 发送推文
        result = self.send_tweet(tweet_content)
        
        return result


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='从建议文件中提取市场分析并发送推文')
    parser.add_argument(
        '--file',
        type=str,
        help='建议文件路径（如果不指定，则使用最新的建议文件）'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default='http://localhost:8000/tweet',
        help='推文API的URL（默认: http://localhost:8000/tweet）'
    )
    
    args = parser.parse_args()
    
    # 创建推文发送器
    sender = TweetSender(tweet_api_url=args.api_url)
    
    # 处理并发送
    result = sender.process_and_send(advice_file_path=args.file)
    
    if result['success']:
        print("\n🎉 推文发送完成！")
        exit(0)
    else:
        print(f"\n❌ 推文发送失败: {result.get('error', '未知错误')}")
        exit(1)


if __name__ == '__main__':
    main()

