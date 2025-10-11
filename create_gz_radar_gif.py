import requests
from PIL import Image
from datetime import datetime, timedelta, timezone
import os

def create_weather_radar_gif():
    """
    下载广州天气官网最新的10张雷达图并制作成GIF动图。
    直接使用 Pillow 库生成 GIF 以精确控制帧率。
    """
    print("开始执行脚本...")

    # 设置时区为北京时间 (UTC+8)
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)

    # 计算最新的雷达图发布时间点 (每6分钟)
    minute = now.minute - (now.minute % 6)
    latest_time = now.replace(minute=minute, second=0, microsecond=0)

    image_urls = []
    # 从最新时间往前推10次，生成URL列表
    for i in range(10):
        current_time = latest_time - timedelta(minutes=i * 6)
        date_str = current_time.strftime("%Y%m%d")
        time_str = current_time.strftime("%Y%m%d%H%M%S")
        url = f"http://www.tqyb.com.cn/data/swan/mcr/{date_str}/{time_str}_gz.png"
        image_urls.append(url)

    # 反转列表，确保GIF按时间顺序播放
    image_urls.reverse()

    downloaded_files = []
    image_objects = []
    # 创建一个临时文件夹
    if not os.path.exists("radar_images"):
        os.makedirs("radar_images")

    print("开始下载雷达图...")
    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                image_path = os.path.join("radar_images", f"radar_{i:02d}.png")
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
        # 清理空文件夹
        if os.path.exists("radar_images"):
            os.rmdir("radar_images")
        return

    print("\n开始生成GIF动图...")
    try:
        # 使用 Pillow 打开所有下载的图片
        for file_path in downloaded_files:
            image_objects.append(Image.open(file_path))

        # 检查是否至少有一张图片
        if image_objects:
            # 使用第一张图片作为基础，并附加余下的图片来创建GIF
            image_objects[0].save(
                'gz_radar.gif',
                save_all=True,
                append_images=image_objects[1:],
                duration=200,  # Pillow 的 duration 单位是毫秒，直接使用200
                loop=0         # 0表示无限循环
            )
            print("成功生成GIF文件: gz_radar.gif")
        else:
            print("图片对象列表为空，无法生成GIF。")

    except Exception as e:
        print(f"生成GIF时发生错误: {e}")
    finally:
        # 确保所有打开的图片对象都被关闭，以便后续删除文件
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
        os.rmdir("radar_images")
        print("已删除文件夹: radar_images")
    except OSError as e:
        print(f"删除文件夹时出错: {e.path} - {e.strerror}")

    print("\n脚本执行完毕。")

if __name__ == "__main__":
    create_weather_radar_gif()
