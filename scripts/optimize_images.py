# -*- coding: utf-8 -*-
"""
自動整理 uploads/ 底下的圖片：
  1. 檔名修掉重複副檔名（work-01.jpg.jpg -> work-01.jpg）
  2. PNG / HEIC 之外的大圖一律轉成 JPG
  3. 長邊縮到 2000px、品質 84，網頁跑得動、A4 列印也夠清楚
  4. 轉檔後刪掉原始大檔（Git 有歷史，隨時救得回來）

本機可以直接跑：python scripts/optimize_images.py
GitHub Actions 每次上傳圖片後也會自動跑一次。
"""
import os, sys
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS = os.path.join(BASE, "uploads")
LONG_SIDE = 2000
QUALITY = 84
MAX_KEEP = 900 * 1024          # 小於這個大小又已經是 jpg 就不動它

changed = []


def target_name(path):
    """work-01.jpg.jpg -> work-01.jpg ；任何格式 -> .jpg"""
    d, f = os.path.split(path)
    stem = f
    for _ in range(3):
        base, ext = os.path.splitext(stem)
        if ext.lower() in (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"):
            stem = base
        else:
            break
    return os.path.join(d, stem + ".jpg")


def process(path):
    dst = target_name(path)
    size = os.path.getsize(path)
    try:
        im = Image.open(path)
    except Exception as e:
        print("  跳過（不是圖片）", path, e)
        return

    w, h = im.size
    needs_resize = max(w, h) > LONG_SIDE
    same_name = os.path.normcase(dst) == os.path.normcase(path)

    if same_name and not needs_resize and size <= MAX_KEEP and im.format == "JPEG":
        return                                    # 已經是合格的 jpg

    im = im.convert("RGB")
    if needs_resize:
        r = LONG_SIDE / max(w, h)
        im = im.resize((round(w * r), round(h * r)), Image.LANCZOS)

    im.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    if not same_name and os.path.exists(path):
        os.remove(path)

    rel = os.path.relpath(dst, BASE).replace("\\", "/")
    changed.append(rel)
    print(f"  {os.path.basename(path)} {w}x{h} {size/1048576:.1f}MB"
          f"  ->  {os.path.basename(dst)} {im.size[0]}x{im.size[1]} "
          f"{os.path.getsize(dst)/1048576:.2f}MB")


def main():
    if not os.path.isdir(UPLOADS):
        print("找不到 uploads/ 資料夾"); return
    print("整理圖片中…")
    for root, _dirs, files in os.walk(UPLOADS):
        for f in sorted(files):
            if f.startswith("."):
                continue
            process(os.path.join(root, f))
    print(f"完成，處理了 {len(changed)} 張" if changed else "完成，沒有需要處理的圖")


if __name__ == "__main__":
    main()
