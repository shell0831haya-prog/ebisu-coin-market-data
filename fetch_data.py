"""
恵比寿コイン 相場データフィード生成スクリプト（GitHub Actions用・標準ライブラリのみ）。

- 金・銀・プラチナ: ニューヨーク先物市場の日次終値（GC=F / SI=F / PL=F）
- ドル円: USDJPY=X の日次終値
- 出典: Yahoo Finance チャートAPI
- 出力: lbma_data.json（直近45日分。円換算はウィジェットのJS側で行う）

店舗の値付けオペレーション（毎朝8時のスポット取得）と同じデータ源・同じ時間帯に
揃えてあり、サイトに表示する相場と値付けの基準が一致する。
毎日 8:20 JST に .github/workflows/update.yml から実行される。
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent
OUTPUT = BASE / "lbma_data.json"
K = 45  # 配信する日数

SYMBOLS = {
    "gold_usd": "GC=F",
    "silver_usd": "SI=F",
    "plat_usd": "PL=F",
    "fx": "USDJPY=X",
}


def yahoo_daily(symbol: str) -> dict:
    """日次終値を {YYYY-MM-DD: close} で返す。当日進行中の足はライブ値で補完。"""
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
           + urllib.parse.quote(symbol) + "?range=3mo&interval=1d")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                data = json.load(res)
            break
        except Exception as e:  # 一時的なレート制限などはリトライ
            last_err = e
            time.sleep(10)
    else:
        raise RuntimeError(f"{symbol}: {last_err}")

    r = data["chart"]["result"][0]
    stamps = r["timestamp"]
    closes = r["indicators"]["quote"][0]["close"]
    live = r["meta"].get("regularMarketPrice")

    out = {}
    for ts, c in zip(stamps, closes):
        d = time.strftime("%Y-%m-%d", time.gmtime(ts))
        if c is not None:
            out[d] = round(float(c), 4)
    # 進行中の足（closeがNone）はライブ値で補完
    if stamps and closes and closes[-1] is None and live is not None:
        d = time.strftime("%Y-%m-%d", time.gmtime(stamps[-1]))
        out[d] = round(float(live), 4)
    return out


def main():
    series = {key: yahoo_daily(sym) for key, sym in SYMBOLS.items()}

    # 金の日付を基準に結合。他の系列が休場の日は直前値で埋める
    dates = sorted(series["gold_usd"].keys())
    out = {"dates": []}
    for key in SYMBOLS:
        out[key] = []
    last = {key: None for key in SYMBOLS}

    for d in dates:
        vals = {}
        ok = True
        for key in SYMBOLS:
            v = series[key].get(d, last[key])
            if v is None:
                ok = False
                break
            vals[key] = v
        if not ok:
            continue
        last.update(vals)
        out["dates"].append(d)
        for key in SYMBOLS:
            out[key].append(vals[key])

    trimmed = {k: v[-K:] for k, v in out.items()}
    OUTPUT.write_text(json.dumps(trimmed))
    n = len(trimmed["dates"])
    print(f"NY先物 {n}日分を書き出しました（{trimmed['dates'][0]} 〜 {trimmed['dates'][-1]}）")
    print(f"最新: 金${trimmed['gold_usd'][-1]} 銀${trimmed['silver_usd'][-1]} "
          f"プラチナ${trimmed['plat_usd'][-1]} ドル円{trimmed['fx'][-1]}")


if __name__ == "__main__":
    main()
