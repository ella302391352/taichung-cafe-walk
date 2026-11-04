# AGENTS.md — 台中咖啡散步

> 給 AI Agent 的專案手冊。開始任何工作前，請先完整讀完本檔。
> 本檔回答一個問題：**「這個專案之後要怎麼繼續做下去？」**

---

## 1. 專案目的

把我在 Google 地圖收藏的**台中咖啡廳**，整理成一個可以在 GitHub Pages 瀏覽的多頁式導覽網站。

- 每家店有一頁介紹；每個行政區有一頁總覽；首頁可依地區瀏覽、依標籤篩選。
- 這不是一次性的網頁：之後我新增收藏時，Agent 要能**照同一套流程**，把新店加進網站，而且風格、格式完全一致。
- 下一階段的擴充目標：把「吃🍽️」餐廳清單（`raw/google-maps/list-eat.csv`，141 家）分批加入。

## 2. 資料流程（一定照這個方向走）

```
raw/google-maps/*.csv   我的收藏清單（輸入）
        ↓  上網／Google 地圖查詢
raw/research/<slug>.md  每家店的原始查詢紀錄（附來源與日期）
        ↓  整理改寫
wiki/places/<slug>.md   知識庫：店家頁（網站唯一的內容來源）
wiki/areas/<slug>.md    知識庫：地區頁
wiki/index.md           知識庫目錄
        ↓  python3 tools/build.py
pages/places/<slug>.html、pages/areas/<slug>.html、index.html、about.html
```

**核心原則：網站內容只來自 wiki，HTML 只由 `tools/build.py` 產生。**
要改網頁上的文字 → 改 wiki；要改版面 → 改 `tools/build.py` 或 `assets/style.css`。不要手動編輯 `pages/` 和 `index.html`，下次 build 會被覆蓋。

## 3. 資料夾結構

```
my-agent-project/
├── AGENTS.md                 ← 本手冊（CLAUDE.md 指向這裡）
├── CLAUDE.md
├── README.md                 ← 專案介紹（給 GitHub 讀者看）
├── index.html                ← 首頁（自動產生）
├── about.html                ← 關於頁（自動產生）
├── assets/style.css          ← 全站唯一的樣式表
├── tools/build.py            ← 網站產生器（只用 Python 標準函式庫）
├── raw/
│   ├── google-maps/          ← 收藏清單 CSV（只新增，不修改）
│   └── research/             ← 每店一檔的查詢紀錄；_excluded.md 記錄未收錄的店
├── wiki/
│   ├── index.md
│   ├── places/               ← 一店一檔
│   └── areas/                ← 一區一檔
├── pages/                    ← 自動產生，勿手改
└── skills/add-cafe/SKILL.md  ← 「新增店家」的標準作業 skill
```

## 4. 命名規則

| 項目 | 規則 | 範例 |
|---|---|---|
| 店家 slug | 小寫英文／拼音，單字用 `-` 連接；分店加地名 | `tongqi-jingzhong`、`phase-coffee-zhongshan` |
| 地區 slug | 行政區拼音 | 西區 `west`、中區 `central`、北區 `north`、南區 `south`、東區 `east`、西屯區 `xitun`、南屯區 `nantun`、北屯區 `beitun`、大里區 `dali` |
| 同一家店的檔名 | raw、wiki、html 三處都用**同一個 slug** | `raw/research/ziye.md` ↔ `wiki/places/ziye.md` ↔ `pages/places/ziye.html` |

不可使用中文檔名或空白（GitHub Pages 連結會出錯）。

## 5. 收錄規則

- 只收錄**臺中市**的店家；只收錄**仍在營業**的店家。
- 不在台中或停業的店，記錄在 `raw/research/_excluded.md`（店名、原因、地址），不放進網站。
- 若同一家店有多間分店都在收藏裡，每間分店各自一頁。

## 6. 檔案格式

### 6.1 `raw/research/<slug>.md`

查詢當下看到的原始資訊，**寫好後不再修改**；資訊有更新時，新增一段「## 更新 YYYY-MM-DD」附在檔尾。
必須包含：查詢日期、來源（網址或「Google 地圖店家頁」）、地址、營業時間、Google 類型、價位、評分與評論數、服務、官方網站／社群、評論常提到的關鍵字。

### 6.2 `wiki/places/<slug>.md`（build.py 依此產生網頁，格式不可走樣）

```markdown
---
slug: ziye
name: 自野
area: 西屯區              ← 必須和 wiki/areas/*.md 的 name 一致
area_slug: xitun
type: 咖啡店
price: $200-400
rating: 4.5
reviews: 574
tags: 每日營業, 巷弄     ← 從第 7 節的標籤表挑選，逗號分隔
tagline: 藏在巷子裡的西屯小店   ← 15 字以內，卡片副標
maps: https://www.google.com/maps/search/?api=1&query=<店名+地址 URL 編碼>
updated: 2026-11-04
---

# 自野

- 地區：臺中市西屯區
- 類型：咖啡店
- 地址：…
- 營業時間：…（查詢日期 YYYY-MM-DD）
- 價位：…
- 服務：…
- Google 地圖：…
- 標籤：#每日營業 #巷弄

## 特色
（100–200 字介紹，見第 8 節寫作規則）

## 推薦品項
評論中常被提到：…   ← 沒有資料就只寫「待確認」

## 我的筆記
（尚未填寫。去過之後由我補上。）   ← 這段只有我能寫，Agent 不可代寫

## 資料來源
- [raw/research/<slug>.md](../../raw/research/<slug>.md)（來源說明，日期）
```

開頭的 `- 欄位：值` 清單用**全形冒號「：」**，build.py 靠它讀取資訊欄。四個 `##` 標題的名稱與順序固定。

### 6.3 `wiki/areas/<slug>.md`

```markdown
---
slug: west
name: 西區
---

# 臺中市西區

一句話介紹這個區域（只寫確定的事實）。

## 店家（數量）

- [店名](../places/<slug>.md)：tagline
```

### 6.4 `wiki/index.md`

分三段：「依地區」（店多的區排前面）、「依標籤」、「未收錄」（連到 `_excluded.md`）。每次新增或移除店家都要同步更新。

## 7. 標籤表

優先使用現有標籤，避免同義詞氾濫（例如不要同時有「深夜」和「夜貓」）。真的需要新標籤時，先加進這張表再使用。

| 標籤 | 使用條件 |
|---|---|
| 深夜 | 至少一天營業到 23:00 以後 |
| 每日營業 | 沒有固定公休日 |
| 甜點 | 評論常提到甜點品項 |
| 有鹹食 | 有正餐、鹹派、義大利麵等 |
| 早午餐 | 有早午餐餐點 |
| 讀書 | 評論常提到讀書、工作、久坐 |
| 有插座 | 評論提到插座 |
| 老屋 | 老建築改建 |
| 復古 | 懷舊、昭和風裝潢 |
| 舊城區 | 位於中區、台中車站周邊 |
| 季節限定 | 甜點隨季節水果更換 |
| 餐酒館 | 晚上有酒、餐酒館氛圍 |
| 聚會 | 適合多人聚餐 |
| 親子 | 評論提到小朋友、家庭 |
| 自家烘豆 | 店家自己烘咖啡豆 |
| 個性小店 | 營業方式或風格特別鮮明 |
| 巷弄 | 位在不好找的巷子裡 |

## 8. 寫作與內容規則

- **語言**：繁體中文、台灣用語；店名保留原文（含日文、英文）。
- **語氣**：像朋友推薦，親切但不浮誇。不用「必吃」「CP 值爆表」「網美必訪」這類廣告詞。
- **不可捏造**：只能寫 raw 裡查得到的事實。評論關鍵字要寫成「評論常提到…」，不可寫成「招牌是…」「最好吃的是…」。查不到就寫「待確認」。
- **營業時間**：一律附查詢日期；資料怪異或店家說「以 IG 公告為主」時，要在介紹裡提醒讀者出發前先確認。
- **我的筆記**：只能由我本人填寫，Agent 不可代寫或改寫。
- **圖片**：不可使用 Google 地圖、部落格、IG 上的店家照片（版權）。需要視覺元素時，用 CSS、emoji 或自繪的簡單 SVG。我自己拍的照片放在 `assets/photos/<slug>-1.jpg`。

## 9. 網頁風格（改版時遵守）

- 色調：米色紙張底（`--paper`）、深咖啡色文字、焦糖色強調；顏色只能用 `assets/style.css` 中 `:root` 的變數。
- 字體：標題 Noto Serif TC（襯線），內文 Noto Sans TC。
- 首頁：主視覺標題 → 數字統計 → 標籤篩選按鈕 → 依地區分段的店家卡片。
- 店家頁：麵包屑 → 店名與 tagline → 標籤 → 左邊內文（特色／推薦品項／我的筆記／資料來源）、右邊資訊卡（地址、營業時間、價位、服務、評分、Google 地圖按鈕）。
- 手機優先：寬度 390px 時不可出現橫向捲動；手機版資訊卡排在內文上方。
- 只用 HTML + CSS + 少量原生 JavaScript，不使用需要編譯的框架。

## 10. 標準作業流程

### A. 新增一家店（最常見的任務）

詳細步驟見 `skills/add-cafe/SKILL.md`，摘要如下：
1. 確認店在收藏清單 CSV 裡（不在的話，請我先加收藏，或由我口頭確認後在 CSV 新增一列）。
2. 查詢店家資訊 → 寫 `raw/research/<slug>.md`。不在台中或已停業 → 只記到 `_excluded.md`，結束。
3. 寫 `wiki/places/<slug>.md`（第 6.2 節格式、第 7 節標籤、第 8 節寫作規則）。
4. 更新 `wiki/areas/<area>.md`；新地區就新建一個。
5. 更新 `wiki/index.md`。
6. 執行 `python3 tools/build.py`。
7. 依第 11 節驗收。

### B. 新增一個行政區
建立 `wiki/areas/<slug>.md`，若行政區不在 `tools/build.py` 的 `AREA_ORDER` 裡，把它加進去，再 build。

### C. 擴充到「吃🍽️」餐廳清單
每次一批（建議 10–20 家），先問我要哪一批；類型會從「咖啡店」擴大，標籤表可以新增「拉麵」「火鍋」等，但要先加進第 7 節的表格。首頁要分「咖啡」與「吃飯」時，修改 build.py，不要另寫一套版型。

### D. 修改版面
只改 `assets/style.css` 與 `tools/build.py`；改完重新 build，並檢查一家店頁與首頁在手機與桌面兩種寬度下的樣子。

## 11. 驗收標準（每次工作結束前都要逐項檢查並回報）

- [ ] 網站上每一家店，在 `raw/research/`、`wiki/places/`、`pages/places/` 都有同 slug 的檔案
- [ ] `wiki/index.md` 與 `index.html` 都列出所有店家與地區，數量一致
- [ ] 所有內部連結（`href` 指向本專案的檔案）都存在，沒有失效連結
- [ ] 每一頁的地址、營業時間都能在對應的 raw 檔找到；查不到的寫「待確認」
- [ ] 沒有任何網路上的店家照片；「我的筆記」沒有被 Agent 代寫
- [ ] 390px 寬度下沒有橫向捲動
- [ ] 回報本次新增／修改的檔案清單

## 12. 禁止事項

- 不可刪除或覆寫 `raw/` 內任何檔案（只能新增，或在檔尾附加更新段落）。
- 刪除 `wiki/` 檔案前必須先問我；移除店家時，改成記到 `_excluded.md`。
- 不可手動修改 `pages/`、`index.html`、`about.html`。
- 不可在網站上公開我的私人資訊（例如住址、Email）。
- 不可為了填滿版面而編造店家資訊。
