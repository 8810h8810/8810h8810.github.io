"""Content regressions for the four meal guides. Static checks, not live app QA."""
from pathlib import Path
import unittest
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]

class MealGuides(unittest.TestCase):
    def page(self, slug):
        source = (ROOT / '_content' / f'{slug}.html').read_text()
        page = (ROOT / 'guide' / slug / 'index.html').read_text()
        self.assertIn(source, page)
        return page

    def test_join_explains_no_local_merge_and_uses_real_feeding(self):
        page = self.page('share-meal-check')
        for text in ['端末内の印を共有表へ自動で足す処理はありません',
                     '次に実際にごはんを出したとき', '実際の食事と異なる印を付けない']:
            self.assertIn(text, page)
        self.assertNotIn('テスト用にマスを押します', page)

    def test_distinguishes_pending_cached_display_and_failed_local_save(self):
        page = self.page('share-meal-check')
        for text in ['端末に保存済み・接続できたら共有します',
                     '共有に接続できません。端末の記録を表示中',
                     '保存できませんでした。端末の空き容量やブラウザの設定を確認してね。',
                     'その操作は保存できていません', '端末への保存に成功した場合',
                     'すべての端末が同時に最新であることを示す表示ではありません']:
            self.assertIn(text, page)

    def test_double_feeding_considers_stale_remote_state(self):
        page = self.page('double-feeding')
        self.assertIn('空欄でも家族に確認します', page)
        self.assertIn('/guide/share-meal-check/#offline', page)
        self.assertIn('一週間の終わりは手動でリセットする', page)

    def test_paper_is_battery_independent_not_phone(self):
        page = self.page('paper-or-phone')
        self.assertIn('電池切れでも記録・確認したい</td><td>紙とペン', page)
        self.assertIn('オフライン対応のアプリでも、端末の電池は必要', page)
        self.assertIn('どの端末でもオフラインで使えると保証するものではありません', page)
        self.assertNotIn('電池・通信に左右されたくない', page)

    def test_design_explains_storage_and_foreground_retry_limits(self):
        page = self.page('why-simple')
        for text in ['端末への保存に成功した操作', '画面を開いている間に再送',
                     'ブラウザのデータ削除は記録を失う原因',
                     '端末内の印を自動で合流させる機能ではありません',
                     'すべてのiPhoneや実際のFirebase通信で動作を確認したこととは区別']:
            self.assertIn(text, page)

class Images(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.images=[]; self.figures=0; self.captions=0; self.feed(html)
    def handle_starttag(self, tag, attrs):
        if tag == 'img': self.images.append(dict(attrs))
        if tag == 'figure': self.figures += 1
        if tag == 'figcaption': self.captions += 1

class GuideVisuals(unittest.TestCase):
    def test_real_screenshot_files_dimensions_and_accessibility(self):
        expected={'dog-empty-local.jpg':('540','930'), 'cat-empty-local.jpg':('540','930'),
                  'sharing-controls-local.jpg':('540','155'), 'join-empty-dialog.jpg':('460','595')}
        for slug,count in [('double-feeding',2),('share-meal-check',2),('paper-or-phone',1),('why-simple',1)]:
            page=(ROOT/'guide'/slug/'index.html').read_text()
            parsed=Images(page)
            self.assertEqual(len(parsed.images),count)
            self.assertEqual(parsed.figures,parsed.captions)
            for image in parsed.images:
                self.assertTrue((ROOT/image['src'].lstrip('/')).is_file())
                self.assertEqual((image['width'],image['height']),expected[Path(image['src']).name])
                self.assertGreater(len(image.get('alt','')),10)
                self.assertEqual(image.get('loading'),'lazy')
            self.assertIn('2026年11月7日撮影',page)
            if slug != 'double-feeding': self.assertNotIn('<video',page)

    def test_video_is_opt_in_captioned_and_honestly_labeled(self):
        page=(ROOT/'guide/double-feeding/index.html').read_text()
        class Media(HTMLParser):
            def __init__(self): super().__init__(); self.tags={}
            def handle_starttag(self,tag,attrs):
                if tag in ['video','source','track']: self.tags[tag]=dict(attrs)
        media=Media();media.feed(page)
        video=media.tags['video'];source=media.tags['source'];track=media.tags['track']
        self.assertIn('controls',video);self.assertIn('playsinline',video)
        self.assertEqual(video['preload'],'none')
        self.assertNotIn('autoplay',video);self.assertNotIn('loop',video)
        self.assertEqual((video['width'],video['height']),('720','1280'))
        self.assertEqual(source['type'],'video/mp4')
        self.assertEqual(track['kind'],'captions');self.assertEqual(track['srclang'],'ja')
        for path in [video['poster'],source['src'],track['src']]:
            self.assertTrue((ROOT/path.lstrip('/')).is_file())
        self.assertTrue((ROOT/track['src'].lstrip('/')).read_text().startswith('WEBVTT'))
        self.assertIn('動画の説明を文章で読む',page)
        for text in ['0–6秒','6–11秒','11–17秒','17–23秒','23–29秒',
                     '操作・同期の録画ではなく','共有の成功を実証するものではありません']:
            self.assertIn(text,page)
        self.assertLess(page.index('<video'),page.index('<nav class="toc"'))

    def test_mobile_stack_and_printable_paper_remain_supported(self):
        css=(ROOT/'site.css').read_text()
        self.assertIn('.guide-screen-grid,.guide-paper-comparison{grid-template-columns:1fr}',css)
        self.assertIn('.guide-paper-comparison{display:block}',css)
        page=(ROOT/'guide/paper-or-phone/index.html').read_text()
        self.assertIn('class="print-sheet"',page)
        self.assertIn('class="week-sheet"',page)

if __name__ == '__main__':
    unittest.main(verbosity=2)
