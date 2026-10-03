# ebisu-coin market data feed

恵比寿コイン（ebisu-coin.com）のサイトに掲載する貴金属相場ウィジェット用のデータフィードです。
毎朝8時20分（JST）にGitHub Actionsで自動更新されます。

- `lbma_data.json` — 日次の金・銀・プラチナ先物終値（USD/troy oz）とドル円レート、直近45日分
- データ源: ニューヨーク先物市場の日次終値（GC=F / SI=F / PL=F）と USDJPY=X（Yahoo Finance チャートAPI経由）
- 生成スクリプト: `fetch_data.py`（このリポジトリ内、GitHub Actionsが毎日実行）

※ファイル名の `lbma_data.json` は互換性維持のための旧名です（現在のデータ源はLBMAではありません）。

データは情報提供のみを目的としたもので、正確性は保証されません。

- `price_table_latest.json` — 地金型金貨（1oz〜1/10oz）の買取・販売価格表。田中貴金属のコイン価格（毎営業日17:00公表）に連動し、平日17:30 JSTに `fetch_price_table.py` で更新。買取LP（?mode=f35）が参照
