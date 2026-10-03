#!/usr/bin/env python3
"""地金型金貨 買取・販売価格表 JSON（田中貴金属連動・D-020）を生成する。
GitHub Actions で毎営業日 17:30 JST に実行し price_table_latest.json を更新。
計算式は ebisu-coin/08_レポート・報告/買取業務/価格表/build_kaitori_price_table.py と同一に保つこと。
  業者買取 = 田中買取 + 業者α / 個人買取 = 田中買取 + 個人α / 当店販売 = 田中小売 − Δ（下限: 個人買取×1.10）
"""
import re, json, html, datetime, urllib.request
from pathlib import Path

URL = 'https://gold.tanaka.co.jp/commodity/souba/'
ALPHA = {'1oz': (2000, 4000, 5000), '1/2oz': (1500, 3000, 4000), '1/4oz': (1000, 2000, 3000), '1/10oz': (1000, 2000, 3000)}
SIZES = ['1oz', '1/2oz', '1/4oz', '1/10oz']
GRAMS = {'1oz': 31.1035, '1/2oz': 15.5517, '1/4oz': 7.7759, '1/10oz': 3.1103}
OUT = Path(__file__).parent / 'price_table_latest.json'


def fetch():
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/128 Safari/537.36', 'Accept-Language': 'ja,en;q=0.8'})
    with urllib.request.urlopen(req, timeout=60) as res:
        t = res.read().decode('utf-8', errors='ignore')
    m = re.search(r'地金価格<span>(\d{4})年(\d{2})月(\d{2})日 (\d{2}:\d{2})公表', t)
    pub = f'{m.group(1)}-{m.group(2)}-{m.group(3)} {m.group(4)}' if m else ''
    seg = t[t.find('id="metal_price"'):]
    g = re.search(r'class="gold">.*?retail_tax">([\d,]+) 円.*?purchase_tax">([\d,]+) 円', seg, re.S)
    gold_retail, gold_buy = int(g.group(1).replace(',', '')), int(g.group(2).replace(',', ''))
    c = t[t.find('id="coin_price_link"'):]
    c = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<script.*?</script>', '', c, flags=re.S)))
    c = re.sub(r'\s+', ' ', c)
    i = c.find('ウィーン金貨ハーモニー'); seg = c[i:i + 1500]
    pairs = re.findall(r'店頭小売価格（税込） ([\d,]+) 円 店頭買取価格（税込） ([\d,]+) 円', seg)
    coins = {sz: {'retail': int(rt.replace(',', '')), 'buy': int(by.replace(',', ''))} for sz, (rt, by) in zip(SIZES, pairs[:4])}
    if len(coins) < 4:
        raise RuntimeError('田中コイン価格の解析に失敗: ' + seg[:300])
    return pub, gold_retail, gold_buy, coins


def build(gold_buy, coins):
    rows = []
    for sz in SIZES:
        ba, ia, sd = ALPHA[sz]
        tb, tr = coins[sz]['buy'], coins[sz]['retail']
        biz = tb + ba; ind = tb + ia; sell = tr - sd
        sell = max(sell, int(ind * 1.10 // 10 * 10))
        rows.append({'size': sz, 'tanaka_buy': tb, 'tanaka_retail': tr, 'melt': round(gold_buy * GRAMS[sz]),
                     'biz_buy': biz, 'ind_buy': ind, 'sell': sell,
                     'ind_margin_pct': round((sell / 1.1 - ind / 1.1) / (sell / 1.1) * 100, 1)})
    return rows


def main():
    pub, gr, gb, coins = fetch()
    rows = build(gb, coins)
    jst = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding='utf-8'))
        if old.get('published') == pub:
            print('田中公表に変化なし（休場日など）', pub); return
    OUT.write_text(json.dumps({'published': pub, 'gold_buy_g': gb, 'gold_retail_g': gr, 'rows': rows,
                               'built': jst.strftime('%Y-%m-%d %H:%M')}, ensure_ascii=False, indent=1), encoding='utf-8')
    print('updated', pub, [(r['size'], r['ind_buy']) for r in rows])


if __name__ == '__main__':
    main()
