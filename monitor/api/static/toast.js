// toast.js - right-side popout toast API used across the dashboard

/*
  Usage:
    window.showToast('Message text', { level: 'green'|'yellow'|'red'|'info', duration: 5000 });
    window.showSuccess('OK'); window.showError('Fail'); window.showWarn('Warn');
  This implementation renders toasts on the top-right and shows the provided message text.
*/

function ensureRightContainer() {
    let c = document.getElementById('toast-container-right');
    if (c) return c;
    c = document.createElement('div');
    c.id = 'toast-container-right';
    c.style.position = 'fixed';
    c.style.top = '12px';
    c.style.right = '12px';
    c.style.display = 'flex';
    c.style.flexDirection = 'column';
    c.style.alignItems = 'flex-end';
    c.style.gap = '8px';
    c.style.zIndex = '20000';
    document.body.appendChild(c);
    return c;
}

function makeToastElement(message, bg, color) {
    const card = document.createElement('div');
    card.className = 'toast-card';
    card.style.background = bg;
    card.style.color = color;
    card.style.padding = '10px 14px';
    card.style.borderRadius = '8px';
    card.style.boxShadow = '0 8px 24px rgba(0,0,0,0.35)';
    // fixed width so all toasts are the same size; extra content wraps vertically
    card.style.width = '320px';
    card.style.maxWidth = '320px';
    card.style.fontWeight = '600';
    card.style.transform = 'translateX(110%)';
    card.style.transition = 'transform 260ms ease, opacity 200ms ease';
    card.style.opacity = '0';

    const text = document.createElement('div');
    text.style.whiteSpace = 'normal';
    text.style.wordBreak = 'break-word';
    text.style.flex = '1 1 auto';
    text.textContent = message;
    card.appendChild(text);

    const close = document.createElement('button');
    close.textContent = '\u00D7';
    close.title = 'Dismiss';
    close.style.marginLeft = '8px';
    close.style.border = 'none';
    close.style.background = 'transparent';
    close.style.color = color;
    close.style.cursor = 'pointer';
    close.style.fontSize = '16px';
    close.style.padding = '0 6px';
    close.style.float = 'none';
    close.style.marginLeft = '12px';
    close.onclick = (e) => { e.stopPropagation(); hide(); };

    // add a small container for text + close positioned right
    const wrapper = document.createElement('div');
    wrapper.style.display = 'flex';
    wrapper.style.justifyContent = 'space-between';
    wrapper.style.alignItems = 'center';
    wrapper.style.gap = '8px';
    wrapper.appendChild(text);
    wrapper.appendChild(close);

    card.innerHTML = '';
    card.appendChild(wrapper);

    function show() {
        requestAnimationFrame(() => { card.style.transform = 'translateX(0)'; card.style.opacity = '1'; });
    }
    function hide() {
        card.style.transform = 'translateX(110%)';
        card.style.opacity = '0';
        setTimeout(() => { try { card.remove(); } catch (e) {} }, 300);
    }
    return { card, show, hide };
}

function toast(message, opts = {}) {
    const duration = (typeof opts.duration === 'number') ? opts.duration : 5000;
    const level = (opts && opts.level) ? opts.level : (opts && opts.variant) ? opts.variant : 'red';

    let bg = '#ef4444';
    let color = '#fff';
    if (level === 'green') { bg = '#16a34a'; color = '#fff'; }
    else if (level === 'yellow') { bg = '#f59e0b'; color = '#000'; }
    else if (level === 'red') { bg = '#ef4444'; color = '#fff'; }
    else if (level === 'info') { bg = '#f59e0b'; color = '#000'; }

    const container = ensureRightContainer();
    const t = makeToastElement(message, bg, color);
    container.appendChild(t.card);
    // show animation
    t.show();

    if (duration > 0) {
        const timer = setTimeout(() => { t.hide(); }, duration);
        // clear timer on manual hide
        const oldHide = t.hide;
        t.hide = function() { clearTimeout(timer); oldHide(); };
    }
    return { remove: t.hide };
}

// Global API
window.showToast = function(msg, opts = {}) {
    const message = (msg === null || msg === undefined) ? '' : String(msg);
    return toast(message, opts);
};

window.showError = function(msg, duration = 8000) { return window.showToast(msg, { level: 'red', duration }); };
window.showSuccess = function(msg, duration = 5000) { return window.showToast(msg, { level: 'green', duration }); };
window.showWarn = function(msg, duration = 6000) { return window.showToast(msg, { level: 'yellow', duration }); };
