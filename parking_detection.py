import cv2
import numpy as np
import json
import os
from playsound3 import playsound3

# 全局变量
parking_spots = []
current_spot = []
drawing = False

def draw_parking_spots(event, x, y, flags, param):
    global current_spot, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        current_spot = [(x, y)]
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        if len(current_spot) > 0 and param is not None:
            frame_copy = param.copy()
            cv2.rectangle(frame_copy, current_spot[0], (x, y), (0, 255, 0), 2)
            cv2.imshow("Parking Spot Detection", frame_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        current_spot.append((x, y))
        parking_spots.append({"name": f"Spot{len(parking_spots) + 1}", "coordinates": [current_spot[0], (current_spot[0][0], current_spot[1][1]), current_spot[1], (current_spot[1][0], current_spot[0][1])]})
        current_spot = []

    # 检测删除模式下的鼠标点击事件
    if event == cv2.EVENT_LBUTTONDOWN and (flags & cv2.EVENT_FLAG_CTRLKEY or flags & cv2.EVENT_FLAG_ALTKEY):
        print(f"检测到删除模式: flags={flags}")
        for i, spot in enumerate(parking_spots):
            pts = np.array(spot["coordinates"], np.int32)
            pts = pts.reshape((-1, 1, 2))
            if cv2.pointPolygonTest(pts, (x, y), False) >= 0:
                del parking_spots[i]
                print(f"已删除车位: {spot['name']}")
                # 刷新显示
                ret, frame = cap.read()
                if not ret:
                    print("无法读取摄像头帧数据，请检查摄像头连接")
                    break
                if ret:
                    frame_copy = frame.copy()
        for spot in parking_spots:
            pts = np.array(spot["coordinates"], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame_copy, [pts], True, (0, 255, 0), 2)
            cv2.putText(frame_copy, spot["name"], (pts[0][0][0], pts[0][0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow("Parking Spot Detection", frame_copy)
        # 强制刷新窗口
        cv2.waitKey(1)

def save_parking_spots():
    print(f"当前车位标记数量: {len(parking_spots)}")
    print(f"车位标记内容: {parking_spots}")  # 打印详细内容
    if not parking_spots:
        print("没有车位标记可保存，请先标记车位！")
        return
    try:
        print("正在保存车位标记...")
        file_path = os.path.join(os.path.dirname(__file__), "parking_spots.json")  # 使用绝对路径
        print(f"保存路径: {file_path}")
        with open(file_path, "w") as f:
            json.dump(parking_spots, f, indent=4)
            f.flush()  # 确保数据写入磁盘
            print(f"成功保存 {len(parking_spots)} 个车位标记到 {file_path}")
            print("文件内容预览:", json.dumps(parking_spots, indent=2))
    except PermissionError:
        print("错误：无文件写入权限，请检查目录权限！")
    except Exception as e:
        print(f"保存失败: {e}")
    finally:
        print("保存操作完成")

def delete_parking_spot():
    if not parking_spots:
        print("没有车位标记可删除！")
        return
    print(f"当前车位标记数量: {len(parking_spots)}")
    print(f"车位标记内容: {parking_spots}")
    deleted_spot = parking_spots.pop()  # 删除最后一个车位
    print(f"已删除车位: {deleted_spot}")
    save_parking_spots()  # 自动保存更新后的列表

def main():
    # 初始化摄像头
    for i in range(3):  # 尝试多个摄像头索引
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
            cv2.namedWindow("Parking Spot Detection")
            print(f"摄像头 {i} 初始化成功")
            break
    else:
        print("无法打开任何摄像头，请检查设备连接")
        exit(1)

    # 读取一帧图像以初始化 frame
    ret, frame = cap.read()
    if not ret:
        print("无法读取摄像头帧数据，错误代码:", cap.get(cv2.CAP_PROP_POS_MSEC))
        print("请检查摄像头连接或是否被占用")
        return
    if not ret:
        print("无法读取摄像头")
        return

    cv2.setMouseCallback("Parking Spot Detection", draw_parking_spots, param=frame)

    # 加载已保存的车位坐标（如果存在）
    try:
        with open("parking_spots.json", "r") as f:
            global parking_spots
            parking_spots = json.load(f)
            # 确保每个车位对象都有 "available" 字段
            for spot in parking_spots:
                if "available" not in spot:
                    spot["available"] = True
        print("已加载车位坐标")
    except FileNotFoundError:
        print("未找到车位坐标文件，将从头开始定义")

    print("按 'd' 键进入车位标记模式")
    print("按 's' 键保存车位坐标")
    print("按 'q' 键退出程序")

    # 调试摄像头状态
    if not cap.isOpened():
        print("摄像头未成功打开，请检查设备连接或权限")
        exit(1)
    else:
        print("摄像头已成功打开")

    while True:
        # 捕获帧
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头帧数据，请检查摄像头连接或是否被占用")
            break

        # 显示当前车位区域
        frame_copy = frame.copy()
        for spot in parking_spots:
            pts = np.array(spot["coordinates"], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame_copy, [pts], True, (0, 255, 0), 2)
            cv2.putText(frame_copy, spot["name"], (pts[0][0][0], pts[0][0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 显示结果
        cv2.imshow("Parking Spot Detection", frame_copy)

        # 模拟车位占用报警（测试用）
        if len(parking_spots) > 0 and not any(spot["available"] for spot in parking_spots):
            print("警告：车位被占用！")
            cv2.putText(frame_copy, "警告：车位被占用！", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Parking Spot Detection", frame_copy)
            # 播放系统声音（仅限 macOS）
            import os
            os.system("say '车位被占用'")

        # 检测按键
        key = cv2.waitKey(1) & 0xFF
        print(f"检测到按键: {chr(key) if key != 255 else '无按键'}")  # 调试按键事件
        if key == ord('q'):
            break
        elif key == ord('s'):
            print("正在保存车位标记...")
            save_parking_spots()
            print("请检查 parking_spots.json 文件是否生成")
        elif key == ord('d'):
            print("进入车位标记模式，请用鼠标拖拽绘制车位区域")
        elif key == ord('r'):
            delete_parking_spot()
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("无法读取摄像头帧数据，请检查摄像头连接")
                    break
                if not ret:
                    print("无法读取摄像头")
                    break

                frame_copy = frame.copy()
                for spot in parking_spots:
                    pts = np.array(spot["coordinates"], np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(frame_copy, [pts], True, (0, 255, 0), 2)
                    cv2.putText(frame_copy, spot["name"], (pts[0][0][0], pts[0][0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                cv2.imshow("Parking Spot Detection", frame_copy)
                key = cv2.waitKey(1) & 0xFF
                print(f"检测到按键: {chr(key) if key != 255 else '无按键'}")  # 调试按键事件
                if key == ord('q') or key == ord('d'):
                    break

        elif key == ord('r'):
            print("进入删除模式，请点击要删除的车位区域")
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("无法读取摄像头帧数据，请检查摄像头连接")
                    break
                if not ret:
                    print("无法读取摄像头")
                    break

                frame_copy = frame.copy()
                for spot in parking_spots:
                    pts = np.array(spot["coordinates"], np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(frame_copy, [pts], True, (0, 0, 255), 2)
                    cv2.putText(frame_copy, spot["name"], (pts[0][0][0], pts[0][0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                cv2.imshow("Parking Spot Detection", frame_copy)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('r'):
                    break

                # 检测鼠标点击事件
                if cv2.getWindowProperty("Parking Spot Detection", cv2.WND_PROP_VISIBLE) < 1:
                    break

                # 模拟鼠标点击事件
                if cv2.waitKey(1) & 0xFF == ord('c'):
                    # 获取鼠标点击位置
                    x, y = cv2.getMousePos()
                    for i, spot in enumerate(parking_spots):
                        pts = np.array(spot["coordinates"], np.int32)
                        if cv2.pointPolygonTest(pts, (x, y), False) >= 0:
                            del parking_spots[i]
                            print(f"已删除车位: {spot['name']}")
                            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()