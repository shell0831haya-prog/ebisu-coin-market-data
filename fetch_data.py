"""
恵比寿コイン 相場データフィード生成スクリプト（GitHub Actions用・標準ライブラリのみ）。

- 金・銀・プラチナ: LBMA/LPPM公式サイトの公開JSON（金・プラチナはPM価格、銀は正午の価格）
- ドル円: frankfurter.dev 経由のECB（欧州中央銀行）公式参照レート
- 出力: lbma_data.json（直近20年分。円換算はウィジェットのJS側で行う）

毎日 8:20 JST に .github/workflows/update.yml から実行される。
"""

import bisect
import json
import urllib.request
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).parent
OUTPUT = BASE / "lbma_data.json"

LBMA = {
    "gold": "https://prices.lbma.org.uk/json/gold_pm.json",
    "silver": "https://prices.lbma.org.uk/json/silver.json",
    "platinum": "https://prices.lbma.org.uk/json/platinum_pm.json",
}
FX_API = "https://api.frankfurter.dev/v1/{start}..{end}?base=USD&symbols=JPY"

START = (date.today() - timedelta(days=int(20.6 * 365.25))).isoformat()


def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "ebisu-coin-feed/1.0"})
    with urllib.request.urlopen(req, timeout=90) as res:
        return json.load(res)


def fetch_metal(url: str) -> dict:
    return {r["d"]: float(r["v"][0]) for r in get_json(url)
            if r["d"] >= START and r.get("v") and r["v"][0]}


def fetch_fx() -> dict:
    data = get_json(FX_API.format(start=START, end=date.today().isoformat()))
    return {d: round(v["JPY"], 2) for d, v in data["rates"].items()}


def main():
    gold = fetch_metal(LBMA["gold"])
    silver = fetch_metal(LBMA["silver"])
    platinum = fetch_metal(LBMA["platinum"])
    fx = fetch_fx()
    fx_keys = sorted(fx.keys())

    def fx_on_or_before(d: str):
        i = bisect.bisect_right(fx_keys, d) - 1
        return fx[fx_keys[i]] if i >= 0 else None

    dates, g, s, p, f_out = [], [], [], [], []
    last_s = last_p = None
    for d in sorted(gold.keys()):  # 金の公表日を基準に結合、休場の系列は直前値
        f = fx_on_or_before(d)
        sv = silver.get(d, last_s)
        pv = platinum.get(d, last_p)
        if f is None or sv is None or pv is None:
            continue
        last_s, last_p = sv, pv
        dates.append(d)
        g.append(round(gold[d], 2))
        s.append(round(sv, 3))
        p.append(round(pv, 2))
        f_out.append(f)

    OUTPUT.write_text(json.dumps(
        {"dates": dates, "gold_usd": g, "silver_usd": s, "plat_usd": p, "fx": f_out}))
    print(f"{len(dates)}日分（{dates[0]} 〜 {dates[-1]}）を書き出しました")


if __name__ == "__main__":
    main()
