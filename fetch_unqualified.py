import requests
import json
import os
from datetime import datetime

def fetch_and_save_unqualified_data():
    """从指定URL获取JSON数据并保存到本地文件"""
    url = "https://kbcrt.gd.work:55125/unqualified.json"
    
    try:
        # 发送HTTP请求获取数据
        response = requests.get(url, timeout=10)
        # 检查请求是否成功
        response.raise_for_status()
        
        # 解析JSON数据
        data = response.json()
        
        # 保存数据到JSON文件
        with open('unqualified.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"数据已成功保存到 unqualified.json")
        
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
    except json.JSONDecodeError:
        print("JSON解析失败")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    fetch_and_save_unqualified_data()
