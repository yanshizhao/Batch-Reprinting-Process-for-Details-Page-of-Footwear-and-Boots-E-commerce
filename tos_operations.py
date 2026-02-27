import tos
import os
from config import AK, SK, REGION, BUCKET_NAME

#TOS 对象存储操作
def init_tos_client():
    """初始化TOS客户端"""
    try:
        client = tos.TosClientV2(
            ak=AK,
            sk=SK,
            region=REGION
        )
        return client
    except Exception as e:
        print(f"❌ TOS客户端初始化失败：{str(e)}")
        return None

def delete_tos_image(remote_file_key):
    """删除TOS上的指定图片"""
    client = init_tos_client()
    if not client:
        return False

    if not remote_file_key:
        print(f"❌ 错误：删除的文件key不能为空")
        return False

    try:
        resp = client.delete_object(
            bucket=BUCKET_NAME,
            key=remote_file_key
        )
        print(f"✅ 删除成功！文件key：{remote_file_key}")
        print(f"✅ TOS返回状态码：{resp.status_code}（204=删除成功）")
        return True

    except tos.exceptions.TosClientError as e:
        print(f"❌ 客户端删除错误：{e.error_code} - {e.error_msg}")
        return False
    except tos.exceptions.TosServerError as e:
        print(f"❌ 服务端删除错误：{e.error_code} - {e.error_msg}")
        if e.error_code == "NoSuchKey":
            print("   解决：检查文件key是否正确，或文件已被删除")
        elif e.error_code == "AccessDenied":
            print("   解决：确保AK/SK有TOS删除权限（主账号默认有）")
        return False
    except Exception as e:
        print(f"❌ 未知删除错误：{str(e)}")
        return False

def upload_to_tos(local_path, remote_file_key):
    """上传本地图片到TOS，返回公网可访问URL"""
    try:
        client = init_tos_client()
        if not client:
            return False

        # 检查本地图片是否存在
        if not os.path.exists(local_path):
            print(f"❌ 错误：本地图片不存在 → {local_path}")
            return False

        # 上传图片
        resp = client.put_object_from_file(
            bucket=BUCKET_NAME,
            key=remote_file_key,
            file_path=local_path
        )

        # 生成可访问URL
        image_url = f"https://{BUCKET_NAME}.tos-{REGION}.volces.com/{remote_file_key}"
        print(f"✅ 上传成功！产品图可直接访问：{image_url}\n✅ TOS返回状态：{resp.status_code}（200=成功）")
        return image_url

    except tos.exceptions.TosClientError as e:
        print(f"❌ 客户端错误（AK/SK错/网络问题）：{e.error_code} - {e.error_msg}")
    except tos.exceptions.TosServerError as e:
        print(f"❌ 服务端错误（权限/桶不存在）：{e.error_code} - {e.error_msg}")
        if e.error_code == "AccessDenied":
            print("   解决：桶权限设为【公共读】，或换主账号AK/SK")
        elif e.error_code == "NoSuchBucket":
            print("  解决：检查桶名是否正确，或区域是否匹配")
    except Exception as e:
        print(f"❌ 未知上传错误：{str(e)}")
    return False

def batch_delete_tos_images(prefix="temp_product/"):
    """批量删除指定前缀的TOS图片"""
    client = init_tos_client()
    if not client:
        return False

    try:
        resp = client.list_objects(BUCKET_NAME, prefix=prefix)
        if not resp.contents:
            print(f"无匹配前缀{prefix}的文件")
            return False

        delete_count = 0
        for obj in resp.contents:
            file_key = obj.key
            if delete_tos_image(file_key):
                delete_count += 1
        print(f"✅ 批量删除完成！成功删除{delete_count}个文件")
        return True
    except Exception as e:
        print(f"❌ 批量删除错误：{str(e)}")
        return False