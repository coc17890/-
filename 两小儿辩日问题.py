import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from skyfield.api import load, wgs84
from skyfield import almanac
import numpy as np
import pandas as pd

def show_custom_messagebox(title, message, is_error=False, font_size=14):
    box = tk.Toplevel()
    box.title(title)
    box.geometry("450x420")
    box.grab_set()
    label = tk.Label(box, text=message, font=("Microsoft YaHei", font_size), wraplength=380, justify="left", fg=("red" if is_error else "black"))
    label.pack(padx=20, pady=30)
    btn = tk.Button(box, text="关闭", font=("Microsoft YaHei", font_size), command=box.destroy)
    btn.pack(pady=10)
    box.transient(root)
    box.wait_window()

# 计算地表观测者到太阳的精确距离（公里）
def get_surface_distance(lat, lon, dt):
    ts = load.timescale()
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    eph = load('de421.bsp')
    observer = eph['earth'] + wgs84.latlon(lat, lon)
    sun = eph['sun']
    return observer.at(t).observe(sun).distance().km

# 计算指定地点的日出和上中天时间
def calculate_sun_events(lat, lon, date):    
    # 1. 计算地方时与UTC的时差
    offset = timedelta(hours=lon / 15)
    # 2. 将地方时的0:00和23:59:59转换为UTC
    local_start = datetime(date.year, date.month, date.day, 0, 0, 0)
    local_end = datetime(date.year, date.month, date.day, 23, 59, 59)
    utc_start = local_start - offset
    utc_end = local_end - offset

    ts = load.timescale()
    t0 = ts.utc(utc_start.year, utc_start.month, utc_start.day, utc_start.hour, utc_start.minute, utc_start.second)
    t1 = ts.utc(utc_end.year, utc_end.month, utc_end.day, utc_end.hour, utc_end.minute, utc_end.second)
    eph = load('de421.bsp')
    location = wgs84.latlon(lat, lon)
    
    # 计算日出日落时间
    f = almanac.sunrise_sunset(eph, location)
    times, events = almanac.find_discrete(t0, t1, f)
    
    # 提取日出时间
    sunrise_time = None
    for t, e in zip(times, events):
        if e == 1:  # 日出事件
            sunrise_time = t
            break
    
    # 计算上中天时间（太阳最高点）
    offset1=timedelta(hours=7) 
    f_transit = almanac.meridian_transits(eph, eph['sun'], location)
    transit_times, transit_events = almanac.find_discrete(t0+offset1, t1-offset1, f_transit) #缩短查找范围，使得该区间内的中天为上中天
    transit_time = transit_times[0] if len(transit_times) > 0 else None
    
    # 检查极昼/极夜
    is_polar_day = False
    is_polar_night = False
    
    # 检查是否有日出事件
    has_sunrise = any(e == 1 for e in events)
    
    if not has_sunrise:
        # 没有日出事件，检查是极昼还是极夜
        if f(t0) == 1:  # 太阳在地平线上
            is_polar_day = True
        else:
            is_polar_night = True
    
    return sunrise_time, transit_time, is_polar_day, is_polar_night

#计算距离差值d
def calculate_distance_difference(lat, lon, current_date):
    sunrise_time, transit_time, is_polar_day, is_polar_night = calculate_sun_events(lat, lon, current_date)
    d = 0
    if is_polar_day or is_polar_night:
        # 极昼或极夜，d=0
        d = 0
        sunrise_dist = 0
        if transit_time is not None:
            transit_dt = transit_time.utc_datetime()
            noon_dist = get_surface_distance(lat, lon, transit_dt)
        else:
            noon_dist = 0
    elif sunrise_time is not None and transit_time is not None:
        # 将skyfield时间对象转换为datetime
        sunrise_dt = sunrise_time.utc_datetime()
        transit_dt = transit_time.utc_datetime()
        
        # 计算日出和上中天时的地表距离
        sunrise_dist = get_surface_distance(lat, lon, sunrise_dt)
        noon_dist = get_surface_distance(lat, lon, transit_dt)
        
        # 计算差值d (日出距离 - 正午距离)
        d = sunrise_dist - noon_dist
    else:
        # 无法计算，设为0
        d = 0
        sunrise_dist = 0
        noon_dist = 0

    return d , sunrise_dist , noon_dist , sunrise_time, transit_time, is_polar_day, is_polar_night

# 计算距离差值d并绘制趋势，并用表格的形式输出每天日出时距离，正午时距离，以及d值
def plot_distance_difference():
    try:
        lat = float(lat_entry.get())
        lon = float(lon_entry.get())
        year = int(year_entry.get())
        
        if not (-90 <= lat <= 90):
            raise ValueError("纬度必须在-90到90之间")
        if not (-180 <= lon <= 180):
            raise ValueError("经度必须在-180到180之间")
        if year < 1900 or year > 2100:
            raise ValueError("年份必须在1900到2100之间")
            
    except ValueError as e:
        show_custom_messagebox("输入错误", str(e), is_error=True, font_size=16)
        return
    
    # 创建进度条
    progress_bar.pack(pady=10)
    progress_label.pack(pady=5)
    root.update_idletasks()
    
    dates = []
    d_values = []  # 日出距离 - 正午距离
    sunrise_dists = []  # 存储日出距离
    sunrise_time_strs = []  # 存储日出时间字符串
    sunrise_utc_times=[]  
    transit_time_strs = []  # 存储正午时间字符串
    transit_utc_times=[]
    noon_dists = []  # 存储正午距离
    
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    total_days = (end_date - start_date).days + 1
    
    for i, day in enumerate(range(total_days)):
        current_date = start_date + timedelta(days=day)
        
        # 更新进度
        progress = (i + 1) / total_days * 100
        progress_bar['value'] = progress
        progress_label.config(text=f"计算中: {progress:.1f}% (日期: {current_date.strftime('%Y-%m-%d')})",font=("Microsoft YaHei", 10))
        root.update_idletasks()
        
        d,sunrise_dist,noon_dist,sunrise_time, transit_time, is_polar_day, is_polar_night =calculate_distance_difference(lat, lon, current_date)
        
        # 计算地方时与UTC的时差
        offset= timedelta(hours=lon / 15)
        if is_polar_day or is_polar_night:
            sunrise_time_str = "极昼" if is_polar_day else "极夜"
            sunrise_utc_time_str = "极昼" if is_polar_day else "极夜"
        else:
            # 日出时间
            sunrise_time_utc = sunrise_time.utc_datetime() if sunrise_time is not None else None
            sunrise_time_local = sunrise_time_utc + offset if sunrise_time_utc is not None else None
            sunrise_time_str = sunrise_time_local.strftime('%H:%M:%S') if sunrise_time_local is not None else "无日出时间"
            sunrise_utc_time_str = sunrise_time_utc.strftime('%H:%M:%S') if sunrise_time_utc is not None else "无日出时间"

        # 正午时间
        transit_time_utc = transit_time.utc_datetime() if transit_time is not None else None
        transit_time_local = transit_time_utc + offset if transit_time_utc is not None else None
        transit_time_str = transit_time_local.strftime('%H:%M:%S') if transit_time_local is not None else "无正午时间"
        transit_utc_time_str = transit_time_utc.strftime('%H:%M:%S') if transit_time_utc is not None else "无正午时间"

        # 只显示current_date的年月日
        current_date = current_date.strftime('%Y-%m-%d')
        # 将结果添加到列表中    
        dates.append(current_date)
        d_values.append(d)
        sunrise_dists.append(sunrise_dist)
        noon_dists.append(noon_dist)
        sunrise_time_strs.append(sunrise_time_str)
        sunrise_utc_times.append(sunrise_utc_time_str)
        transit_time_strs.append(transit_time_str)
        transit_utc_times.append(transit_utc_time_str)

    # 用excel表格的形式输出每天日出时距离，正午时距离，以及d值
    df = pd.DataFrame({
        '日期': dates,
        '日出时间 (地方平时)': sunrise_time_strs,
        '日出时间 (UTC+0)':sunrise_utc_times,
        '日出距离 (km)': sunrise_dists,
        '正午时间 (地方平时)': transit_time_strs,
        '正午时间 (UTC+0)':transit_utc_times,
        '正午距离 (km)': noon_dists,
        '距离差值 d (km)': d_values
    })
    df.to_excel(f"sun_distance_analysis_latitude_{lat}_longitude_{lon}_year_{year}.xlsx", index=False)
    show_custom_messagebox("计算完成", f"已将结果保存到 'sun_distance_analysis_latitude_{lat}_longitude_{lon}_year_{year}.xlsx' 文件中", font_size=16)

    # 绘制图表
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图形和子图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # 图1：距离差值变化趋势
    ax1.plot(dates, d_values, color='royalblue', label='距离差值 d')
    ax1.fill_between(dates, d_values, 0, where=(np.array(d_values) > 0), 
                    facecolor='lightcoral', alpha=0.5, interpolate=True)
    ax1.fill_between(dates, d_values, 0, where=(np.array(d_values) < 0), 
                    facecolor='lightgreen', alpha=0.5, interpolate=True)
    
    ax1.axhline(0, color='gray', linestyle='--', alpha=0.7)
    ax1.set_ylabel("距离差值 d (公里)", fontsize=12)
    ax1.set_title(f"{year}年 日出与正午太阳距离差值变化趋势\n(纬度: {lat}°, 经度: {lon}°)", fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 图2：日出和正午距离对比
    ax2.plot(dates, sunrise_dists, color='darkorange', label='日出距离', alpha=0.7)
    ax2.plot(dates, noon_dists, color='darkblue', label='正午距离', alpha=0.7)
    
    # 计算平均距离并绘制参考线
    avg_sunrise = np.mean(sunrise_dists)
    avg_noon = np.mean(noon_dists)
    ax2.axhline(avg_sunrise, color='darkorange', linestyle='--', alpha=0.5)
    ax2.axhline(avg_noon, color='darkblue', linestyle='--', alpha=0.5)
    
    ax2.set_xlabel("日期", fontsize=12)
    ax2.set_ylabel("距离 (公里)", fontsize=12)
    ax2.set_title("日出与正午太阳距离对比", fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 添加差值范围说明
    min_d = np.min(d_values)
    max_d = np.max(d_values)
    ax1.text(0.01, 0.95, f"d值范围: {min_d:.1f} to {max_d:.1f} km", 
             transform=ax1.transAxes, fontsize=10, verticalalignment='top')
    
    plt.tight_layout()
    plt.show()
    
    # 隐藏进度条（防止窗口已销毁时报错）
    try:
        if progress_bar.winfo_exists():
            progress_bar.pack_forget()
        if progress_label.winfo_exists():
            progress_label.pack_forget()
    except Exception:
        pass

# 计算某地某天d值,并显示结果
def calculate_single_day_d():
    try:
        lat = float(lat_entry.get())
        lon = float(lon_entry.get())
        year = int(single_year_entry.get())
        month = int(single_month_entry.get())
        day = int(single_day_entry.get())
        if not (-90 <= lat <= 90):
            raise ValueError("纬度必须在-90到90之间")
        if not (-180 <= lon <= 180):
            raise ValueError("经度必须在-180到180之间")
        if year < 1900 or year > 2100:
            raise ValueError("年份必须在1900到2100之间")
        if not (1 <= month <= 12):
            raise ValueError("月份必须在1到12之间")
        if not (1 <= day <= 31):
            raise ValueError("日期必须在1到31之间")
        dt = datetime(year, month, day)
    except Exception as e:
        show_custom_messagebox("输入错误", str(e), is_error=True, font_size=16)
        return
    d, sunrise_dist, noon_dist ,sunrise_time, transit_time, is_polar_day, is_polar_night= calculate_distance_difference(lat, lon, dt)

    # 计算地方时与UTC的时差
    offset= timedelta(hours=lon / 15)
    if is_polar_day or is_polar_night:
        sunrise_time_str = "极昼" if is_polar_day else "极夜"
        sunrise_time_UTC0_str = "极昼" if is_polar_day else "极夜"
    else:
        #将日出时间转换为地方时再输出
        sunrise_time_UTC0 = sunrise_time.utc_datetime() if sunrise_time is not None else None
        sunrise_time = sunrise_time_UTC0 + offset if sunrise_time is not None else None
        
        sunrise_time_str = sunrise_time.strftime('%H:%M:%S') if sunrise_time is not None else "无日出时间"
        sunrise_time_UTC0_str = sunrise_time_UTC0.strftime('%H:%M:%S') if sunrise_time_UTC0 is not None else "无日出时间(UTC+0)"

    # 将正午时间转换为地方时再输出
    transit_time_UTC0 = transit_time.utc_datetime() if transit_time is not None else None
    transit_time = transit_time_UTC0 + offset if transit_time is not None else None

    transit_time_str = transit_time.strftime('%H:%M:%S') if transit_time is not None else "无正午时间"
    transit_time_UTC0_str = transit_time_UTC0.strftime('%H:%M:%S') if transit_time_UTC0 is not None else "无正午时间(UTC+0)"

    msg = (f"{year}年{month}月{day}日\n"
           f"纬度: {lat}° 经度: {lon}°\n"
           f"日出时间（地方平时）: {sunrise_time_str}\n"
           f"日出时间（UTC+0）: {sunrise_time_UTC0_str}\n"
           f"正午时间（地方平时）: {transit_time_str}\n"
           f"正午时间（UTC+0）: {transit_time_UTC0_str}\n"
           f"日出距离: {sunrise_dist:.2f} km\n"
           f"正午距离: {noon_dist:.2f} km\n"
           f"d = 日出距离 - 正午距离 = {d:.2f} km")
    show_custom_messagebox("单日d值计算结果", msg, font_size=16)

if __name__ == "__main__":
    # 初始化Tkinter窗口
    root = tk.Tk()
    root.title("两小儿辩日问题分析")
    root.geometry("500x620")
    root.resizable(False, False) # 禁止调整窗口大小

    # 设置样式
    style = ttk.Style()
    style.configure("TFrame", background="#f0f0f0")
    style.configure("TLabel", background="#f0f0f0", font=("Microsoft YaHei", 10))
    style.configure("TButton", font=("Microsoft YaHei", 10, "bold"))

    # 主框架
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 标题
    title_label = ttk.Label(main_frame, text="地表观测者日出与正午至太阳距离计算", font=("Microsoft YaHei", 16, "bold"))
    title_label.pack(pady=10)

    # 输入框架
    input_frame = ttk.Frame(main_frame)
    input_frame.pack(fill=tk.X, pady=10)

    # 纬度输入
    lat_frame = ttk.Frame(input_frame)
    lat_frame.pack(fill=tk.X, pady=5)
    ttk.Label(lat_frame, text="纬度 (°):").pack(side=tk.LEFT, padx=(0, 10))
    lat_entry = ttk.Entry(lat_frame, width=15)
    lat_entry.pack(side=tk.LEFT)
    lat_entry.insert(0, "40.0")  # 默认值

    # 经度输入
    lon_frame = ttk.Frame(input_frame)
    lon_frame.pack(fill=tk.X, pady=5)
    ttk.Label(lon_frame, text="经度 (°):").pack(side=tk.LEFT, padx=(0, 10))
    lon_entry = ttk.Entry(lon_frame, width=15)
    lon_entry.pack(side=tk.LEFT)
    lon_entry.insert(0, "116.0")  # 默认值（北京）


    # 年份输入（趋势图用）
    year_frame = ttk.Frame(input_frame)
    year_frame.pack(fill=tk.X, pady=5)
    ttk.Label(year_frame, text="年份(趋势):").pack(side=tk.LEFT, padx=(0, 10))
    year_entry = ttk.Entry(year_frame, width=10)
    year_entry.pack(side=tk.LEFT)
    year_entry.insert(0, str(datetime.now().year))  # 默认当前年份

    # 单日d值计算输入
    single_frame = ttk.LabelFrame(main_frame, text="单日d值计算", padding=10)
    single_frame.pack(fill=tk.X, pady=10)
    sf1 = ttk.Frame(single_frame)
    sf1.pack(fill=tk.X, pady=2)
    ttk.Label(sf1, text="年:").pack(side=tk.LEFT)
    single_year_entry = ttk.Entry(sf1, width=6)
    single_year_entry.pack(side=tk.LEFT, padx=(0, 10))
    single_year_entry.insert(0, str(datetime.now().year))
    ttk.Label(sf1, text="月:").pack(side=tk.LEFT)
    single_month_entry = ttk.Entry(sf1, width=4)
    single_month_entry.pack(side=tk.LEFT, padx=(0, 10))
    single_month_entry.insert(0, str(datetime.now().month))
    ttk.Label(sf1, text="日:").pack(side=tk.LEFT)
    single_day_entry = ttk.Entry(sf1, width=4)
    single_day_entry.pack(side=tk.LEFT)
    single_day_entry.insert(0, str(datetime.now().day))
    single_btn = ttk.Button(single_frame, text="计算该日d值", command=calculate_single_day_d)
    single_btn.pack(pady=5)

    # 说明标签
    info_label = ttk.Label(main_frame, 
                        text="d = 日出时距离 - 正午时距离\n极昼或极夜时令 d=0\n精确计算一年中每一天d值的变化趋势",
                        font=("KaiTi", 14),  #将字体改为楷体
                        justify=tk.CENTER)
    info_label.pack(pady=10)

    # 按钮
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=15)
    plot_button = ttk.Button(button_frame, text="计算并绘图", command=plot_distance_difference)
    plot_button.pack()

    # 进度条
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill=tk.X, pady=5)
    progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
    progress_label = ttk.Label(progress_frame, text="准备计算...")

    # 底部信息
    footer_label = ttk.Label(main_frame, text="数据来源：NASA JPL DE421 星历 | 精确地表距离计算", font=("Microsoft YaHei", 9))
    footer_label.pack(side=tk.BOTTOM, pady=5)

    root.mainloop()

#--終わり--