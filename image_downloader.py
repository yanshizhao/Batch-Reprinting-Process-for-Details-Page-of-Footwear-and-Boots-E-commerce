
from datetime import datetime


def save_prompts_to_file(prod_folder, prod_folder_name, prompt_nano):
    """
    将提示词列表保存到原图文件夹中
    
    Args:
        prod_folder: 产品文件夹路径对象
        prod_folder_name: 产品文件夹名称
        prompt_nano: 提示词列表
    """
    try:
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_filename = f"{prod_folder_name}_prompts_{timestamp}.txt"
        prompt_file_path = prod_folder / prompt_filename  # 直接保存到原图文件夹
        
        # 保存提示词到文件
        with open(prompt_file_path, 'w', encoding='utf-8') as f:
            f.write(f"产品名称：{prod_folder_name}\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总屏数：{len(prompt_nano)}\n")
            f.write("="*60 + "\n\n")
            
            for i, prompt in enumerate(prompt_nano, 1):
                f.write(f"【Prompt {i}】\n")
                f.write(prompt + "\n")
                f.write("-"*50 + "\n\n")
        
        print(f"提示词已保存至：{prompt_file_path.absolute()}")
        return prompt_file_path
    except Exception as e:
        print(f"保存提示词文件失败：{str(e)}")
        return None