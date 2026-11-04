---
name: add-cafe
description: 在「台中咖啡散步」網站新增一家（或一批）店家時使用：從收藏清單查資料、寫 raw 與 wiki、重新產生網頁並驗收，維持全站格式與風格一致。
---

# 新增店家 Skill

這個 skill 把「新增一家店」的做法固定下來，讓每次新增的頁面都和現有頁面一模一樣。專案規則以 `AGENTS.md` 為準，本檔是它的操作版。

## 輸入

- 店名（必要），最好附 Google 地圖連結或所屬收藏清單
- 一次可以處理多家；超過 20 家時先問使用者要分幾批

## 步驟

### 1. 確認來源
在 `raw/google-maps/*.csv` 找到這家店。找不到時，請使用者確認後，在對應 CSV 檔尾**新增一列**（不可改動既有列）。

### 2. 查詢資料
優先順序：Google 地圖店家頁 → 店家官方網站／IG／FB → 可信的美食媒體。
需要取得：地址、行政區、營業時間（每天）、類型、價位、評分與評論數、內用／外帶等服務、官網或社群、評論常提到的關鍵字。

### 3. 判斷是否收錄
- 不在臺中市 或 已停業／暫時關閉 → 在 `raw/research/_excluded.md` 表格加一列，**結束**。
- 否則繼續。

### 4. 決定 slug
小寫英文或拼音、用 `-` 連接；分店加地名（例：`tongqi-zhongming`）。先確認 `wiki/places/` 沒有同名檔案。

### 5. 寫 `raw/research/<slug>.md`
沿用現有檔案（例如 `raw/research/phase-coffee-zhongshan.md`）的表格格式，必填查詢日期與來源。

### 6. 寫 `wiki/places/<slug>.md`
- 複製 `wiki/places/phase-coffee-zhongshan.md` 的結構，逐欄替換。
- frontmatter 的 `area` 必須等於某個 `wiki/areas/*.md` 的 `name`。
- `tags`：從 AGENTS.md 第 7 節的標籤表挑 2–5 個，依條件判斷，例如營業到 23:00 後 → 深夜。
- `tagline`：15 字以內，點出這家店最大的特點。
- `maps`：`https://www.google.com/maps/search/?api=1&query=` + URL 編碼的「店名 地址」。
- 「特色」：100–200 字，朋友推薦的語氣；只寫 raw 裡有的事實；評論關鍵字寫成「評論常提到…」；營業時間不穩定時提醒先看 IG。
- 「推薦品項」：`評論中常被提到：…`，沒有資料就寫 `待確認`。
- 「我的筆記」：固定寫 `（尚未填寫。去過之後由我補上。）`。

### 7. 更新地區與目錄
- `wiki/areas/<area_slug>.md`：在「## 店家」清單加一行並更新數量；新行政區就新建檔案，必要時把區名加進 `tools/build.py` 的 `AREA_ORDER`。
- `wiki/index.md`：在「依地區」與「依標籤」兩段都加上這家店。

### 8. 產生網頁
```bash
python3 tools/build.py
```

### 9. 驗收
逐項檢查 AGENTS.md 第 11 節，可以用下面的指令檢查失效連結：
```bash
python3 - <<'EOF'
import re, pathlib
root = pathlib.Path('.')
bad = []
for f in list(root.glob('*.html')) + list(root.glob('pages/**/*.html')):
    for h in re.findall(r'href="(?![a-z]+:)([^"#]+)', f.read_text()):
        if not (f.parent / h).resolve().exists():
            bad.append((str(f), h))
print('失效連結：', bad or '無')
EOF
```

### 10. 回報
列出新增／修改的檔案、收錄或排除的店家，以及哪些欄位是「待確認」。

## 品質範例

好的 tagline：「早八開到午夜，讀書工作好去處」（具體、有資訊量）
不好的 tagline：「超讚的必訪咖啡廳」（廣告詞、沒資訊）

好的特色寫法：「評論常提到插座、座位和讀書，很適合需要久坐的時候。」
不好的寫法：「這裡的拿鐵是全台中最好喝的。」（無法查證）
