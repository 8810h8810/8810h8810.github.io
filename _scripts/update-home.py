"""One-time content migration; preserve app links, icons and LINE sharing payload."""
from pathlib import Path
import re
from build_site import GUIDES

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'index.html'
source=path.read_text()
if 'rel="canonical"' not in source:
    source=source.replace('<title>', '<link rel="canonical" href="https://8810h8810.github.io/"><link rel="stylesheet" href="/site.css"><title>',1)
nav='<nav class="site-nav" aria-label="サイト内"><a href="/guide/">使い方・ガイド</a><a href="/about/">運営・編集方針</a><a href="/contact/">お問い合わせ</a></nav>'
if 'aria-label="サイト内"' not in source:
    source=source.replace('<main class="wrap">','<main class="wrap">'+nav,1)
source=source.replace('HYT JPN｜犬と猫の暮らしの道具箱','HYT JPN / 私とチャップ。｜犬と猫の暮らしの道具箱')
guides='<section class="card"><h2>目的から選ぶ、使い方ガイド</h2><ul class="guide-list">'
for slug,(title,description) in GUIDES.items():
    guides+=f'<li><h3><a href="/guide/{slug}/">{title}</a></h3><p>{description}</p></li>'
guides+='</ul></section>'
pattern=r'<section class="card"><h2>家族でお世話するヒント</h2>.*?</section>'
if re.search(pattern,source,flags=re.S):
    source=re.sub(pattern,lambda _:guides,source,count=1,flags=re.S)
if 'id="choose"' not in source:
    choose='''<section class="card" id="choose"><h2>使い始める前に、役割を確認</h2><ul><li><strong>食事を出したか確認したい：</strong>食事チェックの犬版・猫版。朝・夜の14マスを手動で使い、週の終わりにリセットします。日付付きの履歴や量・時刻の保存はありません。</li><li><strong>家族のスマホでも同じ表を見たい：</strong>アプリを開くだけでは共有されません。一人が表を作り、もう一人が招待リンクで参加します。<a href="/guide/share-meal-check/">設定手順と同期の確認方法</a>を用意しています。</li><li><strong>排便と気づいた状態を残したい：</strong>別アプリ『うんちした？』へ。開始後は完了まで進み、履歴を確認します。アプリのURLを送ることと、自分の端末の記録を渡すことは別です。</li></ul><p class="small">食事・治療に関する判断を、チェックの有無や便の選択肢だけに任せる道具ではありません。</p></section>'''
    source=source.replace('<section class="card"><h2>家族に教える</h2>',choose+'<section class="card"><h2>家族に教える</h2>',1)
source=source.replace('<a href="/about/">このサイトについて</a>','<a href="/about/">運営・編集方針</a><a href="/contact/">お問い合わせ・不具合報告</a>')
path.write_text(source)
