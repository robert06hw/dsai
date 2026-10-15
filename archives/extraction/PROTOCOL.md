# 三步資料、表達式、固定片段庫：零 LLM、零 GP 搜尋

以使用者最新指示為準，本次只完成三步，不執行四方法小搜尋，也不鎖定其演化預算。

1.來源限定既有 1,242 個有效歷史程式。使用 behavior_stage1_01 的 candidate_quality.csv 清單，逐一確認原結果的 valid_dev 與 valid_pools 均 true；保留全部來源與檔案 hash，不新增 stage2 程式，不依品質再挑選。pilot_dev 逐位元沿用 6001..6005，每例 5,000 物品、容量 100；保持到達順序，只評已開啟可容納箱，argmax 最大分數、平手第一個，無可容納箱才開箱。既有資料採 floor clip Weibull shape3 scale45；未重新標成論文原始 round 實例。

重跑 Best-fit、公開 EoH 與封存歷史最佳，要求平均箱數分別 2066.4、2059.4、2044.8，逐例箱數與完整決策／容量軌跡 hash 均須重現。未重現則停止。已查看的 pilot_val 保留為未來小實驗診斷，本次不評估；正式 validation/test/probe_audit 不參與新評估。

2.原語法白名單與純度檢查後，解析 score(item,bins)，按語句順序展開 local 依賴，保存每個 local、來源 line、直接依賴與展開內容。第一版僅處理純直線 NumPy 與可明確判定 shape 的運算／條件。S/V 為數值純量／同長度分數向量，BS/BV 為布林純量／向量遮罩；不把遮罩當數值分數，不支援 ragged 索引、未知 shape 或外部狀態。不能轉換者列原因；展開超 4096 運算節點／64 層列安全限制排除。

每個可轉換程式以獨立 CPU 子程序驗證，512MiB、120秒、BLAS1、至多四 worker。先用固定 64 個合法狀態比較原始／展開／保守規範化的 shape、dtype、exact 值（equal_nan）；三者相同例外僅記錄，不依它刪除片段。再對五個完整 pilot_dev 比較原始軌跡每一評分狀態的三份分數，三版本各自完整裝箱，箱數、每步選箱索引與所選容量皆須一致。原程式於 pilot_dev 無效或轉換不一致者記錄並排除，不修復來源。

3.從完整驗證通過程式的展開 score 樹抽取全部子表達式，不依品質挑來源。每個片段只能綁定標準 item/bins，不得殘留 local。記錄型別、節點數／深度、terminal 依賴、來源程式、expanded path 與 line；完整 local 依賴圖另附。原始庫對完全相同結構只存一份實體記錄，保留每次出現與來源 multiplicity，不丟失原始頻次。

整理庫再次檢查型別與輸入依賴；local 名稱因完全展開已消除，外部變數固定 item/bins。保守規範化僅移除數值 unary plus、折疊 literal unary sign 與 double negation；不重排運算、不套結合律，也不依排序行為合併。按規範化的確定結構去重。保留 Worst-fit、常數、單獨不改排序與 probe 非有限片段；有限資料相同行為只診斷，不刪庫。本次不按未來 GP 樹深／大小篩選片段，全部已驗證子表達式保留。

完成後以 fragment_library_lock.json 固定兩庫、來源、依賴、完整驗證結果及實作 hash；後續不得隨搜尋结果追加材料。歷史封存 manifest 逐檔核對不變。本次 LLM 生成0、GP 候選嘗試0，不执行 NSGA-II 或新測試集評估。
