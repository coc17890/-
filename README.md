---

# Sun Distance at Sunrise and Noon: The "Two Boys Arguing About the Sun" Problem (English Version)

## Story Background & Scientific Context

The story of "Two Boys Arguing About the Sun" (两小儿辩日) comes from the ancient Chinese text "Liezi · Tang Wen". It tells of Confucius encountering two children debating whether the sun is closer at sunrise or at noon:

> Two boys argued about the sun, and even Confucius could not decide who was right.

One boy said: "When the sun rises, it looks big and close; at noon, it looks small and far, so the sun is closer in the morning." The other said: "It's cool at sunrise and hot at noon, so the sun must be closer at noon." Both had their reasons, and Confucius could not resolve the dispute.

This story reflects ancient people's keen observation and curiosity about nature. In reality, the distance between the sun and an observer on Earth does change slightly between sunrise and noon, due to Earth's rotation, revolution, shape, and atmospheric effects.

This project uses modern astronomy and NASA ephemeris data to precisely calculate the real distance from a ground observer to the sun at sunrise and noon, helping users understand the science behind this classic debate.

---

## Features

- Calculate, for any given latitude, longitude, and date:
  - The ground distance to the sun at sunrise (in kilometers)
  - The ground distance to the sun at local noon (solar transit)
  - The difference between sunrise and noon distances
- For any year, batch-calculate the daily distance difference, and generate:
  - Excel (.xlsx) table with date, sunrise/noon times (local & UTC+0), distances, and difference
  - Trend chart of distance difference over the year, and comparison chart of sunrise vs. noon distances
- Single-day calculation interface for quick queries

## Requirements

- OS: Windows / macOS / Linux
- Python: 3.7+
- Third-party libraries:
  - skyfield
  - numpy
  - pandas
  - matplotlib
  - tkinter (comes with Python standard library)

If not installed, run:

```powershell
pip install skyfield numpy pandas matplotlib
```

> Note: The `de421.bsp` ephemeris file must be in the same directory as the script, or you must specify its path in the code.

## Usage

1. Clone or download this repo. Place `两小儿辩日问题.py` and `de421.bsp` in the same folder.
2. In terminal, run:

   ```powershell
   python 两小儿辩日问题.py
   ```

3. In the GUI:
   - Enter latitude (°) and longitude (°)
   - Enter year (for trend analysis), click "计算并绘图" (Calculate & Plot) to batch-calculate and export Excel and charts
   - In the "单日 d值计算" (Single-day d value) section, enter year, month, day, and click to get the result for that day

4. Results are saved as Excel files, e.g.:

   ```text
   sun_distance_analysis_latitude_{lat}_longitude_{lon}_year_{year}.xlsx
   ```

5. You may close the progress bar window after calculation.

## File Description

- `两小儿辩日问题.py`: Main program, includes GUI, calculation, and plotting logic
- `de421.bsp`: NASA JPL solar system ephemeris file

## FAQ

- **Error: `de421.bsp` not found**: Make sure the file is in the same directory as the script, or update the path in the code.
- **No sunrise or noon time (polar day/night)**: The script will mark such days as "极昼" (polar day) or "极夜" (polar night), and set d=0.

## License

This project is licensed under the MIT License. See LICENSE for details.

# 两小儿辩日问题分析

## 两小儿辩日典故与科学背景

“两小儿辩日”出自《列子·汤问》，讲述了孔子遇到两个小孩争论太阳远近的问题：

> 两小儿辩日，孔子不能决也。

一个小孩说：“太阳刚升起时，看起来很大很近，到中午时变小变远，所以太阳早上近，中午远。”
另一个小孩则说：“太阳刚升起时天气凉，中午时很热，所以太阳早上远，中午近。”
两人各执一词，孔子也无法判断谁对谁错。

这个故事体现了古人对自然现象的朴素观察和思辨，也反映了科学探究精神。实际上，太阳在地平线附近和正午时的距离确实存在微小差异，涉及地球自转、公转、地球椭球体形状、大气折射等复杂天文物理因素。

本项目正是以现代天文学方法，结合NASA星历数据，精确模拟和计算地表观测者在日出与正午时刻与太阳的真实距离，帮助大家直观理解“两小儿辩日”背后的科学道理。

---

## 功能概览

- 计算指定纬度、经度及日期下：
  - 日出时与太阳的地表距离（以公里为单位）
  - 正午（太阳上中天）时与太阳的地表距离（以公里为单位）
  - 日出时距离与正午时距离之差
- 针对任意一年，批量计算该年每天的距离差值，并生成：
  - Excel 表格（.xlsx），包含日期、日出/正午时间（地方平时与 UTC+0）、对应距离及差值
  - 距离差值随日期变化趋势图，以及日出距离和正午距离对比图
- 提供单日计算界面，可快速查询某天的日出/正午时间及距离差值

## 环境依赖

- 操作系统：Windows / macOS / Linux
- Python：3.7+
- 第三方库：
  - skyfield
  - numpy
  - pandas
  - matplotlib
  - tkinter（随 Python 标准库自带）

若尚未安装，请使用以下命令安装：

```powershell
pip install skyfield numpy pandas matplotlib
``` 

> 注意：`de421.bsp` 星历文件需与脚本放在同一目录，或在脚本中自行指定完整路径。

## 使用说明

1. 克隆或下载本仓库，将 `两小儿辩日问题.py` 与 `de421.bsp` 放在同一目录。
2. 进入项目目录，在终端运行：

   ```powershell
   python 两小儿辩日问题.py
   ```

3. 在弹出的 GUI 界面中：
   - 输入观测地点的纬度 (°) 和经度 (°)
   - 年份输入（趋势图用），点击“计算并绘图”即可批量计算并导出 Excel 文件及绘制统计图
   - 在“单日 d 值计算”区域，输入具体的年、月、日，点击“计算该日 d 值”可查询单日结果

4. 结果文件会输出为 Excel 格式，文件名示例：

   ```text
   sun_distance_analysis_latitude_{lat}_longitude_{lon}_year_{year}.xlsx
   ```

5. 若不再需要进度条，可关闭进度提示窗口。

## 文件说明

- `两小儿辩日问题.py`：主程序，包含 GUI 界面、距离计算与绘图逻辑。
- `de421.bsp`：NASA JPL 提供的太阳系星历数据文件。

## 常见问题

- **报错找不到 `de421.bsp`**：请检查该文件是否与脚本同目录，或修改脚本中 `load('de421.bsp')` 为实际路径。
- **无日出或正午时间（极昼/极夜）**：脚本会自动将对应日期标记为“极昼”或“极夜”，并令距离差值 d=0。

## 许可证

本项目遵循 MIT 许可证，详情请参阅 LICENSE 文件。
