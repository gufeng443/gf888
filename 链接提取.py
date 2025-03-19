import os
import re


def extract_links_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    links = [line.strip() for line in content if re.search(r'https?://', line)]
    return links


def main():
    folder_path = r'C:\Users\Administrator\Desktop\料子'
    output_file = os.path.join(folder_path, '数据汇总.txt')

    with open(output_file, 'w', encoding='utf-8') as output:
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.txt'):
                file_path = os.path.join(folder_path, file_name)
                links = extract_links_from_file(file_path)

                # 写入文件名（不带后缀），后面添加 '-'
                output.write(file_name[:-4] + '-\n')

                # 写入提取到的链接
                for link in links:
                    output.write(link + '\n')

                # 添加一个空行以分隔不同文件的数据
                output.write('\n')


if __name__ == '__main__':
    main()
