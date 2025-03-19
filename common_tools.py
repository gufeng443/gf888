import tkinter as tk
from tkinter import ttk, messagebox
from googletrans import Translator

class TranslationPage(tk.Frame):
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.create_page()

    def create_page(self):
        # 创建输入框标签
        if not hasattr(self, 'label_text'):
            self.label_text = tk.StringVar()
            self.label_text.set("请输入需要翻译的内容：")
            ttk.Label(self, textvariable=self.label_text).pack(pady=10)

            # 创建用户输入框
            self.text_input = tk.Text(self, height=13, width=90)
            self.text_input.pack(pady=10)

            # 创建语言选择框
            self.language_label = ttk.Label(self, text="选择翻译语言：")
            self.language_label.pack(pady=5)

            # 生成语言名称到语言代码的映射
            self.languages_dict = {
                '阿非利卡语': 'af',
                '阿尔巴尼亚语': 'sq',
                '阿姆哈拉语': 'am',
                '阿拉伯语': 'ar',
                '亚美尼亚语': 'hy',
                '阿塞拜疆语': 'az',
                '巴斯克语': 'eu',
                '白俄罗斯语': 'be',
                '孟加拉语': 'bn',
                '波斯尼亚语': 'bs',
                '保加利亚语': 'bg',
                '加泰罗尼亚语': 'ca',
                '宿务语': 'ceb',
                '奇切瓦语': 'ny',
                '中文（简体）': 'zh-cn',
                '中文（繁体）': 'zh-tw',
                '科西嘉语': 'co',
                '克罗地亚语': 'hr',
                '捷克语': 'cs',
                '丹麦语': 'da',
                '荷兰语': 'nl',
                '英语': 'en',
                '世界语': 'eo',
                '爱沙尼亚语': 'et',
                '菲律宾语': 'tl',
                '芬兰语': 'fi',
                '法语': 'fr',
                '弗里西语': 'fy',
                '加利西亚语': 'gl',
                '格鲁吉亚语': 'ka',
                '德语': 'de',
                '希腊语': 'el',
                '古吉拉特语': 'gu',
                '海地克里奥尔语': 'ht',
                '豪萨语': 'ha',
                '夏威夷语': 'haw',
                '希伯来语': 'he',
                '印地语': 'hi',
                '苗语': 'hmn',
                '匈牙利语': 'hu',
                '冰岛语': 'is',
                '伊博语': 'ig',
                '印尼语': 'id',
                '爱尔兰语': 'ga',
                '意大利语': 'it',
                '日语': 'ja',
                '爪哇语': 'jv',
                '卡纳达语': 'kn',
                '哈萨克语': 'kk',
                '高棉语': 'km',
                '韩语': 'ko',
                '库尔德语（库尔曼吉方言）': 'ku',
                '吉尔吉斯语': 'ky',
                '老挝语': 'lo',
                '拉丁语': 'la',
                '拉脱维亚语': 'lv',
                '立陶宛语': 'lt',
                '卢森堡语': 'lb',
                '马其顿语': 'mk',
                '马达加斯加语': 'mg',
                '马来语': 'ms',
                '马拉雅拉姆语': 'ml',
                '马耳他语': 'mt',
                '毛利语': 'mi',
                '马拉地语': 'mr',
                '蒙古语': 'mn',
                '缅甸语': 'my',
                '尼泊尔语': 'ne',
                '挪威语': 'no',
                '奈扬贾语': 'ny',
                '奥里亚语': 'or',
                '乌兹别克语': 'uz',
                '普什图语': 'ps',
                '波斯语': 'fa',
                '波兰语': 'pl',
                '葡萄牙语': 'pt',
                '旁遮普语': 'pa',
                '罗马尼亚语': 'ro',
                '俄语': 'ru',
                '萨摩亚语': 'sm',
                '苏格兰盖尔语': 'gd',
                '塞尔维亚语': 'sr',
                '塞索托语': 'st',
                '肯尼亚语': 'sn',
                '信德语': 'sd',
                '僧伽罗语': 'si',
                '斯洛伐克语': 'sk',
                '斯洛文尼亚语': 'sl',
                '索马里语': 'so',
                '西班牙语': 'es',
                '巽他语': 'su',
                '斯瓦希里语': 'sw',
                '瑞典语': 'sv',
                '塔吉克语': 'tg',
                '泰语': 'th',
                '土耳其语': 'tr',
                '乌克兰语': 'uk',
                '乌尔都语': 'ur',
                '越南语': 'vi',
                '威尔士语': 'cy',
                '科萨语': 'xh',
                '意第绪语': 'yi',
                '约鲁巴语': 'yo',
                '班图语': 'zu'
            }

            self.language_var = tk.StringVar(value='英语')  # 默认英语
            self.language_menu = ttk.Combobox(self, values=list(self.languages_dict.keys()))
            self.language_menu.set('英语')
            self.language_menu.pack(pady=5)

            # 创建翻译按钮
            self.translate_button = ttk.Button(self, text="翻译", command=self.translate_text)
            self.translate_button.pack(pady=10)

            # 创建结果显示框
            self.create_result_boxes()

        self.pack(fill=tk.BOTH, expand=True)

    def create_result_boxes(self):
        # 直译结果框
        if not hasattr(self, 'direct_translation_text'):
            ttk.Label(self, text="直译结果：").pack(pady=5)
            self.direct_translation_text = tk.Text(self, height=13, width=90, wrap=tk.WORD)
            self.direct_translation_text.pack(pady=5)
            self.direct_translation_text.config(state=tk.DISABLED)  # 初始不可编辑

    def translate_text(self):
        input_text = self.text_input.get("1.0", tk.END).strip()
        selected_language = self.language_menu.get()
        target_lang = self.languages_dict.get(selected_language, 'en')  # 默认英语

        if not input_text:
            messagebox.showwarning("警告", "输入内容不能为空！")
            return

        translator = Translator()
        try:
            # 直译
            translated = translator.translate(input_text, src='auto', dest=target_lang).text

            # 更新结果显示框
            self.direct_translation_text.config(state=tk.NORMAL)
            self.direct_translation_text.delete("1.0", tk.END)
            self.direct_translation_text.insert(tk.END, translated)
            self.direct_translation_text.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("错误", f"翻译失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("翻译工具")
    TranslationPage(root).pack(fill=tk.BOTH, expand=True)
    root.mainloop()
