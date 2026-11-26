const fontButton = document.querySelector('.font-button');
const fontPreference = 'seodaemun-large-text';

function setLargeText(enabled) {
  document.documentElement.classList.toggle('large-text', enabled);
  fontButton.setAttribute('aria-pressed', String(enabled));
}

try {
  setLargeText(localStorage.getItem(fontPreference) === 'true');
} catch {
  setLargeText(false);
}

fontButton.hidden = false;
fontButton.addEventListener('click', () => {
  const enabled = fontButton.getAttribute('aria-pressed') !== 'true';
  setLargeText(enabled);
  try {
    localStorage.setItem(fontPreference, String(enabled));
  } catch {
    // The current page still respects the chosen text size.
  }
});

const menu = document.querySelector('.more');
document.addEventListener('click', (event) => {
  if (!menu.contains(event.target) || event.target.closest('.extra a')) menu.open = false;
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menu.open) {
    menu.open = false;
    menu.querySelector('summary').focus();
  }
});

const frame = document.querySelector('.photo-frame');
if (frame) {
  const toggle = document.querySelector('.photo-toggle');
  const help = document.querySelector('.pan-help');
  let zoomed = false;
  let drag = null;
  let x = 0;
  let y = 0;
  function pan(nextX, nextY) {
    const limitX = frame.clientWidth / 2;
    const limitY = frame.clientHeight / 2;
    x = Math.max(-limitX, Math.min(limitX, nextX));
    y = Math.max(-limitY, Math.min(limitY, nextY));
    frame.style.setProperty('--pan-x', x + 'px');
    frame.style.setProperty('--pan-y', y + 'px');
  }
  toggle.hidden = false;
  toggle.addEventListener('click', () => {
    zoomed = !zoomed;
    frame.classList.toggle('zoomed', zoomed);
    toggle.setAttribute('aria-pressed', String(zoomed));
    toggle.textContent = zoomed ? '원래 크기' : '사진 확대';
    frame.tabIndex = zoomed ? 0 : -1;
    help.hidden = !zoomed;
    pan(0, 0);
    if (zoomed) frame.focus({preventScroll:true});
  });
  frame.addEventListener('pointerdown', event => {
    if (!zoomed || !event.isPrimary || event.button !== 0) return;
    frame.setPointerCapture(event.pointerId);
    drag = {id:event.pointerId, left:event.clientX-x, top:event.clientY-y};
    frame.classList.add('dragging');
  });
  frame.addEventListener('pointermove', event => {
    if (drag && event.pointerId === drag.id) pan(event.clientX-drag.left, event.clientY-drag.top);
  });
  frame.addEventListener('lostpointercapture', () => {
    drag = null;
    frame.classList.remove('dragging');
  });
  frame.addEventListener('keydown', event => {
    if (!zoomed) return;
    if (event.key === 'Escape') { toggle.click(); toggle.focus(); return; }
    const steps = {ArrowLeft:[32,0], ArrowRight:[-32,0], ArrowUp:[0,32], ArrowDown:[0,-32]};
    if (steps[event.key]) {
      event.preventDefault();
      const [dx,dy] = steps[event.key];
      pan(x+dx,y+dy);
    }
  });
  window.addEventListener('resize', () => pan(x,y));
}
