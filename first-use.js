/* Practice only: no storage, network, analytics, or access to app records. */
(() => {
  'use strict';
  const demo = document.getElementById('try');
  if (!demo) return;
  const slots = [...demo.querySelectorAll('.demo-slot')];
  const status = document.getElementById('demo-status');
  const reset = document.getElementById('demo-reset');
  const set = (slot, checked) => {
    slot.setAttribute('aria-pressed', String(checked));
    slot.querySelector('[aria-hidden]').textContent = checked ? '✓' : '○';
    slot.querySelector('.demo-word').textContent = checked ? 'チェック済み' : '未チェック';
  };
  slots.forEach(slot => {
    set(slot, false);
    slot.disabled = false;
    slot.addEventListener('click', () => {
      const checked = slot.getAttribute('aria-pressed') !== 'true';
      set(slot, checked);
      const label = slot.getAttribute('aria-label').replace('お試し：', '');
      status.textContent = checked
        ? `${label}に練習の印を付けました。実際の表では「ごはんを出した」の目印です。もう一度押すと取り消せます。`
        : `${label}の練習の印を取り消しました。実際の表でも、空欄だけで「まだ出していない」とは断定できません。`;
    });
  });
  reset.disabled = false;
  reset.addEventListener('click', () => {
    slots.forEach(slot => set(slot, false));
    status.textContent = '練習の印をすべて消しました。実際のアプリの記録は変更していません。';
  });
  status.textContent = 'まず月曜日の朝を押してみてください。この表の印は保存されません。';
})();
