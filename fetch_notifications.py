import requests
import json
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_and_save_notifications(url, output_file):
    """
    从指定URL获取JSON数据并保存到本地文件
    
    Args:
        url (str): 数据来源URL
        output_file (str): 输出文件路径
    """
    try:
        # 发送HTTP请求
        logger.info(f"正在从 {url} 获取通知数据")
        response = requests.get(url, timeout=30)
        
        # 检查响应状态码
        response.raise_for_status()
        
        # 解析JSON数据
        data = response.json()
        
        # 保存数据到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"通知数据已成功保存到 {output_file}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"请求异常: {e}")
        return False
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"JSON解析错误: {e}")
        return False
    except Exception as e:
        logger.error(f"发生未知错误: {e}")
        return False

if __name__ == "__main__":
    NOTIFICATIONS_URL = "https://kbcrt.v6.rocks:55125/notifications.json"
    OUTPUT_FILE = "notifications.json"
    
    # 执行获取和保存操作
    success = fetch_and_save_notifications(NOTIFICATIONS_URL, OUTPUT_FILE)
    
    # 检查文件是否成功生成
    if success and os.path.exists(OUTPUT_FILE):
        print(f"通知数据已成功获取并保存到 {OUTPUT_FILE}")
    else:
        print("获取通知数据失败")
        exit(1)    
