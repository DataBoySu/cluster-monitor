import warnings
import threading
import platform
import subprocess
import os

_ToastNotifierClass = None
_has_winrt = False

# Only attempt Windows-specific imports on Windows
if platform.system() == 'Windows':
    with warnings.catch_warnings():
        # suppress the known pkg_resources deprecation warning emitted by win10toast
        warnings.simplefilter('ignore')
        try:
            from win10toast import ToastNotifier as _ToastNotifierClass
        except Exception:
            _ToastNotifierClass = None

    try:
        from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification
        from winrt.windows.data.xml.dom import XmlDocument
        _has_winrt = True
    except Exception:
        _has_winrt = False


def _safe_show_toast_win10(title, msg, duration):
    try:
        if _ToastNotifierClass is None:
            return
        n = _ToastNotifierClass()
        n.show_toast(title, msg, duration=duration, threaded=False)
    except Exception:
        pass


def _show_linux_notification(title, msg, duration):
    """Fallback for Linux using notify-send."""
    try:
        # duration is in milliseconds for notify-send
        subprocess.run(['notify-send', '-t', str(duration * 1000), title, msg], check=False)
        return True
    except Exception:
        return False


def _show_macos_notification(title, msg):
    """Fallback for macOS using AppleScript."""
    try:
        script = f'display notification "{msg}" with title "{title}"'
        subprocess.run(['osascript', '-e', script], check=False)
        return True
    except Exception:
        return False


def send_toast(title: str, msg: str, duration: int = 5, severity: str = 'info'):
    """Send a system notification if possible.
    
    Supports Windows (WinRT/win10toast), Linux (notify-send), and macOS (osascript).
    """
    system = platform.system()
    
    try:
        if system == 'Windows':
            # If winrt is available, use native Windows 10+ notifications
            if _has_winrt:
                try:
                    def _xml_escape(s):
                        return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
                    xml = f"<toast><visual><binding template='ToastGeneric'><text>{_xml_escape(title)}</text><text>{_xml_escape(msg)}</text></binding></visual></toast>"
                    from winrt.windows.data.xml.dom import XmlDocument
                    from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification
                    doc = XmlDocument()
                    doc.load_xml(xml)
                    notif = ToastNotification(doc)
                    notifier = ToastNotificationManager.create_toast_notifier()
                    notifier.show(notif)
                    return True
                except Exception:
                    pass

            if _ToastNotifierClass is not None:
                threading.Thread(target=_safe_show_toast_win10, args=(title, msg, duration), daemon=True).start()
                return True
                
        elif system == 'Linux':
            return _show_linux_notification(title, msg, duration)
            
        elif system == 'Darwin':  # macOS
            return _show_macos_notification(title, msg)
            
    except Exception:
        pass
        
    return False
