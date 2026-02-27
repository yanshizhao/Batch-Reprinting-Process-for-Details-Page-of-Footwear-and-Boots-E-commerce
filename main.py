# =============== 标准库 ===============
import sys
import uuid
from pathlib import Path

# =============== 第三方库 ===============
import tos
from openai import OpenAI

# =============== 本地模块 ===============
from tos_operations import upload_to_tos, batch_delete_tos_images
from image_downloader import save_prompts_to_file
from prompt_generator_doubao_seed import analysis_product_detail_page
from prompt_generator_qnaigc_deepseekV3 import call_deep_seek_qnaigc

# =============== 配置 ===============
from config import SUPPORTED_EXTENSIONS, ARK_API_KEY


def get_app_dir():
    """获取应用程序所在目录（双击运行时 = exe 所在目录）"""
    return Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent

# =============== 主函数 ===============
def main():
    app_dir = get_app_dir()
    input_root = app_dir / "product_image" / "detail_page_template"
    input_root.mkdir(parents=True, exist_ok=True)

    print(f"应用目录: {app_dir} | 输入目录: {input_root}")

    if not input_root.exists():
        print(f"[ERROR] 输入目录不存在: {input_root}")
        return

    product_folders = [f for f in input_root.iterdir() if f.is_dir()]
    if not product_folders:
        print(f"[WARN] 输入目录为空！请在 {input_root} 下创建子文件夹并放入图片。")
        return
    print(f"[OK] 发现 {len(product_folders)} 个产品文件夹：{[f.name for f in product_folders]}")

    # 初始化客户端
    try:
        client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=ARK_API_KEY
        )
    except Exception as e:
        print(f"[ERROR] OpenAI 初始化失败：{e}")
        return

    # 清理 TOS 临时文件
    try:
        batch_delete_tos_images("temp_product/")
    except Exception as e:
        print(f"[WARN] TOS 清理跳过：{e}")

    processed_count = 0
    for prod_folder in product_folders:
        name = prod_folder.name
        print("=" * 70)
        print(f"[PROCESS] 处理：【{name}】")
        print("=" * 70)

        # 收集图片
        images = [f for f in prod_folder.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]
        if not images:
            print(f"[SKIP] 无支持图片")
            continue
        print(f"[FOUND] {len(images)} 张图片")

        # 上传 TOS
        urls = []
        for img in images:
            try:
                key = f"temp_product/{name}_{uuid.uuid4()}.png"
                url = upload_to_tos(img, key)
                if url:
                    urls.append(url)
                    print(f"  ✓ {img.name}")
            except Exception as e:
                print(f"  ✗ {img.name} 上传失败: {str(e)[:30]}")
        if not urls:
            print("[SKIP] 无有效 URL")
            continue
        if len(urls) > 6:
            urls = urls[:6]
            print("[INFO] 截取前6张图")

        # 豆包模型
        try:
            print("[start]  调用豆包视觉模型分析图片详情")
            prompt_text = analysis_product_detail_page(client, urls)
            print(f"[SUCCESS] 豆包输出长度: {len(prompt_text)} 段详情描述: {prompt_text}")
            #print("prompt_text:", prompt_text)
        except Exception as e:
            print(f"[ERROR] 豆包失败: {e}")
            continue

        # DeepSeek
        try:
            print("[start]  调用deep seek 将图片详情转换为哪nano banana pro 的提示词")
            nano_prompts = call_deep_seek_qnaigc(prompt_text)
            print(f"[SUCCESS] 生成 {len(nano_prompts)} 条提示词")
            save_prompts_to_file(prod_folder, name, nano_prompts)  # ✅ 保存到 prod_folder（图片同级）
        except Exception as e:
            print(f"[ERROR] DeepSeek 失败: {e}")
            continue

        processed_count += 1

    print(f"\n[FINAL] 完成！共处理 {processed_count} 个产品。")

# =============== 入口 ===============
if __name__ == "__main__":
    main()