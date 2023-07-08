# python3 tinypng 图片压缩脚本 python3 compress_images.py 运行
import os
import tinify
import time
import threading

# 添加一个全局变量来控制主循环
exit_flag = False

# 添加一个函数来在新线程中检测用户输入
def check_exit():
    global exit_flag
    while True:
        if input("输入 'q' 退出程序：") == 'q':
            exit_flag = True
            break

# 启动新线程检查退出指令
threading.Thread(target=check_exit).start()

# 存储所有的 TinyPNG API keys
tinify_keys = ["xxxx1","xxxx2"]

# 每n次之后，输出当前使用的key和用量
n = 10

# 图片路径数组
image_paths = ["xxxx/res/drawable-xxhdpi/"]

# 可处理的文件类型
allowed_file_types = [".jpg", ".png"]

# 需要跳过的图片名称
skip_images = []

# 当前使用的 TinyPNG API key 的序号
key_index = 0
tinify.key = tinify_keys[key_index]

# 遍历所有路径，如果路径是目录，则遍历该目录下的所有文件
all_files = []
for path in image_paths:
    if os.path.isfile(path):
        all_files.append(path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                all_files.append(os.path.join(root, file))

# 计算图片总数
total_images = len(all_files)

# 初始化计数器
processed_images = 0
successful_images = 0

# 记录开始时间
start_time = time.time()

for i, img in enumerate(all_files, start=1):
    # 检查是否需要退出
    if exit_flag:
        print("接收到退出指令，正在退出...")
        break
    ext = os.path.splitext(img)[1]
    if ext.lower() not in allowed_file_types:
        print(f'跳过不支持的文件类型：{img}')
        continue
    # 检查图片名称是否在 skip_images 列表中
    if os.path.basename(img) in skip_images:
        print(f'跳过指定命名的图片：{img}')
        continue
    processed_images += 1  # 更新已处理的图片数量
    while True:
        try:
            source = tinify.from_file(img)
            source.to_file(img)  # 在同一级目录下覆盖原图片
            print(f'已完成：{img} ({i}/{total_images})')  # 输出已完成的图片名称和进度
            successful_images += 1  # 更新成功的图片数量
            # 检查是否达到了 n 次压缩
            if successful_images % n == 0:
                try:
                    print(f"当前使用的 key：{tinify_keys[key_index]}，已使用：{tinify.compression_count}")
                except tinify.Error as e:
                    print(f"获取当前 key 的用量失败，原因：{str(e)}")
            break  # 如果图片压缩成功，退出循环
        except tinify.AccountError as e:  # 捕获账户错误
            if "Your monthly limit has been exceeded" in str(e):
                print(f"当前使用的key已用完 key：{tinify_keys[key_index]}")
                key_index += 1  # 切换到下一个 API key
                if key_index >= len(tinify_keys):
                    print("所有的 API keys 的月限额都已用完。")
                    exit(1)  # 退出程序
                else:
                    tinify.key = tinify_keys[key_index]
                    print(f"切换到下一个 API key：{tinify.key}")
            else:
                print(f'压缩失败：{img}，原因：{str(e)}')
                break  # 如果错误不是月限额超过，退出循环
        except tinify.Error as e:  # 捕获其他错误
            print(f'压缩失败：{img}，原因：{str(e)}')
            break  # 如果出现错误，退出循环

# 计算并输出耗时和处理的图片数量
end_time = time.time()
elapsed_time = end_time - start_time
print(f"所有图片处理完毕，耗时：{elapsed_time} 秒。")
print(f"已处理 {processed_images} 张图片，成功压缩 {successful_images} 张。")
