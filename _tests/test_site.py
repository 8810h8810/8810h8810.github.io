"""Static regression and content checks. No network or user record access."""
import hashlib
from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import re
import subprocess
import unittest
from urllib.parse import urlparse, unquote
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder', ROOT/'_scripts/build_site.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
BASE='775e239850f211bca95b9c1543a9c5102131ba1d'

class Page(HTMLParser):
    def __init__(self,html):
        super().__init__();self.links=[];self.ids=[];self.canon=[];self.h1=0;self.h2=0;self.metas={};self.cells=0
        self.feed(html)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag=='link' and a.get('rel')=='canonical':self.canon.append(a['href'])
        if tag=='meta':self.metas[a.get('name',a.get('http-equiv',''))]=a.get('content','')
        if tag=='h1':self.h1+=1
        if tag=='h2':self.h2+=1
        if tag=='td':self.cells+=1

pages={str(p.relative_to(ROOT)):p.read_text() for p in ROOT.rglob('index.html') if not any(part.startswith(('_','.')) for part in p.relative_to(ROOT).parts)}

class Site(unittest.TestCase):
    def test_html_structure_and_canonical(self):
        for name,html in pages.items():
            p=Page(html);self.assertEqual(p.h1,1,name);self.assertEqual(len(p.ids),len(set(p.ids)),name)
            self.assertEqual(len(p.canon),1,name);self.assertTrue(p.canon[0].startswith(builder.ORIGIN+'/'),name)
            self.assertIn('lang="ja"',html);self.assertIn('name="viewport"',html)

    def test_internal_links_and_fragments(self):
        for name,html in pages.items():
            for link in Page(html).links:
                url=urlparse(link)
                if url.netloc and url.netloc!='8810h8810.github.io':continue
                if url.scheme not in ['', 'https']:continue
                if url.path.startswith('/pet-meal-check/'):continue # Separate existing app, not copied or changed.
                if url.path:
                    target=unquote(url.path.lstrip('/'))
                    if target.endswith('/') or not target:target+='index.html'
                else:target=name
                self.assertIn(target,pages,(name,link))
                if url.fragment:self.assertIn(unquote(url.fragment),Page(pages[target]).ids,(name,link))

    def test_each_guide_has_a_distinct_action(self):
        self.assertEqual(len(builder.GUIDES),5)
        for slug in builder.GUIDES:
            html=pages[f'guide/{slug}/index.html'];self.assertGreaterEqual(Page(html).h2,3,slug)
            self.assertIn('関連するガイド',html)
        self.assertIn('共有待ち',pages['guide/share-meal-check/index.html'])
        self.assertIn('14マス',pages['guide/double-feeding/index.html'])
        self.assertIn('5秒',pages['guide/share-meal-check/index.html'])

    def test_old_urls_are_recoverable_and_redirect_to_real_sections(self):
        self.assertEqual(len(builder.REDIRECTS),6)
        for slug,target in builder.REDIRECTS.items():
            p=Page(pages[f'guide/{slug}/index.html'])
            self.assertEqual(p.metas['robots'],'noindex,follow')
            self.assertEqual(p.metas['refresh'],'0;url='+target)
            self.assertIn(target,p.links)

    def test_sitemap_contains_only_canonical_routes(self):
        tree=ET.parse(ROOT/'sitemap.xml')
        locs=[node.text for node in tree.findall('.//{*}loc')]
        self.assertEqual(len(locs),len(set(locs)))
        for slug in builder.REDIRECTS:self.assertNotIn(builder.ORIGIN+f'/guide/{slug}/',locs)
        for name,html in pages.items():
            if Page(html).metas.get('robots')=='noindex,follow':continue
            self.assertIn(Page(html).canon[0],locs,name)

    def test_home_app_links_icons_and_line_payload_are_preserved(self):
        old=subprocess.check_output(['git','show',f'{BASE}:index.html'],cwd=ROOT,text=True)
        new=pages['index.html']
        for pattern in [r'<img class="app-icon"[^>]+>',r'href="https://line.me/[^\"]+"']:
            self.assertEqual(re.findall(pattern,old),re.findall(pattern,new),pattern)
        for url in ['/pet-meal-check/','/pet-meal-check/cat/','https://unchi-shita-mvp-one.blond-ball-8409.chatgpt.site/']:
            self.assertIn(f'href="{url}"',new)

    def test_printable_chart_and_scope_limitations(self):
        html=pages['guide/paper-or-phone/index.html'];start=html.index('<table class="week-sheet">');end=html.index('</table>',start)
        self.assertEqual(Page(html[start:end]+'</table>').cells,14)
        self.assertIn('架空の例',pages['guide/poop-log/index.html'])
        self.assertIn('共有されません',pages['index.html'])

    def test_operator_contact_and_no_private_data(self):
        for name,html in pages.items():
            if Page(html).metas.get('robots')=='noindex,follow':continue
            self.assertIn('href="/contact/"',html,name)
            self.assertNotIn('8810h8810@gmail.com',html)
        self.assertIn('template=bug_report.md',pages['contact/index.html'])
        self.assertIn('招待リンク',pages['contact/index.html'])
        self.assertTrue((ROOT/'.github/ISSUE_TEMPLATE/bug_report.md').exists())

    def test_ad_identity_and_no_ad_loader_on_support_or_redirects(self):
        self.assertEqual((ROOT/'ads.txt').read_text().strip(),'google.com, pub-9642638629259048, DIRECT, f08c47fec0942fa0')
        self.assertIn('ca-pub-9642638629259048',pages['index.html'])
        for name,html in pages.items():
            if name!='index.html':self.assertNotIn('adsbygoogle.js',html,name)

    def test_generated_pages_are_reproducible(self):
        before={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in pages}
        builder.build()
        after={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in pages}
        self.assertEqual(before,after)

    def test_sources_and_internal_report_are_excluded(self):
        config=(ROOT/'_config.yml').read_text()
        for name in ['_content','_scripts','_tests','ADSENSE-REVIEW.md']:self.assertIn(name,config)

if __name__=='__main__':unittest.main(verbosity=2)
