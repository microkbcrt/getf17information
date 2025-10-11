import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re  # 新增：导入正则表达式模块

def fetch_weather_data():
    """精准解析天气数据，确保各部分内容完整提取"""
    url = "http://www.tqyb.com.cn/data/ten/GZFR.HTML"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题（强制匹配包含"未来十天"的<strong>标签）
        title = soup.find('strong', string=lambda t: "未来十天" in str(t))
        title = title.get_text(strip=True) if title else "广州市未来十天天气趋势预报和建议"
        
        # 提取过程天气预报（考虑标签嵌套情况）
        forecast_title = soup.find('strong', string=lambda t: "过程天气预报" in str(t))
        forecast_content = ""
        if forecast_title:
            # 获取<strong>标签的父元素（可能是<span>）
            parent_span = forecast_title.parent
            # 从父元素的下一个兄弟元素开始遍历
            next_elems = parent_span.find_next_siblings()
            for elem in next_elems:
                # 遇到下一个<strong>标签时停止（如"二、应用建议"）
                if elem.name == 'strong' and "应用建议" in elem.get_text(strip=True):
                    break
                if elem.name in ['span', 'p']:
                    # 提取文本并处理特殊字符
                    text = elem.get_text(strip=True).replace('<br>', '').replace('&nbsp;', ' ')
                    forecast_content += text + " "
            # 清理多余空格并去除重复标题
            forecast_content = re.sub(r'\s+', ' ', forecast_content).strip()
            # 额外检查：若内容包含标题文本则移除
            forecast_content = re.sub(r'一、过程天气预报\s*', '', forecast_content)
            
        # 提取应用建议（处理标签嵌套问题）
        advice_title = soup.find('strong', string=lambda t: "应用建议" in str(t))
        advice_content = ""
        if advice_title:
            # 获取<strong>标签的父元素（可能是<span>）
            parent_span = advice_title.parent
            # 从父元素的下一个兄弟元素开始遍历
            next_elems = parent_span.find_next_siblings()
            advice_text = ""
            for elem in next_elems:
                # 遇到右对齐的div时停止
                if elem.name == 'div' and 'text-align:right' in str(elem.get('style', '')):
                    break
                if elem.name in ['span', 'p']:
                    # 提取文本并处理特殊字符
                    text = elem.get_text(strip=True).replace('<br>', '').replace('&nbsp;', ' ')
                    advice_text += text + " "
            # 按1.和2.分割建议，并格式化
            advice_items = re.findall(r'(\d\.\s.*?)(?=\d\.|$)', advice_text)
            advice_content = "\n".join(advice_items) if advice_items else advice_text.strip()

    
        # 提取发布信息（定位到右对齐的div）
        footer_divs = soup.find_all('div', style=lambda s: "text-align:right" in str(s))
        bureau = "广州市气象台"
        time = "2025年06月27日11时"
        if footer_divs:
            footer_texts = [div.get_text(strip=True) for div in footer_divs]
            # 尝试从文本中提取单位和时间
            for text in footer_texts:
                if "气象台" in text:
                    bureau = text
                time_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日\d{1,2}时)', text)  # 修正：使用re.search
                if time_match:
                    time = time_match.group(1)
        
        # 最终格式整理（确保各部分非空）
        formatted_content = f"{title}\n\n一、过程天气预报\n{forecast_content or '暂无具体预报内容'}\n\n"
        formatted_content += "二、气象预报应用建议\n{}\n\n{}\n{}".format(
            advice_content, bureau, time)
        
        # 保存到文件
        with open("tendaysweather.txt", "w", encoding="utf-8") as file:
            file.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            file.write(formatted_content)
            
        print("天气数据已成功解析并保存")
        return True
        
    except Exception as e:
        print(f"解析异常: {e}")
        return False

if __name__ == "__main__":
    fetch_weather_data()
