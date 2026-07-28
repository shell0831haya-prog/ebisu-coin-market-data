# ebisu-coin market data feed

恵比寿コイン（ebisu-coin.com）のサイトに掲載する貴金属相場ウィジェット用のデータフィードです。
毎朝8時20分（JST）にGitHub Actionsで自動更新されます。

- `lbma_data.json` — 日次の金・銀・プラチナ先物終値（USD/troy oz）とドル円レート、直近45日分
- データ源: ニューヨーク先物市場の日次終値（GC=F / SI=F / PL=F）と USDJPY=X（Yahoo Finance チャートAPI経由）
- 生成スクリプト: `fetch_data.py`（このリポジトリ内、GitHub Actionsが毎日実行）

※ファイル名の `lbma_data.json` は互換性維持のための旧名です（現在のデータ源はLBMAではありません）。

データは情報提供のみを目的としたもので、正確性は保証されません。
