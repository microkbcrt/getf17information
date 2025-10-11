import requests
import json
import re
import time
from datetime import datetime

# 目标URL
url = 'http://tqyb.com.cn/data/gzWeather/hntData.js'

try:
    # 发送HTTP请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()  # 检查请求是否成功
    
    # 提取JSON数据
    js_content = response.text
    match = re.search(r'var hntData = ({.*?});', js_content, re.DOTALL)
    if not match:
        raise ValueError('未找到hntData数据')
    
    json_str = match.group(1)
    json_str = json_str.replace('\\"', '"')  # 修复转义字符
    
    # 解析JSON
    data = json.loads(json_str)
    
    # 验证数据结构
    if 'data' not in data or 'G3399' not in data['data'] or not isinstance(data['data']['G3399'], list):
        raise ValueError('G3399数据不存在或格式错误')
    
    station = data['data']['G3399']
    
    # 提取露温数据 (lw -> G1099)
    if len(station) < 3 or 'lw' not in station[2] or 'G1099' not in station[2]['lw'] or not isinstance(station[2]['lw']['G1099'], list):
        raise ValueError('露温数据缺失或格式错误')
    
    lw_values = station[2]['lw']['G1099']
    lw_last = lw_values[-1]
    
    # 提取地温数据 (dw -> G3399)
    if 'dw' not in station[0] or 'G3399' not in station[0]['dw'] or not isinstance(station[0]['dw']['G3399'], list):
        raise ValueError('地温数据缺失或格式错误')
    
    dw_values = station[0]['dw']['G3399']
    dw_last = dw_values[-1]
    
    # 验证数值有效性
    try:
        lw_last = float(lw_last)
        dw_last = float(dw_last)
    except (ValueError, TypeError):
        raise ValueError('露温或地温数据无效')
    
    # 计算差值
    diff = lw_last - dw_last
    
    # 颜色映射规则
    color_map = {
        'green': '#00ff00',
        'blue': '#0000ff',
        'yellow': '#ffff00',
        'orange': '#ff9900',
        'red': '#ff0000'
    }
    
    if diff <= -1:
        color = color_map['green']
        description = '不会出现回南天'
    elif -1 < diff < -0.5:
        color = color_map['blue']
        description = '不会出现回南天'
    elif -0.5 <= diff <= 0:
        color = color_map['yellow']
        description = '有出现回南天的可能'
    elif 0 < diff < 2:
        color = color_map['orange']
        description = '出现回南天的可能性很大'
    else:
        color = color_map['red']
        description = '可能出现严重的回南天'
    
    # 构建结果
    result = {
        'huinan': round(diff, 1),
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'color': color,
        'description': description,
        'last_values': {
            '露温': lw_last,
            '地温': dw_last
        }
    }
    
    # 保存到JSON文件
    with open('huinan.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print(json.dumps(result, ensure_ascii=False, indent=4))
    
except requests.exceptions.RequestException as e:
    print(json.dumps({'error': f'请求错误: {str(e)}'}, ensure_ascii=False))
except (ValueError, json.JSONDecodeError) as e:
    print(json.dumps({'error': f'数据处理错误: {str(e)}'}, ensure_ascii=False))
except Exception as e:
    print(json.dumps({'error': f'未知错误: {str(e)}'}, ensure_ascii=False))
