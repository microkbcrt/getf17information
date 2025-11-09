import requests
import json

def fetch_and_parse_alarm_data():
    # API URL
    url = "https://app.gjzwfw.gov.cn/fwmhapp/qixiang/interfaces/findWarnCapByElement.do"
    
    # 1. === 关键改动：定义前端JS所需的精确预警类型 ===
    # 这个列表的元素必须与 JS 文件中 alarmIconsMap 的键完全一致
    alarm_keywords = [
        '台风白色', '台风蓝色', '台风黄色', '台风橙色', '台风红色', 
        '暴雨黄色', '暴雨橙色', '暴雨红色', 
        '高温黄色', '高温橙色', '高温红色', 
        '寒冷黄色', '寒冷橙色', '寒冷红色', 
        '大雾黄色', '大雾橙色', '大雾红色', 
        '灰霾黄色', 
        '雷雨大风蓝色', '雷雨大风黄色', '雷雨大风橙色', '雷雨大风红色', 
        '道路结冰黄色', '道路结冰橙色', '道路结冰红色', 
        '冰雹橙色', '冰雹红色', 
        '森林火险黄色', '森林火险橙色', '森林火险红色'
    ]
    
    # 根据 F12 抓包结果，构造完全一致的请求体
    payload = {
        'areaCode': '440000', # 广东省代码
        'warnLevel': 'RED,BLUE,YELLOW,Orange,UNKOWN',
        'warnEvent': 'A'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    print("开始查询全省预警信息...")

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        all_alarms_raw = response.json()
        
        if not isinstance(all_alarms_raw, list):
            print(f"API未返回预期的列表格式。响应: {response.text}")
            return
        print(f"成功获取全省 {len(all_alarms_raw)} 条预警记录。")

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"获取或解析数据失败: {e}")
        return
            
    # 处理预警取消状态
    canceled_ids = set()
    for alarm_item in all_alarms_raw:
        if alarm_item.get('msgType') == 'Cancel':
            canceled_id = alarm_item.get('referencesInfo')
            if canceled_id:
                canceled_ids.add(canceled_id)
    
    print(f"分析完成：发现 {len(canceled_ids)} 条取消记录。开始筛选 '荔湾区' 的有效预警并适配前端格式...")
    
    target_area = "荔湾"
    area_alarms = []
    
    # 筛选并适配数据
    for alarm_item in all_alarms_raw:
        # 必须是生效的预警，且未被取消
        is_active = (alarm_item.get('msgType') in ['Alert', 'Update'] and 
                     alarm_item.get('identifier') not in canceled_ids)

        if not is_active:
            continue

        # 发布单位必须包含目标区域
        sender = alarm_item.get('sender', '')
        if target_area not in sender:
            continue
            
        # 2. === 关键改动：从 headline 中匹配并提取标准 alarmType ===
        headline = alarm_item.get('headline', '')
        matched_alarm_type = None
        for keyword in alarm_keywords:
            if keyword in headline:
                matched_alarm_type = keyword
                break # 找到第一个匹配就停止，避免混淆

        # 如果成功匹配到了标准类型，才进行处理
        if matched_alarm_type:
            content = alarm_item.get('description', '无详细信息')
            
            # 使用匹配到的 keyword 作为 alarmType
            area_alarms.append({
                "area": target_area,
                "alarmType": matched_alarm_type,
                "meaning": content,
                "guidelines": content
            })
    
    # 保存为JSON文件
    try:
        with open("alarmcontent.json", "w", encoding="utf-8") as f:
            json.dump(area_alarms, f, ensure_ascii=False, indent=4)
        print(f"成功为 '{target_area}' 保存 {len(area_alarms)} 条适配前端的生效预警信息到 alarmcontent.json")
        if len(area_alarms) == 0:
            print(f"提示: '{target_area}' 当前没有任何与前端匹配的生效预警信息。")
    except Exception as e:
        print(f"保存文件失败: {e}")

if __name__ == "__main__":
    fetch_and_parse_alarm_data()
