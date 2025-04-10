
import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splrep, splev
from matplotlib import rcParams



#需要中文打开这里的注释
rcParams['font.family'] = 'SimHei'  # 黑体
rcParams['axes.unicode_minus'] = False  # 显示负号
rcParams['axes.titlesize'] = 10  # 设置标题字体大小

#需要日文打开这里的注释
# rcParams['font.family'] = 'MS Gothic'#日语字体
# rcParams['axes.unicode_minus'] = False  # 显示负号
# rcParams['axes.titlesize'] = 10  # 设置标题字体大小

# 不同曲线的点样式，支持最多十个点，十个点之后会循环使用
MARKERS = ['o', 's', '^', 'D', '*', 'x', 'v', 'p', 'h', '+']
COLORS = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'cyan', 'magenta']

class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("轻量绘图软件")# 设置窗口标题
        self.entries = {}# 用户输入的所有数据都放在这个字典中

        self.create_input_fields()
        self.create_data_input_area()
        self.create_plot_button()

    def create_input_fields(self):
        labels = [
            ("測定者名字", "pic_people1"),
            ("記録者名字", "pic_people2"),
            ("図表作成者", "pic_people3"),
            ("标题", "pic_name"),
            ("图编号", "pic_number"),
            ("横軸名称", "pic_x_name"),
            ("横軸単位", "pic_x_unit"),
            ("纵轴名称", "pic_y_name"),
            ("纵轴単位", "pic_y_unit"),
            ("横轴从哪开始", "pic_x_tick"),
            ("横轴到哪结束", "pic_x_tick_end"),
            ("横軸刻度", "pic_x_tick_step"),
            ("纵轴从哪开始", "pic_y_tick"),
            ("纵轴到哪结束", "pic_y_tick_end"),
            ("纵轴刻度", "pic_y_tick_step"),
        ]

        for i, (label_text, var_name) in enumerate(labels): # i获取索引，后面那个元祖获取每一项，将其全部进行放入操作
            label = tk.Label(self.root, text=label_text)# 把一个文字标签挂在self.root上面，文字内容为第一项
            label.grid(row=i, column=0, sticky="e")#第i行，第0列，e表示向右对齐
            entry = tk.Entry(self.root, width=30)# 创建一个输入框，宽度为30
            entry.grid(row=i, column=1)# 在第i行，第1列，默认向左对齐
            self.entries[var_name] = entry# 将输入框的引用存储在字典中，键为pic_people1等，值为输入框用户输入的内容

        self.grid_var = tk.IntVar()# 创建一个整型变量，用于存储网格显示的状态
        grid_checkbox = tk.Checkbutton(self.root, text="显示网格", variable=self.grid_var)# 创建一个复选框，文本为“显示网格”，属于grid_var变量
        grid_checkbox.grid(row=len(labels), column=1, sticky="w")# 在最后一行，列1，w表示向左对齐
        self.grid_var2 = tk.IntVar()
        grid_checkbox = tk.Checkbutton(self.root, text="正方向箭头", variable=self.grid_var2)
        grid_checkbox.grid(row=(len(labels))+1, column=1, sticky="w")
        self.grid_var3 = tk.IntVar()
        grid_checkbox = tk.Checkbutton(self.root, text="彩图", variable=self.grid_var3)
        grid_checkbox.grid(row=(len(labels))+2, column=1, sticky="w")




    def create_data_input_area(self):# 创建数据输入区域
        tk.Label(self.root, text="先输入曲线名，按回车，下面是数据点（x,y），结束按回车，按两下可以切换曲线").grid(row=0, column=2, padx=5, sticky="w")#  # 在第1行，第2列（绝对不能错，因为第一列是文字，第二列输入框），五个像素，靠左对齐
        self.data_text = tk.Text(self.root, height=30, width=50)# 创建一个文本框，大小为30行50列
        self.data_text.grid(row=1, column=2, rowspan=30, padx=5, pady=5)# 在第2行（要和get保持一致），第3列，跨30行，5个像素的边距





    def create_plot_button(self):# 创建绘图按钮
        plot_button = tk.Button(self.root, text="绘图", command=self.plot_graph)# 创建一个按钮，文本为“绘图”，点击后调用plot_graph回调函数，进入绘图模式
        plot_button.grid(row=30, column=1, pady=10)





    def parse_data(self):#错误解析，数据处理函数
        text = self.data_text.get("1.0", tk.END).strip()# 获取大文本框中的所有内容，去掉首尾空格
        lines = text.split("\n")# 将文本按行分割成列表，每一行为一个数据
        all_curves = []# 所有曲线数据的列表，里面是一个个元组，元组里是曲线名称，x坐标，y坐标
        current_name = None# 当前曲线名称
        current_x = []# 当前曲线的x坐标列表
        current_y = []# 当前曲线的y坐标列表

        for line in lines + [""]:  # 添加一个空行处理最后一组
            line = line.strip()# 去掉首尾空格
            if not line:# 如果是空行，表示当前曲线结束
                if current_name and current_x and current_y:# 如果当前曲线有数据
                    all_curves.append((current_name, current_x, current_y))# 将当前曲线数据添加到所有曲线列表中，填入三个数据，分别是曲线名称，x坐标，y坐标，xy坐标是列表
                    current_name = None#初始化
                    current_x = []
                    current_y = []
                continue
            if current_name is None:#第一次进入，当前曲线名称为空
                current_name = line# 如果当前曲线名称为空，表示当前行是曲线名称
            else:
                try:
                    x, y = map(float, line.split(","))#xy处理部分，先分割成x和y两个部分，map函数转换成浮点数
                    current_x.append(x)# 将x坐标添加到当前曲线的x坐标列表中
                    current_y.append(y)
                except:
                    raise ValueError(f"填入数字，例如 1,2，这个数据不合法：{line}")

        return all_curves
    




    def plot_graph(self):
        try:
            # 创建图形和坐标轴
            
            all_curves = self.parse_data()# 解析数据，获取所有曲线数据
            if not all_curves:#正常是真，如果为空，说明没有数据
                messagebox.showerror("错误", "请至少输入一条曲线数据。")
                return

            for key in self.entries:# 遍历所有输入框，检查是否为空
                if not self.entries[key].get():# 如果输入框为空，提示用户
                    messagebox.showerror("错误", f"请输入：{key}")
                    return

            
            
            if not self.grid_var2.get():#如果不需要箭头，进入正常绘图模式
                plt.figure()# 创建一个新的图形窗口，默认大小为6x4英寸
 
                if self.grid_var.get():# 如果复选框被选中，显示网格
                    plt.grid(True)

                for i, (label, x_vals, y_vals) in enumerate(all_curves):# 参数i是索引，label是曲线名称，x_vals是x坐标列表，y_vals是y坐标列表
                    if len(x_vals) < 4:
                        messagebox.showerror("错误", f"“{label}” 至少需要4个数据点。")
                        return

                    sorted_data = sorted(zip(x_vals, y_vals))# zip将x和y坐标打包成元组，按x坐标排序，sorted进行排序
                    x_vals, y_vals = zip(*sorted_data)# 解压缩，得到排序后的x和y坐标列表
                    spl = splrep(x_vals, y_vals, s=10)# 使用样条插值函数
                    x_new = np.linspace(min(x_vals), max(x_vals), 100)
                    y_new = splev(x_new, spl)

                    marker = MARKERS[i % len(MARKERS)]#  # 获取当前曲线的点样式，循环使用
                    if self.grid_var3.get():
                        col=COLORS[i % len(COLORS)]
                    else:
                        col='black'
                    plt.plot(x_new, y_new, color=col,linestyle='-')# 绘制曲线，颜色为黑色，线型为实线
                    plt.scatter(x_vals, y_vals, marker=marker, color=col,edgecolors='black', label=label)# 绘制原始数据点，颜色为黑色，边框颜色为黑色，标签为“曲线名称 原始点”

                    

                
                
                plt.suptitle(f"測定者：{self.entries['pic_people1'].get()} 記録者:{self.entries['pic_people2'].get()} 図表作成者:{self.entries['pic_people3'].get()}", fontsize=10)# 设置标题，字体大小为10
                plt.title("図：" + self.entries["pic_number"].get() + " " + self.entries["pic_name"].get(), fontsize=17)# 设置副标题，字体大小为17
                plt.xlabel(self.entries["pic_x_name"].get() + "  " + self.entries["pic_x_unit"].get(), fontsize=12)# 设置x轴标签，字体大小为12
                plt.ylabel(self.entries["pic_y_name"].get() + "  " + self.entries["pic_y_unit"].get(), fontsize=12)## 设置y轴标签，字体大小为12
                plt.legend()# 添加图例，显示曲线名称
                plt.xticks(np.arange(float(self.entries["pic_x_tick"].get()), float(self.entries["pic_x_tick_end"].get()) + 1, float(self.entries["pic_x_tick_step"].get())))## 设置x轴刻度，范围从pic_x_tick到pic_x_tick_end，步长为pic_x_tick_step
                plt.yticks(np.arange(float(self.entries["pic_y_tick"].get()), float(self.entries["pic_y_tick_end"].get()) + 1, float(self.entries["pic_y_tick_step"].get())))
                plt.show()
                
            else:#需要箭头，进入箭头绘图模式
                fig, ax = plt.subplots()# 返回一个图形和坐标轴对象
                    # 设置x和y轴范围
                                # 设置网格  
                if self.grid_var.get():
                    ax.grid(True)
                    # 绘制横向坐标轴（X轴）
                ax.plot([ float(self.entries["pic_x_tick"].get()),float(self.entries["pic_x_tick_end"].get())], [0, 0], color='black', linewidth=1)

    # 绘制纵向坐标轴（Y轴）
                ax.plot([0, 0], [float(self.entries["pic_y_tick"].get()), float(self.entries["pic_y_tick_end"].get())], color='black', linewidth=1)
                # 绘制横向坐标轴
                # ax.plot([ float(self.entries["pic_x_tick"].get()),0], [float(self.entries["pic_x_tick_end"].get()),0], color='black', linewidth=1)  # 纵向坐标轴

                # # 绘制纵向坐标轴
                # ax.plot([0, float(self.entries["pic_y_tick"].get())], [0,float(self.entries["pic_y_tick_end"].get())], color='black', linewidth=1)  # 横向坐标轴
                # 绘制正方向的箭头
                ax.annotate('', xy=(float(self.entries["pic_x_tick_end"].get()), 0), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color='black'))
                ax.annotate('', xy=(0, float(self.entries["pic_y_tick_end"].get())), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color='black'))
                # 绘制曲线
                for i, (label, x_vals, y_vals) in enumerate(all_curves):# 参数i是索引，label是曲线名称，x_vals是x坐标列表，y_vals是y坐标列表
                    if len(x_vals) < 4:
                        messagebox.showerror("错误", f"“{label}” 至少需要4个数据点。")
                        return

                    sorted_data = sorted(zip(x_vals, y_vals))# zip将x和y坐标打包成元组，按x坐标排序，sorted进行排序
                    x_vals, y_vals = zip(*sorted_data)# 解压缩，得到排序后的x和y坐标列表
                    spl = splrep(x_vals, y_vals, s=10)# 使用样条插值函数
                    x_new = np.linspace(min(x_vals), max(x_vals), 100)
                    y_new = splev(x_new, spl)

                    marker = MARKERS[i % len(MARKERS)]#  # 获取当前曲线的点样式，循环使用
                    if self.grid_var3.get():
                        col=COLORS[i % len(COLORS)]
                    else:
                        col='black'
                    ax.plot(x_new, y_new, color=col,linestyle='-')# 绘制曲线，颜色为黑色，线型为实线
                    ax.scatter(x_vals, y_vals, marker=marker, color=col,edgecolors='black', label=label)# 绘制原始数据点，颜色为黑色，边框颜色为黑色，标签为“曲线名称 原始点”
                # ax.plot(x_new, y_new, color='black',linestyle='-')# 绘制曲线，颜色为黑色，线型为实线
                # ax.scatter(x_vals, y_vals, marker=marker, color='black',edgecolors='black', label=label)# 绘制原始数据点，颜色为黑色，边框颜色为黑色，标签为“曲线名称 原始点”

                # 设置坐标轴标签
                ax.set_xlabel(self.entries["pic_x_name"].get() + "  " + self.entries["pic_x_unit"].get(), fontsize=12)
                ax.set_ylabel(self.entries["pic_y_name"].get() + "  " + self.entries["pic_y_unit"].get(), fontsize=12)
                ax.set_title("図：" + self.entries["pic_number"].get() + " " + self.entries["pic_name"].get(), fontsize=17)
                ax.set_title(f"測定者：{self.entries['pic_people1'].get()} 記録者:{self.entries['pic_people2'].get()} 図表作成者:{self.entries['pic_people3'].get()}", fontsize=10)# 设置标题，字体大小为10
                ax.legend()# 添加图例，显示曲线名称


                plt.show()
            

        except Exception as e:
            messagebox.showerror("错误", f"发生错误：{str(e)}")

# 启动GUI
if __name__ == "__main__":#保护操作，防止被别的文件打开
    root = tk.Tk()# 创建主窗口
    app = PlotApp(root)# 创建应用程序实例，操作全部在init函数中完成
    root.mainloop()# 启动主事件循环，这段代码会监视用户执行了什么操作，直到窗口关闭，如果发现操作






# plt.xticks=np.arange(float(self.entries["pic_x_tick"].get()),float(self.entries["pic_x_tick_end"].get()) + 1,float(self.entries["pic_x_tick_step"].get()))
            # plt.yticks= np.arange(float(self.entries["pic_y_tick"].get()),float(self.entries["pic_y_tick_end"].get()) + 1,float(self.entries["pic_y_tick_step"].get()))

                # # if self.grid_var2.get():
                # self.spines['top'].set_visible(False)
                # self.spines['right'].set_visible(False)
                # self.spines['left'].set_position('zero')
                # self.spines['bottom'].set_position('zero') 
                # # 自定义负方向的轴线（无箭头）
                # self.plot([-6, 0], [0, 0], color='black', linewidth=1)  # x轴负方向
                # self.plot([0, 0], [-1.5, 0], color='black', linewidth=1)  # y轴负方向

                # # 添加正方向的箭头（作为坐标轴）
                # self.annotate('', xy=(6, 0), xytext=(0, 0),
                # arrowprops=dict(arrowstyle="->", color='black'))
                # self.annotate('', xy=(0, 1.5), xytext=(0, 0),
                # arrowprops=dict(arrowstyle="->", color='black'))

                                #     # 绘制x轴和y轴的负向线条
                # ax.plot([0,0],  (float(self.entries["pic_x_tick"].get()), float(self.entries["pic_x_tick_end"].get())), color='black', linewidth=1)
                # ax.plot([0,0], (float(self.entries["pic_y_tick"].get()), float(self.entries["pic_y_tick_end"].get())), color='black', linewidth=1)
                # 设置坐标轴标签