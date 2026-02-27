import requests
import json
import re
from config import  QINIU_API_KEY



def extract_prompts_from_response(response_dict):
    """
    从DeepSeek API响应中提取prompts列表（兼容所有Prompt格式，含无换行的【Prompt X】）
    """
    # 通用文本清理：去首尾空白、合并连续空白/换行为单个空格
    def clean_prompt(text):
        text = text.strip()
        return re.sub(r'\s+', ' ', text)

    # 正则模式列表（按优先级排序，修正【Prompt X】的匹配规则）
    patterns = [
        r'\*\*【Prompt \d+ - [^】]+】\*\*\s*(.*?)(?=\n\n\*\*【Prompt|\Z)', 
        r'【Prompt \d+ - [^】]+】\s*(.*?)(?=\n\n【Prompt|\Z)',            
        r'【Prompt \d+】\s*(.*?)(?=\n\n【Prompt|\Z)',                   
        r'\*\*Prompt \d+\*\*\s*(.*?)(?=\n\n\*\*Prompt|\Z)'            
    ]

    try:
        # 提取API响应的核心内容
        content = response_dict['choices'][0]['message']['content']
        # 按优先级循环匹配，匹配到即处理并返回
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                prompts = [clean_prompt(match) for match in matches]
                print(f"成功提取{len(prompts)}条提示词")
                return prompts
        # 无匹配结果
        print("未找到prompts列表")
        return []
    except Exception as e:
        print(f"提取失败: {e}")
        return []



def call_deep_seek_qnaigc(design_details):
    """
    将豆包视觉模型输出内容，转换为nano banana pro的提示词
    返回:
        dict: 接口返回的JSON数据（成功时）；None（失败时）
    """

    prompt_template = """ 
你是一名产品摄影提示词优化专家，负责将用户输入的参考图描述转化为高质量、可直接出图的“Nano Banana Pro”风格英文提示词。

工作流程：
解析输入：用户输入。{设计详情}，中包含多个参考图描述，每个都有结构化信息（如【拍摄角度】、【鞋子摆放角度】等）。
提取与翻译要素：针对每个参考图，必须从用户描述中提取以下六大要素，并全部转化为专业英文摄影术语：
构图角度 (Shot & Angle)：必须同时提取【拍摄角度】和【摆放角度】。将它们整合成一个完整的英文描述。例如，将“近景微俯5°-10°”与“单鞋平放、鞋头与水平线呈0°-5°”结合为：Close-up from a slight high angle (5°-10°俯角), centered composition with the shoe placed flat (toe at 0°-5° to horizontal)。
焦点区域 (Focus Area)：根据描述，用英文说明要展示的细节或整体。例如：focusing on the toe contour。
背景描述 (Background)：包括颜色、纹理、留白比例。例如：solid light beige background with subtle grid texture (matt finish, 70% negative space)。
布光方案 (Lighting)：一般为柔光漫射，可根据阴影描述调整。例如：soft diffused lighting。
细节要素 (Details)：包括阴影效果、空间关系、构图类型等。例如：minimal shadow casting a faint shoe silhouette。
风格基调 (Style)：根据“电商适配”和“优化方向”，确定风格。例如：minimalist and high-end。
生成提示词：将提取并翻译的六大要素，按照以下固定结构生成一条完整的英文提示词，并加入强约束以确保Nano Banana Pro严格按照指令执行：
Strictly adhere to the following specifications: [构图角度]，[焦点区域]，[背景描述]，[布光方案]，[细节要素]，[风格基调]，professional product photography, high definition, sharp focus, studio lighting.
注意： [ ]是占位符，你需要用从用户输入中提取并翻译后的具体英文内容来替换它们，而不是输出方括号本身。强约束语句“Strictly adhere to the following specifications:”必须包含在每个提示词的开头，以强制Nano Banana Pro精确遵循所有细节。

输出格式：为每个参考图生成一个提示词，并严格按照顺序编号，输出格式如下：
【Prompt 1】 生成的完整英文提示词句子。
【Prompt 2】 生成的完整英文提示词句子。

示例：

用户输入："拍摄角度：近景微俯5°-10°；摆放角度：单只鞋（局部展示），鞋头平放朝正前，与水平线呈0°-5°；鞋跟朝后，与水平线呈0°-5° ,xxxx"
你的输出：
【Prompt 1】 Strictly adhere to the following specifications: Close-up from a slight high angle (5°-10° overhead angle), centered composition with the shoe placed flat (toe at 0°-5° to horizontal), focusing on the toe contour and its transition to the vamp, xxxx.
"""
    final_prompt = prompt_template.format(设计详情=design_details)
    #print( final_prompt)
    # 1. 构造请求基础参数
    qiniu_url = "https://api.qnaigc.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {QINIU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek/deepseek-v3.2-251201",
        "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text",  "text": final_prompt},
                        #{"type": "image_url", "image_url":{"url":image_urls}}
                    ]
                }
        ],
    }

    try:
        response = requests.request("POST", qiniu_url, headers=headers, json=payload)
        # 检查HTTP响应状态码
        response.raise_for_status()
        #print(response)
        #print(f"响应状态码: {response.status_code}")
        response_dict = response.json()
        #print("response_dict:", response_dict)
        
        # 步骤2：提取提示词集
        extract_prompts = extract_prompts_from_response(response_dict)
        #print("extract_prompts: ", extract_prompts)
        return extract_prompts
    except ValueError as e:
        # 捕获JSON解析失败的异常
        print(f"解析接口返回数据失败: {e}")
        return None


