# Wayne Wang — Interior Designer Portfolio

王東群個人作品集與簡歷網站。純靜態 HTML，沒有框架、沒有資料庫。

**線上網址：https://waynewang-design.github.io/**

---

## 我要加照片（不用裝任何軟體，手機也能做）

1. 打開 https://github.com/WayneWang-design/waynewang-design.github.io
2. 進 `uploads/` → 點對應案子的資料夾（下表）
3. 右上角 **Add file → Upload files**，把照片拖進去
4. 檔名照 `01.jpg`、`02.jpg`⋯ 排（最多 8 張），最下面按 **Commit changes**

上傳後 GitHub 會自動幫你壓縮圖片、重新產生網頁，**約兩分鐘後網站就更新了**。
原始 4K 大檔直接丟沒關係，系統會自動縮到適合網頁的大小。

| 資料夾 | 案子 |
| :-- | :-- |
| `uploads/guotai/` | 01 國泰層峰 |
| `uploads/shuangxiang-1920/` | 02 雙橡園 1920 |
| `uploads/huatan-villa/` | 03 花壇別墅 |
| `uploads/xiushui-house/` | 04 秀水透天 |
| `uploads/guangyan-clinic/` | 05 光妍醫美診所 |
| `uploads/guanxin-clinic/` | 06 觀昕預防醫學診所 |

首頁那六張封面圖是 `uploads/work-01.jpg` ～ `work-06.jpg`，換掉就換封面。
個人照是 `uploads/portrait.jpg`（首頁大圖）跟 `uploads/about.jpg`（關於我）。

## 我要改文字

所有專案文字都在 **`projects.json`** 一個檔案裡。在 GitHub 網頁上點開它 → 右上角鉛筆圖示 → 改完 Commit，網站一樣會自動更新。

- 空著的欄位（`location`／`size`／`style`／`materials`）不會顯示，填了才出現
- `captions` 是每張圖底下的說明（客廳、餐廳、主臥⋯），只寫要標的那幾張就好：

```json
"captions": { "01": "客廳", "03": "主臥室" }
```

　　key 對應圖片檔名（`01` = `01.jpg`）。沒寫的圖就不顯示文字，也不會留空位。
- `concept` 是設計概念段落，`highlights` 是條列重點，格式：`["第一段", "第二段"]`
- 首頁的個人簡介、履歷、聯絡方式在 `index.html` 裡

## 換電腦怎麼接手

```bash
git clone https://github.com/WayneWang-design/waynewang-design.github.io.git
cd waynewang-design.github.io
```

直接用瀏覽器打開 `index.html` 就能預覽。改完推回去：

```bash
git add . && git commit -m "更新內容" && git push
```

需要在本機重建內頁的話（選用，因為 GitHub 會自動做）：

```bash
pip install pillow
python scripts/optimize_images.py && python build.py
```

---

## 檔案結構

```
index.html              首頁（作品／關於／履歷／聯絡）
works/*.html            六個專案內頁 ← 由 build.py 自動產生，不要手改
projects.json           專案資料，改這個就好
build.py                產生內頁的腳本
assets/site.css         全站樣式（首頁和內頁共用）
scripts/                圖片自動壓縮
uploads/                所有照片
.github/workflows/      自動化：上傳圖片後自動壓縮＋重建
```

網頁在螢幕上是暗色版，按右下角「列印 / 存成 PDF」會自動轉成米白配色的 A4 三頁版本，可直接寄給業主或當面試履歷。
