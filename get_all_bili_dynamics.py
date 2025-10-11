# get_all_bili_dynamics.py
import requests
import json
from datetime import datetime
import os
import time

# --- 【统一配置区】 ---
# 将所有目标用户的信息集中管理，方便增删
TARGET_USERS = [
    {"name": "F1", "mid": "65125803"},
    {"name": "genshin", "mid": "401742377"},
    {"name": "honkai", "mid": "1340190821"},
    {"name": "phigros", "mid": "414149787"},
    {"name": "ruixue", "mid": "258614728"},
    {"name": "tastecar", "mid": "386205726"},
    {"name": "zzz", "mid": "1636034895"},
]
OUTPUT_FILENAME = 'dynamics.json' # 所有动态都输出到这一个文件
SESSDATA = os.environ.get('BILI_SESSDATA')

def get_content_from_detail_api(dynamic_id, headers):
    """
    一个更强大的函数，用于从详情API中深度提取和组合文本内容，
    能够兼容图文、纯文本、视频等多种动态类型。
    （此函数在所有原始脚本中完全相同，直接复用）
    """
    detail_api_url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail"
    params = {"dynamic_id": dynamic_id}
    
    # print(f"  正在请求详情API以获取动态({dynamic_id})的完整内容...")
    
    try:
        response = requests.get(detail_api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('code') == 0 and data.get('data', {}).get('card'):
            card_str = data['data']['card'].get('card')
            card_data = json.loads(card_str)
            
            # 1. 尝试图文动态的 'item.description'
            description = card_data.get('item', {}).get('description')
            if description:
                return description.strip()
            
            # 2. 尝试纯文本或带文字转发的 'item.content'
            content = card_data.get('item', {}).get('content')
            if content:
                return content.strip()
            
            # 3. 尝试视频动态的 'title', 'desc', 和 'dynamic'
            title = card_data.get('title')
            video_desc = card_data.get('desc')
            dynamic_text = card_data.get('dynamic', '') # 附加文字可能不存在
            if title and video_desc is not None:
                # 组合成更有意义的文本
                final_text = f"投稿了视频：【{title}】\n\n{dynamic_text}\n\n视频简介：\n{video_desc}"
                return final_text.strip()

            # 4. 最后的备用检查 (兼容旧逻辑)
            if dynamic_text:
                 return dynamic_text.strip()

            print(f"  警告：在详情API响应中未能找到任何有效的文本字段 (ID: {dynamic_id})。")
            return None
        else:
            print(f"  [详情API错误] Code: {data.get('code')}, Message: {data.get('message', '无')}")
            return None
            
    except Exception as e:
        print(f"  [严重错误] 处理详情API时发生异常: {e}")
        return None

def fetch_latest_dynamic_for_user(host_mid, headers):
    """
    为单个用户获取最新动态的核心函数。
    修改后不再写入文件，而是返回包含动态数据的字典。
    """
    list_api_url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?host_mid={host_mid}"

    # print(f"正在通过列表API获取用户(UID: {host_mid})的最新动态...")
    try:
        response = requests.get(list_api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('code') != 0:
            print(f"  列表API返回错误！ 代码: {data.get('code')}, 信息: {data.get('message', '无')}")
            return None

        items_list = data.get('data', {}).get('items')
        if not items_list:
            print(f"  用户(UID: {host_mid})的动态列表中未找到任何动态。")
            return None

        latest_post = max(items_list, key=lambda item: item.get('modules', {}).get('module_author', {}).get('pub_ts', 0))
        
        dynamic_id = latest_post.get('id_str')
        if not dynamic_id:
            print("  错误：无法从最新的动态中提取到 'id_str'。")
            return None
        
        # print(f"  已找到最新动态ID({dynamic_id})。")
        
        final_content = get_content_from_detail_api(dynamic_id, headers)
        
        if final_content is None:
            # print("  因为未能获取到有效的动态文本内容，将跳过此用户。")
            return None

        publish_timestamp = latest_post.get('modules', {}).get('module_author', {}).get('pub_ts', 0)
        publish_time_str = datetime.fromtimestamp(publish_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        dynamic_url = f"https://www.bilibili.com/opus/{dynamic_id}"

        # 准备要返回的数据字典
        final_data = {
            "publish_time": publish_time_str,
            "dynamic_url": dynamic_url,
            "content": final_content
        }
        return final_data

    except Exception as e:
        print(f"  获取用户(UID: {host_mid})动态时发生未知错误: {e}")
        return None

def main():
    """
    主执行函数，负责调度、聚合和文件写入。
    """
    if not SESSDATA:
        print("错误：环境变量 BILI_SESSDATA 未设置！脚本无法运行。")
        exit(1)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Cookie': f'SESSDATA={SESSDATA}',
        'Referer': 'https://www.bilibili.com/'
    }

    # 创建一个空字典来存储所有用户的最终数据
    all_dynamics_data = {}
    
    print("🚀 开始获取所有目标用户的最新B站动态...")

    for user in TARGET_USERS:
        user_name = user['name']
        user_mid = user['mid']
        print(f"\n--- 正在处理用户: {user_name} (UID: {user_mid}) ---")
        
        dynamic_data = fetch_latest_dynamic_for_user(user_mid, headers)
        
        if dynamic_data:
            all_dynamics_data[user_name] = dynamic_data
            print(f"✅ 成功获取到 '{user_name}' 的最新动态。")
        else:
            print(f"❌ 未能获取到 '{user_name}' 的有效动态，已跳过。")
        
        # 为了避免请求过于频繁导致被API限制，每次请求后加入短暂的延时
        time.sleep(1) 

    if not all_dynamics_data:
        print("\n⚠️ 本次运行未能获取到任何用户的动态，JSON文件将不会被创建或更新。")
        return

    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(all_dynamics_data, f, ensure_ascii=False, indent=4)
        print(f"\n\n🎉 任务完成！所有用户的动态已合并保存到文件: {OUTPUT_FILENAME}")
    except Exception as e:
        print(f"\n\n🚨 严重错误：在写入最终JSON文件时发生异常: {e}")

if __name__ == "__main__":
    main()
