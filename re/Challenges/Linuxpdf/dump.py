python
import base64
import zlib
import os
import re

def base64_decode_and_inflate(encoded_data):
    try:
        compressed_data = base64.b64decode(encoded_data)

        # 尝试 zlib
        try:
            decompressed_data = zlib.decompress(compressed_data)
            return decompressed_data
        except zlib.error:
            pass

        # 尝试 gzip
        try:
            decompressed_data = zlib.decompress(compressed_data, 16 + zlib.MAX_WBITS)
            return decompressed_data
        except zlib.error:
            pass

        # 尝试 raw deflate
        try:
            decompressed_data = zlib.decompress(compressed_data, -zlib.MAX_WBITS)
            return decompressed_data
        except zlib.error as e:
            print(f"解压缩失败: {e}")
            return None

    except Exception as e:
        print(f"解码失败: {e}")
        return None


def main():
    pdf_path = r"path"  # 改成你的 PDF 路径
    output_dir = "extracted"                        # 提取到这个文件夹

    with open(pdf_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # 定位数据段（根据你原来的逻辑）
    start_index = content.find('"vm_64.cfg"')
    if start_index == -1:
        print("找不到 vm_64.cfg，请检查 PDF 或搜索关键字")
        return

    end_marker = "for \\(let filename i"
    end_index = content.find(end_marker, start_index)
    if end_index == -1:
        print("找不到结束标记")
        return

    data_section = content[start_index:end_index - 4]

    # 按 ", " 分割每条记录
    items = data_section.split(", ")

    success = 0
    failed = 0

    for item in items:
        if ": " not in item:
            continue

        try:
            path_part, data_part = item.split(": ", 1)
            file_path = path_part.replace('"', "").strip()
            b64_data = data_part.replace('"', "").strip()

            if not file_path or not b64_data:
                continue

            decoded = base64_decode_and_inflate(b64_data)
            if decoded is None:
                print(f"[失败] {file_path}")
                failed += 1
                continue

            # 完整输出路径
            full_path = os.path.join(output_dir, file_path)

            # 自动创建目录
            dir_name = os.path.dirname(full_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            with open(full_path, "wb") as out:
                out.write(decoded)

            print(f"[成功] {full_path}  ({len(decoded)} bytes)")
            success += 1

        except Exception as e:
            print(f"[异常] {item[:50]}... -> {e}")
            failed += 1

    print("\n========== 完成 ==========")
    print(f"成功: {success}")
    print(f"失败: {failed}")
    print(f"文件保存在: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    main()