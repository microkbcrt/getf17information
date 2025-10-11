import requests
from bs4 import BeautifulSoup
import json
import re
import os
import logging
from datetime import datetime

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 输出到控制台
    ]
)

def get_html(url):
    """获取网页内容，处理编码和异常"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        logging.info(f"请求URL: {url}")
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        
        # 处理编码问题
        if response.encoding == 'ISO-8859-1':
            response.encoding = 'utf-8'
            
        logging.info(f"请求成功，状态码: {response.status_code}")
        return response.text
        
    except requests.exceptions.RequestException as e:
        logging.error(f"请求失败: {e}")
        return None

def parse_weather_data(html):
    """解析天气数据，处理异常情况"""
    if not html:
        logging.warning("没有HTML内容可解析")
        return []
    
    try:
        # 使用html.parser解析器（无需额外安装）
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找天气数据节点
        day_nodes = soup.select('div.weather.pull-left')
        if not day_nodes:
            logging.warning("未找到天气数据节点")
            return []
            
        logging.info(f"找到 {len(day_nodes)} 天的天气数据")
        
        # 天气描述修饰替换规则（Python字典版本）
        weather_replacements = {
            '小雨': '多云，有小雨',
            '晴': '晴到多云',
            '小到中雨': '多云，有小到中雨',
            '阵雨': '多云，有(雷)阵雨',
            '雷阵雨': '多云，有雷阵雨局部大雨',
            '中雨': '多云，有中雷雨',
            '中到大雨': '多云，有中雷雨局部暴雨',
            '大雨': '多云到阴天，有大雨局部暴雨',
            '大到暴雨': '阴天，有大到暴雨',
            '暴雨': '阴天，有暴雨局部大暴雨',
            '暴雨到大暴雨': '阴天，有暴雨到大暴雨局部特大暴雨',
            '大暴雨': '阴天，有大暴雨局部特大暴雨',
        }
        
        # 天气图标映射
        icon_mappings = {
            '晴': {'day': '00.png', 'night': '00n.png'},
            '多云': {'day': '01.png', 'night': '01n.png'},
            '阴': {'day': '02.png', 'night': '02n.png'},
            '小雨': {'day': '07.png', 'night': '07n.png'},
            '小到中雨': {'day': '07.png', 'night': '07n.png'},
            '中雨': {'day': '08.png', 'night': '08.png'},
            '大雨': {'day': '09.png', 'night': '09.png'},
            '中到大雨': {'day': '10.png', 'night': '10.png'},
            '大到暴雨': {'day': '23.png', 'night': '23.png'},
            '暴雨': {'day': '23.png', 'night': '23n.png'},
            '暴雨到大暴雨': {'day': '23.png', 'night': '23n.png'},
            '大暴雨': {'day': '23.png', 'night': '23.png'},
            '雷阵雨': {'day': '11.png', 'night': '11.png'},
            '阵雨': {'day': '03.png', 'night': '03n.png'}
        }
        
        all_weather_data = []
        
        for i, day_node in enumerate(day_nodes):
            # 提取日期
            date_node = day_node.select_one('div.date')
            date_text = date_node.get_text(strip=True) if date_node else f"未知日期_{i+1}"
            date_text = re.sub(r'[^\d/周一二三四五六日]', '', date_text)  # 清理日期文本
            date_text = re.sub(r'周([一二三四五六日])', r'周\1', date_text)  # 统一周的表示
            
            # 提取天气描述、温度、风力等信息
            descs = day_node.select('div.desc')
            windds = day_node.select('div.windd')
            winds = day_node.select('div.winds')
            tmps = day_node.select('div[class*="tmp"]')
            
            # 白天天气
            day_weather_raw = descs[0].get_text(strip=True) if len(descs) > 0 else ""
            day_weather = weather_replacements.get(day_weather_raw, day_weather_raw)
            
            # 夜间天气
            night_weather_raw = descs[1].get_text(strip=True) if len(descs) > 1 else ""
            night_weather = weather_replacements.get(night_weather_raw, night_weather_raw)
            
            logging.info(f"第 {i+1} 天: {date_text}, 天气: {day_weather_raw}/{night_weather_raw} -> 转换后: {day_weather}/{night_weather}")
            
            # 匹配天气图标
            day_icon = icon_mappings.get(day_weather_raw, {}).get('day', 'default.png')
            night_icon = icon_mappings.get(night_weather_raw, {}).get('night', 'defaultn.png')
            
            # 构建白天数据
            daytime = {
                "weather": day_weather,
                "icon": day_icon,
                "temperature": tmps[0].get_text(strip=True) if len(tmps) > 0 else "",
                "wind_direction": windds[0].get_text(strip=True) if len(windds) > 0 else "",
                "wind_strength": winds[0].get_text(strip=True) if len(winds) > 0 else ""
            }
            
            # 构建夜间数据
            night = {
                "weather": night_weather,
                "icon": night_icon,
                "temperature": tmps[1].get_text(strip=True) if len(tmps) > 1 else "",
                "wind_direction": windds[1].get_text(strip=True) if len(windds) > 1 else "",
                "wind_strength": winds[1].get_text(strip=True) if len(winds) > 1 else ""
            }
            
            # 添加到总数据列表
            all_weather_data.append({
                "date": date_text,
                "daytime": daytime,
                "night": night
            })
        
        return all_weather_data
        
    except Exception as e:
        logging.error(f"解析天气数据时出错: {e}")
        return []

def save_data(data, js_file_path, json_file_path):
    """保存数据到JS和JSON文件"""
    if not data:
        logging.warning("没有数据可保存")
        return False
    
    try:
        # 转换为JSON字符串
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        # 保存为JS文件（用于前端直接引用）
        with open(js_file_path, 'w', encoding='utf-8') as js_file:
            js_file.write(f"var weatherData = {json_data};")
            
        # 保存为纯JSON文件
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(json_data)
            
        logging.info(f"数据已成功保存到 {js_file_path} 和 {json_file_path}")
        return True
        
    except Exception as e:
        logging.error(f"保存文件时出错: {e}")
        return False

def main():
    """主函数，协调整个数据获取和处理流程"""
    url = "http://nmc.cn/publish/forecast/AGD/guangzhou.html"
    
    try:
        # 禁用不安全请求警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        logging.info("===== 开始获取广州天气预报数据 =====")
        
        # 获取网页内容
        html = get_html(url)
        if not html:
            raise Exception("无法获取网页内容")
            
        # 解析天气数据
        weather_data = parse_weather_data(html)
        if not weather_data:
            raise Exception("未解析到有效天气数据")
            
        # 保存数据
        js_file_path = 'nmcweather.js'
        json_file_path = 'nmcweather.json'
        
        if save_data(weather_data, js_file_path, json_file_path):
            logging.info("===== 天气数据更新完成 =====")
        else:
            raise Exception("保存数据失败")
            
    except Exception as e:
        logging.error(f"执行脚本时发生致命错误: {str(e)}")
        raise  # 重新抛出异常，使GitHub Actions任务标记为失败

if __name__ == "__main__":
    main()
