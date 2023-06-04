# 本站青苓君许可声明
# 
# 版权所有 (c) 2023 本站青苓君
# 

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtGui import QPalette
import qtmax
from pymxs import runtime as rt
#import pymxs
import requests
import base64
import os
import clipboard


class Module1Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Module1Widget, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout()

        self.url_line_edit = QtWidgets.QLineEdit()
        self.url_line_edit.editingFinished.connect(self.check_url_line_edit)
        layout.addWidget(self.url_line_edit)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setMinimumHeight(250)  # Set a default height for the image_label
        layout.addWidget(self.image_label)

        # Create the "输入提示词" group
        prompt_group = QtWidgets.QGroupBox("输入提示词")
        prompt_layout = QtWidgets.QVBoxLayout()

        self.prompt_line_edit = QtWidgets.QLineEdit()
        prompt_layout.addWidget(self.prompt_line_edit)

        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)

        self.cnt_group = QtWidgets.QGroupBox("controlNet")
        # self.cnt_group.setCheckable(True)
        # self.cnt_group.setChecked(False)
        # self.cnt_group.toggled.connect(self.toggle_group)
        cnt_layout = QtWidgets.QVBoxLayout()

        self.get_channel_btn = QtWidgets.QPushButton("一键获取通道图")
        self.get_channel_btn.clicked.connect(self.get_channel_images)
        cnt_layout.addWidget(self.get_channel_btn)

        self.file_list_widget = QtWidgets.QListWidget()
        #self.file_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        cnt_layout.addWidget(self.file_list_widget)

        self.cnt_group.setLayout(cnt_layout)
        layout.addWidget(self.cnt_group)

        # Create the "渲染" group
        render_group = QtWidgets.QGroupBox("渲染")
        render_layout = QtWidgets.QVBoxLayout()

        self.settings_btn = QtWidgets.QPushButton("设置")
        self.settings_btn.clicked.connect(self.show_settings_menu)
        render_layout.addWidget(self.settings_btn)

        self.render_btn = QtWidgets.QPushButton("渲染图片")
        self.render_btn.clicked.connect(self.render_image)
        render_layout.addWidget(self.render_btn)

        render_group.setLayout(render_layout)
        layout.addWidget(render_group)

        self.setLayout(layout)
        self.check_url_line_edit()  # Check initial state of input fields
        self.width = 512  # Default width
        self.height = 512  # Default height
        self.sampler_name = "Euler"  # Default sampler name
        self.steps = 50  # Default steps value
        self.cfg_scale = 7  # Default cfg_scale value
        self.restore_faces = False  # Default restore_faces value
        self.tiling = False  # Default tiling value
        self.negative_prompt = "(nsfw,deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4, dead Black,text,obscure)"  # Default negative_prompt value
        self.hosturl = self.url_line_edit
        self.controlnet = []

    def check_url_line_edit(self):
        if self.url_line_edit.text().strip() == "":
            self.url_line_edit.setText("http://127.0.0.1:7860")

    def show_settings_menu(self):
        dialog = SettingsDialog(self.width, self.height, self.sampler_name, self.steps, self.cfg_scale, self.restore_faces, self.tiling, self.negative_prompt,self.hosturl,self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.width = dialog.width
            self.height = dialog.height
            self.sampler_name = dialog.sampler_name
            self.steps = dialog.steps
            self.cfg_scale = dialog.cfg_scale
            self.restore_faces = dialog.restore_faces
            self.tiling = dialog.tiling
            self.negative_prompt = dialog.negative_prompt

    def render_image(self):
        control_net = self.get_item_payloads() #debug使用
        url = self.url_line_edit.text()
        prompt = self.prompt_line_edit.text()

        self.thread = RequestThread(url, prompt, self.width, self.height, self.sampler_name, self.steps, self.cfg_scale, self.restore_faces, self.tiling,self.negative_prompt,control_net)
        self.thread.requestFinished.connect(self.handle_request_finished)
        self.thread.start()  
        
    def handle_request_finished(self, image_data):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image_data)

        # Add the following code to resize the image if it's too large
        width, height = pixmap.width(), pixmap.height()
        if width > 250 or height > 250:
            scale_factor = min(250 / width, 250 / height)
            pixmap = pixmap.scaled(int(width * scale_factor), int(height * scale_factor))

        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)  # Center align the image

    def save_image(self):
        pixmap = self.image_label.pixmap()
        if pixmap:
            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "保存图片", "", "PNG Files (*.png)")
            if save_path:
                pixmap.save(save_path, "PNG")      

    def check_clipboard(self, checked):
        if checked:
            clipboard_content = clipboard.paste()
            if clipboard_content:
                byte_array = QtCore.QByteArray(clipboard_content.encode())
                image = QtGui.QImage.fromData(byte_array)
                if not image.isNull() and image.format() != QtGui.QImage.Format_Invalid:
                    pixmap = QtGui.QPixmap.fromImage(image)

                    file_path = qtpycompat.compat.getSaveFileName(
                        self,
                        "保存图片",
                        "",
                        "PNG Files (*.png)",
                        options=QtWidgets.QFileDialog.Options()
                    )
                    save_path = file_path[0] if isinstance(file_path, tuple) else file_path

                    if save_path:
                        pixmap.save(save_path, "PNG")
                else:
                    print("Clipboard content is not an image.")
   
    def toggle_group(self, checked):
        if checked:
            self.cnt_group.setTitle("controlNet (已启用)")
        else:
            self.cnt_group.setTitle("controlNet (已禁用)")
        
    def get_channel_images(self):

        file_path = rt.maxFilePath
        if not file_path:
            QtWidgets.QMessageBox.warning(self, "警告", "请先保存场景以获取工程文件路径")
            return

        output_folder = rt.pathConfig.appendPath(file_path, "outputjpg")

        if not os.path.exists(output_folder):
            choice = QtWidgets.QMessageBox.question(self, "提示", "你可能没有保存渲染图：{0}，是否执行保存操作？".format(output_folder),
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                os.makedirs(output_folder, exist_ok=True)
                save_file = os.path.join(output_folder, "output.jpg")
                rt.execute("vfbControl #saveallimage \"{0}\"".format(save_file))
                self.update_file_list(output_folder)  # Update the file list
            else:
                self.file_list_widget.clear()  # Clear the file list
                return

        files = ["output.VRayNormals.jpg", "output.VRayToon.jpg", "output.VRayWireColor.jpg", "output.VRayZDepth.jpg"]
        existing_files = [file for file in files if os.path.exists(os.path.join(output_folder, file))]

        if not existing_files:
            choice = QtWidgets.QMessageBox.question(self, "提示", "未识别到通道图像文件，需要我为你保存新渲染的通道？",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                save_file = os.path.join(output_folder, "output.jpg")
                rt.execute("vfbControl #saveallimage \"{0}\"".format(save_file))
                self.update_file_list(output_folder)  # Update the file list
            else:
                self.file_list_widget.clear()  # Clear the file list
                return

        self.update_file_list(output_folder)  # Update the file list
    


    def update_file_list(self, folder):
        self.dropdowns = []  # 创建一个空数组来存储dropdown
        self.base64_files = {}  # 存储文件名和对应的base64值的映射关系
        self.file_list_widget.clear()

        # 获取文件夹中所有的图片文件
        image_files = [file for file in os.listdir(folder) if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]

        for file_name in image_files:
            checkbox = QtWidgets.QCheckBox()
            checkbox.setChecked(False)  # 设置默认状态

            label = QtWidgets.QLabel(file_name)  # 文本只读

            dropdown = QtWidgets.QComboBox()
            dropdown.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)  # 调整下拉尺寸

            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(label)
            layout.addStretch(1)  # 布局适配
            layout.addWidget(dropdown)
            layout.addWidget(checkbox)

            item_widget = QtWidgets.QWidget()
            item_widget.setLayout(layout)
            item_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

            item = QtWidgets.QListWidgetItem(self.file_list_widget)
            item.setSizeHint(item_widget.sizeHint())  # 设置尺寸
            self.file_list_widget.setItemWidget(item, item_widget)
            self.dropdowns.append(dropdown)

            file_path = os.path.join(folder, file_name)
            # 将文件转换为base64并存储在实例变量中
            with open(file_path, "rb") as f:
                file_data = f.read()
                base64_data = base64.b64encode(file_data).decode("utf-8")
                self.base64_files[file_name] = base64_data  # 使用文件名作为键存储base64值

        self.file_list_widget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.file_list_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.refresh_model_list()
        #self.show_base64_files() #debug


    def show_base64_files(self):
            # 创建一个消息框来显示base64_files的结果
            message = "Base64 Files:\n\n"
            for mapped_name, base64_data in self.base64_files.items():
                message += f"{mapped_name}: {base64_data}\n\n"

            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Base64 Files")
            msg_box.setText(message)
            msg_box.exec_()

    def show_dropdown_mapping_dialog(self, dropdown_mapping):
        message_box = QtWidgets.QMessageBox()
        message_box.setWindowTitle("Dropdown Mapping")
        message_box.setText("Dropdown Mapping:")
        message_box.setInformativeText(str(dropdown_mapping))
        message_box.exec_()

    def get_image_data(self, mapped_name):
            # 根据条目名获取对应的图片数据
            if mapped_name in self.base64_files:
                base64_data = self.base64_files[mapped_name]
                base64header ="data:image/png;base64,"
                # 进一步处理或返回base64_data
                return base64header+base64_data
            else:
                # 条目名不存在时的处理
                return None


    def get_model_from_mapping(self, model_name):
        # 根据模型名称从映射关系中获取对应的模型
        if model_name in self.dropdown_mapping:
            return self.dropdown_mapping[model_name]
        else:
            return None

    def updata_dropdown_list(self, model_list):
        dropdown_mapping = {}  # 存储模型名称和下拉列表项的映射关系
        for model in model_list:
            model_name = model.split("_")[-1]  # 获取模型名称的最后一个 "_" 后面的内容
            dropdown_mapping[model_name] = model  # 建立模型名称和下拉列表项的映射关系       
            for dropitem in self.dropdowns:
                dropitem.addItem(model_name)
        # 存储映射关系为实例变量，以便在其他方法中使用
        self.dropdown_mapping = dropdown_mapping
         # 调用弹窗函数显示dropdown_mapping的内容
        #self.show_dropdown_mapping_dialog(dropdown_mapping)
        
   
    def get_item_payloads(self):
        item_payloads = []
        for i in range(self.file_list_widget.count()):
            item_widget = self.file_list_widget.itemWidget(self.file_list_widget.item(i))

            checkbox = item_widget.findChild(QtWidgets.QCheckBox)
            if checkbox and checkbox.isChecked():
                label = item_widget.findChild(QtWidgets.QLabel)
                dropdown = item_widget.findChild(QtWidgets.QComboBox)

                label_out = self.get_image_data(label.text())
                model_name_out = self.get_model_from_mapping(dropdown.currentText())
                if label and dropdown:
                    item_payload = {
                        "input_image": label_out,
                        "module": "none",
                        "model": model_name_out,
                        "pixel_perfect": True
                    }
                    item_payloads.append(item_payload)#满足要求的加入。   
        print(item_payloads)
        return item_payloads

    def get_item_payloads_debug(self):
        item_payloads = []
        for i in range(self.file_list_widget.count()):
            item_widget = self.file_list_widget.itemWidget(self.file_list_widget.item(i))

            checkbox = item_widget.findChild(QtWidgets.QCheckBox)
            if checkbox and checkbox.isChecked():
                label = item_widget.findChild(QtWidgets.QLabel)
                dropdown = item_widget.findChild(QtWidgets.QComboBox)

                label_out = self.get_image_data(label.text())
                model_name_out = self.get_model_from_mapping(dropdown.currentText())
                if label and dropdown:
                    item_payload = {
                        "input_image": label_out,
                        "module": "none",
                        "model": model_name_out
                    }
                    item_payloads.append(item_payload)

        if not item_payloads:
            label = QtWidgets.QLabel("No items selected.")
            item_payloads.append(label.text())

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Item Payloads")

        layout = QtWidgets.QVBoxLayout()
        dialog.setLayout(layout)

        label = QtWidgets.QLabel("\n".join(str(payload) for payload in item_payloads))
        layout.addWidget(label)

        dialog.exec_()



    def handle_model_list_error(self, error_message):
        reply = QtWidgets.QMessageBox.question(
            self, "Error", f"Failed to fetch model list:\n{error_message}", QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Cancel
        )
        if reply == QtWidgets.QMessageBox.Retry:
            self.refresh_model_list()

    def refresh_model_list(self):
        url = self.url_line_edit.text()
        model_list_thread = CNT_ModelList_RequestThread(url, parent=self)
        model_list_thread.modelListFetched.connect(self.updata_dropdown_list)#连接成功调用更新组件。
        model_list_thread.errorOccurred.connect(self.handle_model_list_error)#连接失败调用弹框提示用户是否重连。
        model_list_thread.start()

class Module2Widget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ddl1 =None
        self.hasVrayWireColor = False
        self.ddlItems = ["120,120,120|墙","180,120,120|建筑；大厦","6,230,230|天空","80,50,50|地板；地面","4,200,3|树","120,120,80|天花板","140,140,140|道路；路线","204,5,255|床","230,230,230|窗玻璃；窗户","4,250,7|草","224,5,255|橱柜","235,255,7|人行道","150,5,61|人；个体；某人；凡人；灵魂","120,120,70|地球；土地","8,255,51|门；双开门","255,6,82|桌子","143,255,140|山；峰","204,255,4|植物；植被；植物界","255,51,7|窗帘；帘子；帷幕","204,70,3|椅子","0,102,200|汽车；机器；轿车","61,230,250|水","255,6,51|绘画；图片","11,102,255|沙发；长沙发；躺椅","255,7,71|书架","255,9,224|房子","9,7,230|海","220,220,220|镜子","255,9,92|地毯","112,9,255|田野","8,255,214|扶手椅","7,255,224|座位","255,184,6|栅栏；围栏","10,255,71|书桌","255,41,10|岩石；石头","7,255,255|衣柜；壁橱；储藏柜","224,255,8|台灯","102,8,255|浴缸；沐浴缸；浴盆","255,61,6|栏杆；扶手","255,194,7|靠垫","255,122,8|基座；底座；支架","0,255,20|盒子","255,8,41|柱子；支柱","255,5,153|招牌；标志","6,51,255|抽屉柜；抽屉；梳妆台；梳妆柜","235,12,255|柜台","160,150,20|沙滩；沙子","0,163,255|水槽","140,140,140|摩天大楼","250,10,15|壁炉；炉床；明火炉","20,255,0|冰箱；冰柜","31,255,0|看台；有盖看台","255,31,0|小路","255,224,0|楼梯；台阶","153,255,0|跑道","0,0,255|展示柜；橱窗；展示架","255,71,0|台球桌；斯诺克桌","0,235,255|枕头","0,173,255|纱门；纱窗","31,0,255|楼梯；楼梯","11,200,200|河流","255,82,0|桥","0,255,245|书架","0,61,255|百叶窗；屏风","0,255,112|咖啡桌；鸡尾酒桌","0,255,133|厕所；茅房；坑位；便池；小便池；马桶","255,0,0|花","255,163,0|书","255,102,0|山丘","194,255,0|长凳","0,143,255|台面","51,255,0|炉灶；厨房炉灶；烹饪炉灶","0,82,255|棕榈树","0,255,41|厨房中间的工作台","0,255,173|计算机；计算设备；数据处理器；电子计算机；信息处理系统","10,0,255|转椅","173,255,0|船","0,255,153|闩","255,92,0|街机","255,0,255|简陋的小屋；小屋；小笼棚；简陋的棚屋","255,0,245|公共汽车；汽车客车；长途大巴；旅游大巴；双层巴士；公共小巴；摩托巴士；豪华大巴；公共汽车；载客车辆","255,0,102|毛巾","255,173,0|灯；光源","255,0,20|卡车；货车","255,184,184|塔","0,31,255|枝形吊灯；吊灯","0,255,61|遮阳篷；阳光遮盖物；遮阳百叶窗","0,71,255|路灯；街灯","255,0,204|展台；小隔间；小亭子；货摊","0,255,194|电视接收器；电视；电视机","0,255,82|飞机；航空器；飞行器","0,10,255|泥地赛道","0,112,255|服装；穿着的服装；服饰","51,0,255|柱子","0,194,255|土地；地面；土壤","0,122,255|楼梯扶手；栏杆；栏杆；扶手","0,255,163|自动扶梯","255,153,0|脚凳；小凳子；蒲团；抱枕","0,255,10|瓶子","255,112,0|自助餐柜台；柜台；餐具柜","143,255,0|海报；张贴；广告牌；通知；账单；卡片","82,0,255|舞台","163,255,0|货车；面包车","255,235,0|船；轮船","8,184,170|喷泉","133,0,255|传送带；输送带；输送机","0,255,92|天篷；顶棚","184,0,255|洗衣机；自动洗衣机","255,0,31|玩具","0,184,255|游泳池；游泳浴池；游泳馆","0,214,255|凳子","255,0,112|桶；木桶","92,255,0|篮子；提篮","0,224,255|瀑布","112,224,255|帐篷；可折叠的住所","70,184,160|袋子","163,0,255|迷你摩托车；摩托车","153,0,255|摇篮","71,255,0|烤箱","255,0,163|球","255,204,0|食物；实体食品","255,0,143|阶梯；楼梯","0,255,235|水箱；储水池","133,255,0|商标；品牌名称；品牌","255,0,235|微波炉；微波炉炉","245,0,255|锅；花盆","255,0,122|动物；有生命的生物；野兽；畜生；生物","255,245,0|自行车","10,190,212|湖","214,255,0|洗碗机；洗碗机","0,204,255|屏幕；银幕；投影屏幕","20,0,255|毛毯；盖子","255,255,0|雕塑","0,153,255|抽油烟机；排气罩","0,41,255|壁灯","0,255,204|花瓶","41,0,255|交通信号灯；交通信号；红绿灯","41,255,0|托盘","173,0,255|垃圾桶；烟灰缸","0,245,255|风扇","71,0,255|码头；栈桥；船坞","122,0,255|CRT屏幕","0,255,184|盘子","0,92,255|监视器；监测设备","184,255,0|公告栏；布告板","0,133,255|淋浴","255,214,0|散热器","251,94,194|玻璃杯","102,255,0|时钟","92,0,255|旗帜"]
        self.defaultItems = self.ddlItems.copy()
        self.initUI()

    def initUI(self):
        vbox = QtWidgets.QVBoxLayout()

        # Group Box 1
        grp1 = QtWidgets.QGroupBox("1、搜索后下拉即可看到所有匹配选项", self)
        vbox.addWidget(grp1)

        grp1_layout = QtWidgets.QVBoxLayout(grp1)

        ddl1 = QtWidgets.QComboBox(grp1)
        ddl1.setEditable(True)
        ddl1.lineEdit().textEdited.connect(self.on_ddl1_text_edited)
        ddl1.currentIndexChanged.connect(self.on_ddl1_selected)
        self.update_ddl_items(ddl1, self.ddlItems)
        grp1_layout.addWidget(ddl1)

        # Color Component QLabel
        color_label =QtWidgets.QLabel(self)
        color_label.setFixedSize(260, 30)
        color_label.setAutoFillBackground(True)
        grp1_layout.addWidget(color_label)

        searchLabel = QtWidgets.QLabel("输入关键词：", grp1)
        grp1_layout.addWidget(searchLabel)

        searchTextBox = QtWidgets.QLineEdit(grp1)
        searchTextBox.textChanged.connect(self.on_search_text_changed)
        grp1_layout.addWidget(searchTextBox)


        # Group Box 2
        grp2 = QtWidgets.QGroupBox("2、可将显示颜色设置成对象颜色预览", self)
        vbox.addWidget(grp2)

        grp2_layout = QtWidgets.QVBoxLayout(grp2)

        btn_stmat = QtWidgets.QPushButton("颜色附加到选中物体", grp2)
        btn_stmat.clicked.connect(self.on_btn_stmat_pressed)
        grp2_layout.addWidget(btn_stmat)

        vbox.addStretch(1)
        self.setLayout(vbox)
        self.setWindowTitle("Module2Widget")

        self.ddl1 = ddl1
        self.color_label = color_label

        # Set the initial color based on the first item
        self.update_color_label(self.ddlItems[0])

    def update_ddl_items(self, ddl, items):
        ddl.clear()
        ddl.addItems(items)

    def filter_ddl_items(self, ddl, keyword):
        filtered_items = [item for item in self.ddlItems if keyword.lower() in item.lower()]
        self.update_ddl_items(ddl, filtered_items)

    def update_color_label(self, selected_item):
        color_values = selected_item.split("|")[0].split(",")
        if len(color_values) == 3:
            try:
                red, green, blue = int(color_values[0]), int(color_values[1]), int(color_values[2])
                self.color_label.setStyleSheet(f"background-color: rgb({red}, {green}, {blue});")
            except ValueError:
                # Handle invalid color values
                self.color_label.setStyleSheet("background-color: rgb(0, 0, 0);")
        else:
            # Handle unexpected format
            self.color_label.setStyleSheet("background-color: rgb(0, 0, 0);")

    def on_ddl1_text_edited(self, text):
        self.filter_ddl_items(self.ddl1, text)

    def on_ddl1_selected(self, index):
        if self.ddl1!=None:
            selected_item = self.ddl1.currentText()
            self.update_color_label(selected_item)

    def on_search_text_changed(self, text):
        self.filter_ddl_items(self.ddl1, text)

    def on_btn_stmat_pressed(self):
        sel_obj = rt.selection
        if sel_obj.count > 0:
            color = self.color_label.palette().color(QPalette.Window)
            for obj in sel_obj:
                obj.wirecolor = rt.Color(color.red(), color.green(), color.blue())
                
class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, width, height, sampler_name, steps, cfg_scale, restore_faces, tiling, negative_prompt, hosturl,parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.url = hosturl.text()

        layout = QtWidgets.QVBoxLayout()

        self.width_spin_box = QtWidgets.QSpinBox()
        self.width_spin_box.setMaximum(2048)  # Set maximum width value
        self.width_spin_box.setValue(width)
        self.width_spin_box.valueChanged.connect(self.update_width)
        layout.addWidget(QtWidgets.QLabel("宽度"))
        layout.addWidget(self.width_spin_box)

        self.height_spin_box = QtWidgets.QSpinBox()
        self.height_spin_box.setMaximum(2048)  # Set maximum height value
        self.height_spin_box.setValue(height)
        self.height_spin_box.valueChanged.connect(self.update_height)
        layout.addWidget(QtWidgets.QLabel("高度"))
        layout.addWidget(self.height_spin_box)

        self.get_size_button = QtWidgets.QPushButton("一键获取渲染尺寸")
        self.get_size_button.clicked.connect(self.get_render_size)
        layout.addWidget(self.get_size_button)

        self.sampler_combo_box = QtWidgets.QComboBox()
        layout.addWidget(QtWidgets.QLabel("采样器"))
        layout.addWidget(self.sampler_combo_box)
        
        # 获取按钮
        self.get_sampler_button = QtWidgets.QPushButton("获取采样器")
        self.sampler_combo_box.addItem(sampler_name)
        self.get_sampler_button.clicked.connect(self.refresh_samplers_List)
        layout.addWidget(self.get_sampler_button)

        self.steps_spin_box = QtWidgets.QSpinBox()
        self.steps_spin_box.setMaximum(150)  # Set maximum steps value
        self.steps_spin_box.setValue(steps)
        layout.addWidget(QtWidgets.QLabel("步数"))
        layout.addWidget(self.steps_spin_box)

        self.cfg_scale_spin_box = QtWidgets.QSpinBox()
        self.cfg_scale_spin_box.setMaximum(30)  # Set maximum cfg_scale value
        self.cfg_scale_spin_box.setValue(cfg_scale)
        layout.addWidget(QtWidgets.QLabel("cfg_scale"))
        layout.addWidget(self.cfg_scale_spin_box)

        self.negative_prompt_line_edit = QtWidgets.QLineEdit()
        self.negative_prompt_line_edit.setText(negative_prompt)
        layout.addWidget(QtWidgets.QLabel("负面提示"))
        layout.addWidget(self.negative_prompt_line_edit)

        tiling_restore_layout = QtWidgets.QHBoxLayout()

        self.tiling_check_box = QtWidgets.QCheckBox("开启平铺")
        self.tiling_check_box.setChecked(tiling)
        tiling_restore_layout.addWidget(self.tiling_check_box)

        self.restore_faces_check_box = QtWidgets.QCheckBox("面部修复")
        self.restore_faces_check_box.setChecked(restore_faces)
        tiling_restore_layout.addWidget(self.restore_faces_check_box)

        layout.addLayout(tiling_restore_layout)

        button_layout = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        cancel_btn = QtWidgets.QPushButton("取消")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.setWindowTitle("设置")
        self.setFixedSize(250, 300)  # Adjusted height to accommodate the new button

        self.width = width
        self.height = height
        self.sampler_name = sampler_name
        self.steps = steps
        self.cfg_scale = cfg_scale
        self.restore_faces = restore_faces
        self.tiling = tiling
        self.negative_prompt = negative_prompt
        # self.refresh_samplers_List()

    def save_settings(self):
        self.width = self.width_spin_box.value()
        self.height = self.height_spin_box.value()
        self.sampler_name = self.sampler_combo_box.currentText()
        self.steps = self.steps_spin_box.value()
        self.cfg_scale = self.cfg_scale_spin_box.value()
        self.restore_faces = self.restore_faces_check_box.isChecked()
        self.tiling = self.tiling_check_box.isChecked()
        self.negative_prompt = self.negative_prompt_line_edit.text()
        self.accept()

    def update_width(self, value):
        self.width = value

    def update_height(self, value):
        self.height = value

    def keyPressEvent(self, event):
            if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                if self.width_spin_box.hasFocus() or self.height_spin_box.hasFocus():
                    event.ignore()
                    return
            super(SettingsDialog, self).keyPressEvent(event)
            
    def get_render_size(self):
        render_width = rt.renderWidth
        render_height = rt.renderHeight

        if render_width < 1024:
            target_width = render_width
            target_height = render_height
        else:
            target_width = 1024
            target_height = int(render_height * (target_width / render_width))
            
        self.width_spin_box.setValue(target_width)
        self.height_spin_box.setValue(target_height)   
        
    def handle_samplers_List_error(self, error_message):
        reply = QtWidgets.QMessageBox.question(
            self, "Error", f"Failed to fetch model list:\n{error_message}", QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Cancel
        )
        if reply == QtWidgets.QMessageBox.Retry:
            self.refresh_samplers_List()

    def refresh_samplers_List(self):
        model_list_thread = Samplers_List_RequestThread(self.url, parent=self)
        model_list_thread.samplersListFetched.connect(self.updata_samplers_List)#连接成功调用更新组件。
        model_list_thread.errorOccurred.connect(self.handle_samplers_List_error)#连接失败调用弹框提示用户是否重连。
        model_list_thread.start()  

    def updata_samplers_List(self,samplers_List):
        self.sampler_combo_box.clear() #清空列表防止出错
        for sampler in samplers_List:
            self.sampler_combo_box.addItem(sampler)
            
#以下是api
class CNT_ModelList_RequestThread(QtCore.QThread):
    modelListFetched = QtCore.Signal(list)
    errorOccurred = QtCore.Signal(str)

    def __init__(self, url, parent=None):
        super(CNT_ModelList_RequestThread, self).__init__(parent)
        self.url = url

    def fetch_model_list(self):
        try:
            response = requests.get(self.url + "/controlnet/model_list")
            response.raise_for_status()
            json_response = response.json()
            model_list = json_response.get("model_list", [])
            self.modelListFetched.emit(model_list)
        except requests.exceptions.RequestException as e:
            self.errorOccurred.emit(str(e))

    def run(self):
        try:
            self.fetch_model_list()
        except Exception as e:
            self.errorOccurred.emit(str(e))
            
class Samplers_List_RequestThread(QtCore.QThread):
    samplersListFetched = QtCore.Signal(list)
    errorOccurred = QtCore.Signal(str)

    def __init__(self, url, parent=None):
        super(Samplers_List_RequestThread, self).__init__(parent)
        self.url = url

    def fetch_samplers_List(self):
        try:
            response = requests.get(self.url + "/sdapi/v1/samplers")
            response.raise_for_status()
            json_response = response.json()
            samplers_List = [model.get("name") for model in json_response]
            self.samplersListFetched.emit(samplers_List)
        except requests.exceptions.RequestException as e:
            self.errorOccurred.emit(str(e))

    def run(self):
        try:
            self.fetch_samplers_List()
        except Exception as e:
            self.errorOccurred.emit(str(e))
            
class RequestThread(QtCore.QThread):
    requestFinished = QtCore.Signal(bytes)

    def __init__(self, url, prompt, width=512, height=512, sampler_name="Euler", steps=50, cfg_scale=7, restore_faces=False, tiling=False, negative_prompt="(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4, dead Black,text,obscure,nsfw)", control_net=[],parent=None):
        super(RequestThread, self).__init__(parent)
        self.url = url
        self.prompt = prompt
        self.width = width
        self.height = height
        self.sampler_name = sampler_name
        self.steps = steps
        self.cfg_scale = cfg_scale
        self.restore_faces = restore_faces
        self.tiling = tiling
        self.negative_prompt = negative_prompt
        self.control_net = control_net

    def run(self):
        payload = {
            "prompt": self.prompt,
            "sampler_name": self.sampler_name,
            "steps": self.steps,
            "cfg_scale": self.cfg_scale,
            "restore_faces": self.restore_faces,
            "tiling": self.tiling,
            "negative_prompt": self.negative_prompt,
            "width": self.width,
            "height": self.height,
            "save_images": True,
            "alwayson_scripts":{"controlnet":{"args":self.control_net}}
        }

        try:
            response = requests.post(self.url + "/sdapi/v1/txt2img", json=payload)
            response.raise_for_status()

            json_response = response.json()
            image_data_list = json_response.get("images", [])

            if image_data_list:
                image_data = base64.b64decode(image_data_list[0].replace("data:image/png;base64,", ""))
                self.requestFinished.emit(image_data)

        except requests.exceptions.RequestException as e:
            print("Error:", e)

class PyMaxDockWidget(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super(PyMaxDockWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle('SDforMAX@bilbili青苓君v0.0.1')
        self.initUI()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self):
        tab_widget = QtWidgets.QTabWidget()

        module1_widget = Module1Widget()
        module2_widget = Module2Widget()

        tab_widget.addTab(module1_widget, "渲染")
        tab_widget.addTab(module2_widget, "工具")

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(tab_widget)

        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        self.setWidget(widget)
        self.resize(300, 600)
        self.setFixedSize(self.size())


def main():
    main_window = qtmax.GetQMaxMainWindow()
    w = PyMaxDockWidget(parent=main_window)
    w.setFloating(True)
    w.show()


if __name__ == '__main__':
    main()
