import requests
import json
import os

def fetch_and_save_bilibili_rank():
    """
    从API获取B站热搜数据并保存到bilibilirank.json文件中。
    """
    api_url = "https://v2.xxapi.cn/api/weibohot"
    file_path = "weiborank.json"

    try:
        # 发送HTTP GET请求
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()  # 如果请求失败（状态码不是2xx），则抛出异常

        # 解析JSON数据
        data = response.json()

        # 将数据写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"成功获取B站热搜并保存到 {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"请求API时发生错误: {e}")
    except json.JSONDecodeError:
        print("解析JSON响应失败，API可能返回了无效的数据。")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    fetch_and_save_bilibili_rank()
