# 台中咖啡散步 ☕

把我在 Google 地圖收藏的台中咖啡廳，交給 AI Agent 依照一套固定規則整理成導覽網站。

- **網站**：`https://<你的帳號>.github.io/<repo 名稱>/`
- **規則手冊**：[AGENTS.md](AGENTS.md)（[CLAUDE.md](CLAUDE.md) 指向它）
- **新增店家 skill**：[skills/add-cafe/SKILL.md](skills/add-cafe/SKILL.md)

## 這個專案在做什麼

這不是只做一個網頁，而是建立一套「AI 能照著繼續做」的流程：

```
Google 地圖收藏 (raw/google-maps)
   → 每店查詢紀錄 (raw/research)
   → Wiki 知識庫 (wiki/)
   → python3 tools/build.py
   → 網站 (index.html、pages/)
```

目前收錄：14 家台中咖啡廳、7 個行政區。收藏清單中不在台中或已停業的 10 家記錄在 `raw/research/_excluded.md`。

## 如何新增一家店

對 AI 說：「依照 skills/add-cafe 新增 ○○○ 這家店」。AI 會讀 AGENTS.md，依序寫好 raw 查詢紀錄、wiki 頁面、更新地區與目錄，最後執行 build 並驗收。因為網頁全部由 `tools/build.py` 從 wiki 產生，新頁面的版型、標籤與寫法都會和現有頁面一致。

## 本機預覽

直接用瀏覽器開啟 `index.html` 即可；修改 wiki 後執行：

```bash
python3 tools/build.py
```

## 資料說明

店家資訊查詢自 Google 地圖店家頁（2026-11-04），營業時間可能變動，請以店家公告為準。網站未使用任何網路上的店家照片。
