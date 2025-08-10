#!/usr/bin/env python3
"""
DeepSeek API 连接测试脚本
用于验证与 DeepSeek API 的连接状态和基本功能
"""

import os
import json
import logging
import requests
import time
from datetime import datetime
from config import DEEPSEEK_AI, DATA_DIRS
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class DeepSeekTester:
    def __init__(self, api_key=None):
        """初始化测试器
        
        Args:
            api_key: DeepSeek API密钥，如果为None则从环境变量获取
        """
        self.api_key = DEEPSEEK_AI['api_key']
        self.api_url = "https://api.deepseek.com/chat/completions"
        
        if not self.api_key:
            logger.error("未设置 DeepSeek API 密钥！请设置环境变量 DEEPSEEK_API_KEY")
            raise ValueError("API密钥未设置")

    def test_connection(self, model="deepseek-chat", max_retries=3, retry_delay=2.0):
        """测试与 DeepSeek API 的连接
        
        Args:
            model: 要测试的模型名称
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间（秒）
        
        Returns:
            bool: 连接测试是否成功
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hello! This is a test message."}
            ],
            "temperature": 0.7,
            "max_tokens": 50
        }
        
        retries = 0
        while retries <= max_retries:
            try:
                logger.info(f"正在测试 DeepSeek API 连接，模型: {model}，尝试次数: {retries + 1}/{max_retries + 1}")
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    logger.info("✅ API连接测试成功！")
                    logger.info(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
                    return True
                    
                elif response.status_code == 401:
                    logger.error("❌ API密钥无效或未授权")
                    return False
                    
                elif response.status_code == 429:
                    logger.warning(f"⚠️ API调用频率限制 (429)，等待重试...")
                    
                else:
                    logger.error(f"❌ API调用失败: HTTP {response.status_code}")
                    logger.error(f"错误详情: {response.text}")
                    return False
                    
            except requests.exceptions.Timeout:
                logger.warning("⚠️ API请求超时")
            except requests.exceptions.ConnectionError:
                logger.warning("⚠️ API连接错误")
            except Exception as e:
                logger.error(f"❌ 发生未知错误: {str(e)}")
            
            retries += 1
            if retries <= max_retries:
                wait_time = retry_delay * (2 ** (retries - 1))
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                logger.error("❌ 达到最大重试次数，测试失败")
                return False
        
        return False

def main():
    """主函数"""
    try:
        # 创建测试器实例
        tester = DeepSeekTester()
        
        # 测试 deepseek-chat 模型
        logger.info("开始测试 DeepSeek API 连接...")
        success = tester.test_connection(model="deepseek-chat")
        
        if success:
            logger.info("🎉 所有测试完成，API连接正常")
        else:
            logger.error("💔 API连接测试失败，请检查配置和网络状态")
            
    except Exception as e:
        logger.error(f"💔 测试过程中发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()