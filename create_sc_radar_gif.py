import requests
from PIL import Image
from datetime import datetime, timedelta, timezone
import os

def create_south_china_radar_gif():
    """
    下载国家气象中心最新的10张华南雷达拼图并制作成GIF动图。
    """
    print("开始执行华南雷达拼图GIF生成脚本...")

    # 核心修改点：NMC使用UTC时间，所以我们获取当前的UTC时间
    utc_tz = timezone.utc
    now = datetime.now(utc_tz)

    # 雷达图通常每6分钟更新一次，计算最新时间点
    minute = now.minute - (now.minute % 6)
    latest_time = now.replace(minute=minute, second=0, microsecond=0)

    image_urls = []
    # 从最新时间往前推10次，生成URL列表
    for i in range(10):
        current_time = latest_time - timedelta(minutes=i * 6)
        
        # 根据NMC的URL规则生成路径和文件名
        date_path = current_time.strftime("%Y/%m/%d")
        time_filename = current_time.strftime("%Y%m%d%H%M%S")
        
        url = (f"https://image.nmc.cn/product/{date_path}/RDCP/"
               f"SEVP_AOC_RDCP_SLDAS3_ECREF_ASCN_L88_PI_{time_filename}000.PNG")
        
        image_urls.append(url)

    # 反转列表，确保GIF按时间顺序播放
    image_urls.reverse()

    downloaded_files = []
    image_objects = []
    # 创建一个临时文件夹
    if not os.path.exists("radar_images_sc"):
        os.makedirs("radar_images_sc")

    print("开始下载华南雷达拼图...")
    for i, url in enumerate(image_urls):
        try:
            # 增加 User-Agent 模拟浏览器访问，提高成功率
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, timeout=15, headers=headers)
            
            if response.status_code == 200:
                # 文件名中的':'在Windows中是非法字符，需要替换
                image_path = os.path.join("radar_images_sc", f"radar_{i:02d}.png")
                with open(image_path, "wb") as f:
                    f.write(response.content)
                downloaded_files.append(image_path)
                print(f"成功下载图片: {url}")
            else:
                print(f"下载失败，状态码: {response.status_code}, URL: {url}")
        except requests.exceptions.RequestException as e:
            print(f"下载时发生错误: {e}, URL: {url}")

    if not downloaded_files:
        print("没有下载到任何图片，无法生成GIF。")
        if os.path.exists("radar_images_sc"):
            os.rmdir("radar_images_sc")
        return

    print("\n开始生成GIF动图...")
    try:
        # 使用 Pillow 打开所有下载的图片
        for file_path in downloaded_files:
            image_objects.append(Image.open(file_path))

        if image_objects:
            image_objects[0].save(
                'sc_radar.gif',  # 输出文件名为 sc_radar.gif
                save_all=True,
                append_images=image_objects[1:],
                duration=200,    # 200毫秒
                loop=0           # 无限循环
            )
            print("成功生成GIF文件: sc_radar.gif")
        else:
            print("图片对象列表为空，无法生成GIF。")

    except Exception as e:
        print(f"生成GIF时发生错误: {e}")
    finally:
        for img in image_objects:
            img.close()

    print("\n开始清理已下载的图片...")
    for file_path in downloaded_files:
        try:
            os.remove(file_path)
            print(f"已删除: {file_path}")
        except OSError as e:
            print(f"删除文件时出错: {e.path} - {e.strerror}")
    
    try:
        os.rmdir("radar_images_sc")
        print("已删除文件夹: radar_images_sc")
    except OSError as e:
        print(f"删除文件夹时出错: {e.path} - {e.strerror}")

    print("\n脚本执行完毕。")

if __name__ == "__main__":
    create_south_china_radar_gif()
