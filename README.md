# ebisu-coin market data feed

恵比寿コイン（ebisu-coin.com）のサイトに掲載する貴金属相場ウィジェット用のデータフィードです。
毎朝8時15分に自動更新されます。

- `lbma_data.json` — 日次の金・銀・プラチナ価格（USD/troy oz）とドル円レート、直近20年分
- 価格出典: LBMA（金PM・銀）/ LPPM（プラチナPM）の公表価格、為替は Yahoo Finance
- 生成スクリプト: ローカルの `fetch_lbma_prices.py` + `update_lbma_feed.sh`

データは情報提供のみを目的としたもので、正確性は保証されません。
