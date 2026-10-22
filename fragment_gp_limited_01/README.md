# 有限初始化的歷史片段輔助GP

python gp_search.py prepare 固定新三種子、Best-fit＋15隨機共同初始化、原始庫合法抽樣視圖、設定與hash；未執行完整候選評估。

python timed_run.py 執行9runs、每run128名義名額，全部搜索結束才做pilot_val與固定參考診斷。保存候選、結果、每代checkpoint，中斷按相同計畫續跑，不增加名額。

python analyze.py 核對預算／共用初始化／父代更新／完整根插入禁令／既有策略重找紀錄／完整軌跡與成本，產出報告並封存。

python analyze.py verify <目錄> 驗證可搬移交付。操作與限制見PROTOCOL.md，實際計時入口見RUN_SEARCH.md。已封存目錄不要重新prepare或改庫。
