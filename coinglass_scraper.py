import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('coinglass_scraper')

class CoinglassScraperError(Exception):
    """自定义异常类"""
    pass

class CoinglassScraper:
    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
        self._last_data = None
        self._last_update = None
        self._cache_duration = 300  # 缓存时间5分钟
    
    async def _initialize(self):
        """初始化浏览器"""
        if not self._browser:
            try:
                playwright = await async_playwright().start()
                self._browser = await playwright.chromium.launch(headless=True)
                self._context = await self._browser.new_context()
                self._page = await self._context.new_page()
            except Exception as e:
                logger.error(f"初始化浏览器失败: {str(e)}")
                raise CoinglassScraperError("浏览器初始化失败")
    
    async def _close(self):
        """关闭浏览器"""
        if self._browser:
            try:
                await self._browser.close()
                self._browser = None
                self._context = None
                self._page = None
            except Exception as e:
                logger.error(f"关闭浏览器失败: {str(e)}")
    
    async def _fetch_table_data(self):
        """获取表格数据"""
        try:
            await self._page.goto('https://www.coinglass.com/bull-market-peak-signals')
            await self._page.wait_for_selector('table', timeout=30000)
            
            # 提取表格数据
            table_data = await self._page.evaluate('''() => {
                const rows = Array.from(document.querySelectorAll('table tr'));
                return rows.map(row => {
                    const cells = Array.from(row.querySelectorAll('td, th'));
                    return cells.map(cell => cell.textContent.trim());
                });
            }''')
            
            return table_data
        except Exception as e:
            logger.error(f"获取表格数据失败: {str(e)}")
            raise CoinglassScraperError("获取表格数据失败")
    
    def _process_data(self, table_data):
        """处理表格数据"""
        try:
            # 转换为DataFrame
            df = pd.DataFrame(table_data[1:], columns=table_data[0])
            
            # 提取关键指标
            indicators = {}
            for index, row in df.iterrows():
                name = row.get('Name', '').strip()
                value = row.get('Value', '').strip()
                if name and value:
                    try:
                        # 移除百分号并转换为浮点数
                        value = float(value.replace('%', ''))
                        indicators[name] = value
                    except ValueError:
                        logger.warning(f"无法转换值 '{value}' 为数字")
                        continue
            
            return indicators
        except Exception as e:
            logger.error(f"处理数据失败: {str(e)}")
            raise CoinglassScraperError("数据处理失败")
    
    async def get_indicators(self, force_refresh=False):
        """获取市场指标
        
        Args:
            force_refresh (bool): 是否强制刷新缓存
            
        Returns:
            dict: 市场指标数据
        """
        # 检查缓存
        now = datetime.now()
        if (not force_refresh and 
            self._last_data and 
            self._last_update and 
            (now - self._last_update).total_seconds() < self._cache_duration):
            return self._last_data
        
        try:
            await self._initialize()
            table_data = await self._fetch_table_data()
            indicators = self._process_data(table_data)
            
            # 更新缓存
            self._last_data = indicators
            self._last_update = now
            
            return indicators
        except Exception as e:
            logger.error(f"获取指标失败: {str(e)}")
            return None
        finally:
            await self._close()

# 创建全局实例
scraper = CoinglassScraper()

async def get_market_indicators(force_refresh=False):
    """对外提供的接口函数"""
    try:
        return await scraper.get_indicators(force_refresh)
    except Exception as e:
        logger.error(f"获取市场指标失败: {str(e)}")
        return None

# 测试代码
if __name__ == "__main__":
    async def test():
        indicators = await get_market_indicators()
        if indicators:
            print("\n获取的市场指标:")
            for name, value in indicators.items():
                print(f"{name}: {value}")
        else:
            print("获取指标失败")
    
    asyncio.run(test())