"""
DeepSeek API调用模块 - 提供与DeepSeek R1模型的API交互

此模块负责:
1. 提供统一的API调用接口
2. 管理身份验证和API密钥
3. 处理错误和异常情况
4. 格式化请求和响应
"""

import os
import json
import logging
import requests
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# 导入配置
from config import DEEPSEEK_AI, DATA_DIRS

# 导入提示词模块
from ai.prompt import (
    get_investment_advice_template, 
    prepare_investment_advice_params,
    save_prompt_for_debug,
    extract_json_from_text
)

# 设置日志
logger = logging.getLogger(__name__)

class DeepseekAPI:
    """DeepSeek API接口类，提供与DeepSeek R1模型交互的方法"""
    
    def __init__(self, api_key: str = None, api_url: str = None):
        """初始化DeepSeek API客户端
        
        Args:
            api_key: DeepSeek API密钥，如果为None则尝试从环境变量获取
            api_url: 自定义API URL，如果为None则使用配置中的值
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.api_url = api_url or DEEPSEEK_AI['api_url']
        
        if not self.api_key:
            logger.warning("未设置DeepSeek API密钥，请通过环境变量DEEPSEEK_API_KEY或初始化参数提供")
    
    def validate_api_key(self) -> bool:
        """验证API密钥是否设置
        
        Returns:
            如果API密钥已设置则返回True，否则返回False
        """
        return bool(self.api_key)
    
    def chat_completion(self, 
                        messages: List[Dict[str, str]], 
                        model: str = None,
                        temperature: float = None,
                        max_tokens: int = None,
                        top_p: float = None,
                        stream: bool = None,
                        max_retries: int = 3,
                        retry_delay: float = 2.0,
                        **kwargs) -> Optional[Dict[str, Any]]:
        """发送聊天补全请求至DeepSeek API
        
        Args:
            messages: 消息列表，格式为[{"role": "user", "content": "..."}, ...]
            model: 使用的模型名称，默认从配置读取
            temperature: 采样温度，控制输出的随机性，默认从配置读取
            max_tokens: 最大生成的token数量，默认从配置读取
            top_p: 核采样的概率质量，默认从配置读取
            stream: 是否使用流式响应，默认从配置读取
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间（秒）
            **kwargs: 其他API参数
            
        Returns:
            API响应的JSON数据，如果调用失败则返回None
        """
        if not self.validate_api_key():
            logger.error("未设置API密钥，无法调用DeepSeek API")
            return None
        
        # 准备参数，优先使用传入的参数，否则使用配置中的默认值
        payload = {
            "model": model or DEEPSEEK_AI['model'],
            "messages": messages,
            "temperature": temperature if temperature is not None else DEEPSEEK_AI['temperature'],
            "max_tokens": max_tokens if max_tokens is not None else DEEPSEEK_AI['max_tokens'],
            "top_p": top_p if top_p is not None else DEEPSEEK_AI['top_p'],
            "stream": stream if stream is not None else DEEPSEEK_AI['stream']
        }
        
        # 添加其他可选参数
        payload.update(kwargs)
        
        # 调用API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 实现重试逻辑
        retries = 0
        while retries <= max_retries:
            try:
                logger.info(f"正在调用DeepSeek API，模型: {payload['model']}，尝试次数: {retries + 1}/{max_retries + 1}")
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    logger.info("DeepSeek API调用成功")
                    return response.json()
                elif response.status_code == 429:  # 速率限制
                    logger.warning(f"API调用受到限制 (429)，等待重试...")
                    retries += 1
                    if retries <= max_retries:
                        # 等待时间指数增长
                        wait_time = retry_delay * (2 ** (retries - 1))
                        logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"达到最大重试次数，API调用失败: {response.status_code} - {response.text}")
                        return None
                elif response.status_code >= 500:  # 服务器错误
                    logger.warning(f"服务器错误 ({response.status_code})，尝试重试...")
                    retries += 1
                    if retries <= max_retries:
                        wait_time = retry_delay * (2 ** (retries - 1))
                        logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"达到最大重试次数，API调用失败: {response.status_code} - {response.text}")
                        return None
                else:
                    # 其他错误（如验证失败、参数错误等）不进行重试
                    logger.error(f"API调用失败: {response.status_code} - {response.text}")
                    return None
            
            except requests.exceptions.Timeout:
                logger.warning("API请求超时，尝试重试...")
                retries += 1
                if retries <= max_retries:
                    wait_time = retry_delay * (2 ** (retries - 1))
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error("达到最大重试次数，API请求超时")
                    return None
            except requests.exceptions.ConnectionError:
                logger.warning("API连接错误，尝试重试...")
                retries += 1
                if retries <= max_retries:
                    wait_time = retry_delay * (2 ** (retries - 1))
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error("达到最大重试次数，API连接失败")
                    return None
            except requests.exceptions.RequestException as e:
                # 其他requests异常
                logger.error(f"API请求异常: {str(e)}")
                retries += 1
                if retries <= max_retries:
                    wait_time = retry_delay * (2 ** (retries - 1))
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"达到最大重试次数，API请求失败: {str(e)}")
                    return None
            except Exception as e:
                logger.error(f"调用DeepSeek API出错: {str(e)}")
                retries += 1
                if retries <= max_retries:
                    wait_time = retry_delay * (2 ** (retries - 1))
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"达到最大重试次数，发生未知错误: {str(e)}")
                    return None
        
        return None
    
    def generate_text(self, prompt: str, max_retries: int = 3, retry_delay: float = 2.0, **kwargs) -> Optional[str]:
        """使用单一提示词生成文本响应
        
        这是chat_completion的简化版本，方便单个提示词的使用场景
        
        Args:
            prompt: 提示词文本
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间（秒）
            **kwargs: 传递给chat_completion的其他参数
            
        Returns:
            生成的文本内容，如果调用失败则返回None
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages, max_retries=max_retries, retry_delay=retry_delay, **kwargs)
        
        if response:
            
            self.save_response_to_file(response)
            
            try:
                content = response["choices"][0]["message"]["content"]
                return content
            except (KeyError, IndexError) as e:
                logger.error(f"解析API响应出错: {str(e)}")
                return None
        
        return None
    
    def generate_investment_advice(self, data_json: str, last_advice: Dict = None, max_retries: int = 3, retry_delay: float = 2.0, **kwargs) -> Optional[str]:
        """生成加密货币投资建议
        
        Args:
            data_json: 包含历史价格和指标数据的JSON字符串
            last_advice: 上次生成的建议，JSON格式，可选
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间（秒）
            **kwargs: 传递给generate_text的其他参数
            
        Returns:
            生成的投资建议文本，如果调用失败则返回None
        """
        # 获取当前日期
        current_date = kwargs.pop('current_date', None)
        if not current_date:
            current_date = datetime.now().strftime('%Y-%m-%d')
        
        # 准备提示词参数
        params = prepare_investment_advice_params(current_date, last_advice)
        
        # 生成提示词
        prompt = get_investment_advice_template(
            current_date=params["current_date"],
            last_position=params["last_position"],
            last_cost_basis=params["last_cost_basis"],
            last_action=params["last_action"],
            data_json=data_json
        )
        
        save_prompt_for_debug(prompt)
        
        return self.generate_text(prompt, max_retries=max_retries, retry_delay=retry_delay, **kwargs)
    
    def save_investment_record(self, recommendation: str, data_json: str = None, **kwargs) -> Dict[str, Any]:
        """保存投资建议记录，并解析JSON格式的操作摘要
        
        Args:
            recommendation: 生成的投资建议文本
            data_json: 用于生成建议的市场数据，可选
            **kwargs: 其他元数据
            
        Returns:
            包含记录ID和解析后建议的字典
        """
        # 确保记录目录存在
        records_dir = kwargs.get('records_dir', DATA_DIRS['records'])
        os.makedirs(records_dir, exist_ok=True)
        
        # 创建记录ID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        record_id = f"BTI-{timestamp}"
        
        # 解析JSON操作摘要
        advice_data = extract_json_from_text(recommendation) or {}
        
        # 准备记录数据
        record = {
            "id": record_id,
            "timestamp": timestamp,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "recommendation": recommendation,
            "advice_data": advice_data,
            "metadata": kwargs
        }
        
        # 如果提供了市场数据，也保存它
        # if data_json:
        #     try:
        #         record["market_data"] = json.loads(data_json)
        #     except:
        #         record["market_data_raw"] = data_json
        
        # 保存到文件
        filename = f"{record_id}.json"
        filepath = os.path.join(records_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已保存投资建议记录: {filepath}")
        return {"record_id": record_id, "advice_data": advice_data}
    
    def load_investment_record(self, record_id: str, records_dir: str = None) -> Optional[Dict[str, Any]]:
        """加载投资建议记录
        
        Args:
            record_id: 记录ID
            records_dir: 记录目录
            
        Returns:
            记录数据字典，如果加载失败则返回None
        """
        if records_dir is None:
            records_dir = DATA_DIRS['records']
            
        filepath = os.path.join(records_dir, f"{record_id}.json")
        
        if not os.path.exists(filepath):
            logger.error(f"找不到记录文件: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                record = json.load(f)
            return record
        except Exception as e:
            logger.error(f"加载记录失败: {str(e)}")
            return None
    
    def load_latest_investment_record(self, records_dir: str = None) -> Optional[Dict[str, Any]]:
        """加载最新的投资建议记录
        
        通过文件名中的时间戳排序，找到最新的记录文件
        
        Args:
            records_dir: 记录目录
            
        Returns:
            最新的记录数据字典和记录ID，如果没有记录则返回None
        """
        records_dir = DATA_DIRS['records']
            
        if not os.path.exists(records_dir):
            logger.warning(f"记录目录不存在: {records_dir}")
            return None, None
        
        # 获取所有BTI开头的文件
        try:
            files = [f for f in os.listdir(records_dir) if f.startswith('BTI-') and f.endswith('.json')]
            if not files:
                logger.info(f"目录中没有找到投资建议记录: {records_dir}")
                return None, None
            
            # 按文件名排序（基于时间戳）
            files.sort(reverse=True)
            latest_file = files[0]
            record_id = latest_file.split('.')[0]  # 去掉.json后缀
            
            # 加载记录
            record = self.load_investment_record(record_id, records_dir)
            if record:
                logger.info(f"成功加载最新的投资建议记录: {record_id}")
                return record, record_id
            else:
                return None, None
        except Exception as e:
            logger.error(f"查找最新记录时出错: {str(e)}")
            return None, None
    
    def generate_and_save_investment_advice(self, data_json: str, last_record_id: str = None, debug: bool = False, 
                                 max_retries: int = 3, retry_delay: float = 2.0, **kwargs) -> Dict[str, Any]:
        """生成投资建议并保存记录，可选择加载上次建议
        
        Args:
            data_json: 包含历史价格和指标数据的JSON字符串
            last_record_id: 上次建议的记录ID，如果不提供，会自动加载最新记录
            debug: 是否开启调试模式，记录完整提示词
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间（秒）
            **kwargs: 传递给generate_investment_advice的其他参数
            
        Returns:
            包含建议内容、记录ID和结构化建议数据的字典
        """
        # 尝试加载上次建议
        last_advice = None
        
        # 如果未提供上次记录ID，尝试自动找到最新记录
        if not last_record_id:
            logger.info("未提供上次记录ID，正在尝试自动加载最新记录")
            last_record, last_record_id = self.load_latest_investment_record()
        else:
            logger.info(f"正在加载指定的上次投资建议: {last_record_id}")
            last_record = self.load_investment_record(last_record_id)
        
        # 从记录中提取建议数据
        if last_record:
            # 首先尝试使用已解析的结构化数据
            if "advice_data" in last_record and last_record["advice_data"]:
                last_advice = last_record["advice_data"]
                logger.info(f"成功加载上次建议数据: 仓位 {last_advice.get('position', 'N/A')}%")
            # 如果没有结构化数据，尝试重新解析
            elif "recommendation" in last_record:
                last_advice = extract_json_from_text(last_record["recommendation"])
                if last_advice:
                    logger.info(f"从文本重新解析上次建议数据: 仓位 {last_advice.get('position', 'N/A')}%")
        else:
            logger.info("没有找到上次记录，将生成首次投资建议")
        
        # 将重试参数传递给generate_investment_advice
        advice = self.generate_investment_advice(
            data_json, 
            last_advice=last_advice, 
            max_retries=max_retries,
            retry_delay=retry_delay,
            **kwargs
        )
        
        if not advice:
            logger.error("生成投资建议失败，即使在重试后")
            return {"success": False, "error": "生成投资建议失败，请检查API连接和配置"}
        
        try:
            # 保存记录并解析结构化数据
            result = self.save_investment_record(
                recommendation=advice,
                data_json=data_json,
                last_record_id=last_record_id,
                user_settings=kwargs.get('user_settings', {})
            )
            
            return {
                "success": True,
                "advice": advice,
                "record_id": result["record_id"],
                "advice_data": result["advice_data"]
            }
        except Exception as e:
            logger.error(f"保存投资建议记录时出错: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            
            # 尽管保存失败，仍然返回建议内容
            return {
                "success": True,
                "advice": advice,
                "record_id": f"temp-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "advice_data": extract_json_from_text(advice) or {},
                "save_error": str(e)
            }

    def save_response_to_file(self, response):
        """
        将AI回复保存到本地文件
        
        Args:
            response: AI的回复内容 (JSON对象)
        """
        try:
            # 创建保存目录
            responses_dir = os.path.join(DATA_DIRS['responses'])
            os.makedirs(responses_dir, exist_ok=True)
            
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"response_{timestamp}.json"
            file_path = os.path.join(responses_dir, filename)
            
            # 保存到文件 (作为JSON)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
                  
            logger.info(f"AI原始回复已保存至: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存AI回复时出错: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
