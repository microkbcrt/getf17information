import requests
import json
import re

def fetch_and_parse_alarm_data():
    # 目标URL
    url = "http://www.tqyb.com.cn/data/alarm/gz_areaAlarm.js"
    
    try:
        # 发送HTTP请求获取网页内容
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        print(f"成功获取网页内容，长度: {len(response.text)} 字节")
    except requests.exceptions.RequestException as e:
        print(f"无法获取网页内容，请检查链接或网络状态。错误: {e}")
        return
    
    # 提取JSON数据
    match = re.search(r'var\s+gz_areaAlarm\s*=\s*(\{.*?\});', response.text, re.DOTALL)
    if not match:
        print("无法解析网页内容，请检查网页格式。")
        return
    
    json_data = match.group(1)
    print("使用主模式匹配成功")
    
    try:
        # 将JSON字符串转换为Python字典
        data = json.loads(json_data)
        print(f"成功解析JSON数据，包含 {len(data)} 个预警类型")
    except json.JSONDecodeError as e:
        print(f"JSON解析失败，请检查网页内容格式。错误: {e}")
        return
    
    # 目标区域名称
    target_area = "荔湾"
    # 初始化目标区域预警信息列表
    area_alarms = []
    
    # 遍历所有预警类型
    for alarm_type, alarm_data in data.items():
        # 确保数据是字典类型
        if not isinstance(alarm_data, dict):
            print(f"警告: 发现非字典类型的预警数据 - 类型: {type(alarm_data)}, 键: {alarm_type}")
            continue
            
        # 获取区域列表
        areas = alarm_data.get('areas', [])
        
        # 检查目标区域是否在该预警中
        if target_area in areas:
            # 获取目标区域在列表中的索引
            area_index = areas.index(target_area)
            
            # 获取预警类型名称
            areas_a_name = alarm_data.get('areasAName', [])
            alarm_type_name = areas_a_name[area_index] if area_index < len(areas_a_name) else '未知预警类型'
            
            # 获取防御措施
            areas_guidelines = alarm_data.get('areasGuidelines', [])
            guidelines = areas_guidelines[area_index] if area_index < len(areas_guidelines) else '无防御措施'
            
            # 获取预警含义
            meaning = alarm_data.get('meaning', '未知预警含义')
            
            # 添加到结果列表
            area_alarms.append({
                "area": target_area,
                "alarmType": alarm_type_name,
                "meaning": meaning,
                "guidelines": guidelines
            })
    
    # 保存为JSON文件
    try:
        with open("alarmcontent.json", "w", encoding="utf-8") as f:
            json.dump(area_alarms, f, ensure_ascii=False, indent=4)
        print(f"成功保存 {len(area_alarms)} 条预警信息")
        if len(area_alarms) == 0:
            print(f"警告: 未找到 {target_area} 的预警信息，可能当前没有预警或网站结构已变化")
    except Exception as e:
        print(f"保存文件失败: {e}")

if __name__ == "__main__":
    fetch_and_parse_alarm_data()
