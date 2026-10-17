"""Build the five practical guides; source directories are excluded by Jekyll."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://8810h8810.github.io'
GUIDES = {
    'double-feeding': ('ごはんの重複を減らす確認ルール', '朝・夜の14マスで足りる用途、記録漏れへの対処、週のリセットまで。家族で使う前に決めることを整理します。'),
    'share-meal-check': ('家族共有の設定と、同期しないときの確認手順', '一人目の共有表作成から、招待、iPhoneのホーム画面への引き継ぎ、オフライン復帰までを説明します。'),
    'paper-or-phone': ('紙とスマホの選び方・手書き用の週間表', '置く場所と確認する人から記録方法を選ぶ比較表、写して使える週間表、切り替え手順を掲載します。'),
    'poop-log': ('排便の記録を完了して、履歴を確認する', 'うんちした？の記録手順、写真・状態・色の確認、家族へ伝える際の注意、記録が見つからないときの対処。'),
    'why-simple': ('機能を絞った理由と、できること・できないこと', '食事チェックと排便記録の役割を分け、実際の実装と限界、制作・確認・更新の方針を説明します。'),
}
REDIRECTS = {
    'what-to-record': '/guide/double-feeding/#scope',
    'when-routine-breaks': '/guide/double-feeding/#handoff',
    'one-place-rule': '/guide/double-feeding/#one-place',
    'keep-it-going': '/guide/why-simple/#keep',
    'poop-what-to-note': '/guide/poop-log/#fields',
    'poop-family': '/guide/poop-log/#handoff',
}

def shell(title, description, route, body):
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}｜犬と猫の暮らしの道具箱</title>
<meta name="description" content="{escape(description, quote=True)}">
<meta name="google-adsense-account" content="ca-pub-9642638629259048">
<link rel="canonical" href="{ORIGIN}{route}"><link rel="stylesheet" href="/site.css"></head>
<body><a class="skip" href="#main">本文へ</a><header class="site-header"><a class="brand" href="/">犬と猫の暮らしの道具箱</a><nav class="site-nav" aria-label="サイト内"><a href="/guide/">使い方・ガイド</a><a href="/about/">運営について</a><a href="/contact/">困ったとき</a></nav></header>
<main id="main" class="wrap"><p class="crumbs"><a href="/">トップ</a> / <a href="/guide/">使い方・ガイド</a></p><article class="card"><h1>{escape(title)}</h1><p class="meta">運営・制作：HYT JPN / 私とチャップ。　内容確認：<time datetime="2026-10-17">2026年10月17日</time></p>
{body}
</article></main><footer class="site-footer"><nav aria-label="フッター"><a href="/">トップ</a><a href="/guide/">ガイド一覧</a><a href="/about/">運営・編集方針</a><a href="/contact/">お問い合わせ・不具合報告</a><a href="/privacy/">プライバシー</a></nav><p>家庭のお世話を確認するための情報と道具です。診断・治療を提供するものではありません。</p></footer></body></html>
'''

def related(current):
    links=''.join(f'<li><a href="/guide/{slug}/">{escape(title)}</a></li>' for slug,(title,_) in GUIDES.items() if slug != current)
    return '<nav class="related" aria-label="関連するガイド"><h2>次に確認する</h2><ul>'+links+'</ul></nav>'

def build():
    for slug, (title, description) in GUIDES.items():
        content=(ROOT/'_content'/f'{slug}.html').read_text()
        (ROOT/'guide'/slug/'index.html').write_text(shell(title, description, f'/guide/{slug}/',content+related(slug)))
    for old, destination in REDIRECTS.items():
        # Same destination for users and crawlers. Old bookmarks keep working.
        html=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ガイドを統合しました</title><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url={destination}"><link rel="canonical" href="{ORIGIN}{destination.split('#')[0]}"><link rel="stylesheet" href="/site.css"></head><body><main class="wrap"><article class="card"><h1>ガイドを統合しました</h1><p>関連する説明を、具体的な手順と一緒に読めるよう整理しました。自動で移動しない場合は、<a href="{destination}">統合先のガイドを開いてください</a>。</p><p><a href="/guide/">ガイド一覧へ</a></p></article></main></body></html>'''
        (ROOT/'guide'/old/'index.html').write_text(html)
    listing='<p class="lead">使う前の判断、共有の設定、記録が残らないときの確認を、目的別にまとめています。読んで終わりではなく、表を選ぶ・設定する・保存を確認するところまで進めるガイドです。</p><ul class="guide-list">'
    for slug,(title,description) in GUIDES.items():
        listing+=f'<li><h2><a href="/guide/{slug}/">{escape(title)}</a></h2><p>{escape(description)}</p></li>'
    listing+='</ul><p class="note">内容が重なっていた記事は上のガイドへ統合しています。過去の記事のURLからも該当する説明へ移動できます。</p><p><a class="button" href="/pet-meal-check/">犬の食事チェック</a><a class="button" href="/pet-meal-check/cat/">猫の食事チェック</a></p>'
    (ROOT/'guide/index.html').write_text(shell('使い方・お世話ガイド', '食事チェックの使い方、家族共有、紙とスマホの選び方、排便記録の確認を目的別に説明します。','/guide/',listing))
    for slug in ['about','privacy','contact']:
        folder=ROOT/slug;folder.mkdir(exist_ok=True)
        title,description={
            'about':('運営・編集方針','私とチャップ。とHYT JPNの制作方針、掲載内容の確認方法、提供する道具の役割と限界。'),
            'privacy':('プライバシーポリシー','この案内サイトと関連アプリのデータ保存・任意の解析・広告・外部リンクの取り扱い。'),
            'contact':('お問い合わせ・不具合報告','記録を消さずに確認する手順と、不具合を公開報告する際に書くこと・書かないこと。'),
        }[slug]
        (folder/'index.html').write_text(shell(title,description,f'/{slug}/',(ROOT/'_content'/f'{slug}.html').read_text()))
    routes=['/','/guide/',*[f'/guide/{slug}/' for slug in GUIDES],'/about/','/contact/','/privacy/','/pet-meal-check/','/pet-meal-check/cat/']
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml+=''.join(f'  <url><loc>{ORIGIN}{route}</loc></url>\n' for route in routes)
    (ROOT/'sitemap.xml').write_text(xml+'</urlset>\n')

if __name__ == '__main__':
    build()
