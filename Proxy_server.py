import os
import re
import json
import base64
import urllib.parse
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
import uvicorn
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# === НАСТРОЙКИ ===
PROXY_DOMAIN = os.getenv("PROXY_DOMAIN", "potyjnovpn.apruxdomain.store")
HWID = os.getenv("HWID", "CB522960-E2A9-7A19-12CB-FD12FEC71E19")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "ciorsa")

app = FastAPI(title="PotyjnoVPN Proxy")

# === HTML-ШАБЛОН С ГРАДИЕНТОМ ===
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PotyjnoVPN</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            min-height: 100vh;
            background: linear-gradient(180deg, 
                #0a0a0a 0%,
                #0a1a2a 20%,
                #0d2847 40%,
                #1a3a6a 55%,
                #3a6a8a 70%,
                #6a7a3a 85%,
                #b8940a 100%
            );
            color: #ffffff;
            padding: 20px;
            display: flex;
            justify-content: center;
        }
        
        .container {
            max-width: 800px;
            width: 100%;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 32px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 1px;
            text-shadow: 0 2px 20px rgba(0, 100, 255, 0.3);
        }
        
        .header h1 span {
            color: #60a5fa;
        }
        
        .header .subtitle {
            color: #94a3b8;
            font-size: 16px;
            margin-top: 5px;
            letter-spacing: 2px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        
        .stat-item {
            display: flex;
            flex-direction: column;
        }
        
        .stat-item .label {
            font-size: 12px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-item .value {
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
            margin-top: 2px;
        }
        
        .stat-item .value.highlight {
            color: #60a5fa;
        }
        
        .actions {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 25px;
        }
        
        .btn {
            flex: 1;
            min-width: 140px;
            padding: 12px 20px;
            border: none;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.08);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .btn:hover {
            background: rgba(96, 165, 250, 0.2);
            border-color: rgba(96, 165, 250, 0.3);
            transform: translateY(-1px);
            box-shadow: 0 8px 25px rgba(96, 165, 250, 0.15);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn-primary {
            background: rgba(96, 165, 250, 0.2);
            border-color: rgba(96, 165, 250, 0.3);
        }
        
        .btn-primary:hover {
            background: rgba(96, 165, 250, 0.3);
        }
        
        .count {
            text-align: center;
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 20px;
            letter-spacing: 0.5px;
        }
        
        .count span {
            color: #60a5fa;
            font-weight: 600;
        }
        
        .keys-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 30px;
        }
        
        .key-card {
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 16px 20px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            transition: all 0.3s ease;
        }
        
        .key-card:hover {
            border-color: rgba(96, 165, 250, 0.15);
            background: rgba(0, 0, 0, 0.6);
        }
        
        .key-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .key-protocol {
            font-size: 16px;
            font-weight: 700;
            color: #60a5fa;
            letter-spacing: 0.3px;
        }
        
        .key-address {
            font-size: 14px;
            color: #94a3b8;
            font-weight: 400;
            margin-left: 8px;
        }
        
        .btn-copy-key {
            padding: 6px 14px;
            border: none;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(96, 165, 250, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(96, 165, 250, 0.15);
            white-space: nowrap;
        }
        
        .btn-copy-key:hover {
            background: rgba(96, 165, 250, 0.25);
            transform: scale(1.02);
        }
        
        .btn-copy-key.copied {
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            border-color: rgba(34, 197, 94, 0.2);
        }
        
        .key-details {
            display: flex;
            flex-wrap: wrap;
            gap: 6px 16px;
            font-size: 13px;
            color: #c8d0dc;
        }
        
        .key-details .tag {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: rgba(255, 255, 255, 0.05);
            padding: 2px 10px;
            border-radius: 6px;
            font-size: 12px;
            color: #94a3b8;
        }
        
        .key-details .tag .label {
            color: #64748b;
        }
        
        .key-details .tag .value {
            color: #e2e8f0;
            font-weight: 500;
        }
        
        .key-details .tag .value.highlight {
            color: #60a5fa;
        }
        
        .footer {
            text-align: center;
            color: #475569;
            font-size: 13px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            letter-spacing: 0.5px;
        }
        
        .footer a {
            color: #60a5fa;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        .loading {
            text-align: center;
            padding: 40px 20px;
            color: #94a3b8;
        }
        
        .error {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            color: #f87171;
        }
        
        @media (max-width: 600px) {
            .stats {
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                padding: 14px;
            }
            
            .stat-item .value {
                font-size: 16px;
            }
            
            .actions {
                flex-direction: column;
            }
            
            .btn {
                min-width: unset;
            }
            
            .key-header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .key-details {
                font-size: 12px;
                gap: 4px 12px;
            }
            
            .container {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1># <span>PotyjnoVPN</span></h1>
            <div class="subtitle">подписка</div>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat-item">
                <span class="label">📊 Использовано</span>
                <span class="value">{used}</span>
            </div>
            <div class="stat-item">
                <span class="label">📈 Осталось</span>
                <span class="value">{remaining}</span>
            </div>
            <div class="stat-item">
                <span class="label">📋 Лимит</span>
                <span class="value">{limit}</span>
            </div>
            <div class="stat-item">
                <span class="label">📅 Действует</span>
                <span class="value">{expiry}</span>
            </div>
        </div>
        
        <div class="actions">
            <button class="btn btn-primary" onclick="copyAllKeys()">📋 Скопировать все ключи</button>
            <button class="btn btn-primary" onclick="copyProxyLink()">🔗 Скопировать ссылку</button>
        </div>
        
        <div class="count">ключи · <span id="keys-count">{count}</span></div>
        
        <div class="keys-list" id="keys-list">
            {keys_html}
        </div>
        
        <div class="footer">
            ⚡ proxied через <a href="https://t.me/{channel}" target="_blank">PotyjnoVPN</a>
        </div>
    </div>
    
    <script>
        function copyToClipboard(text) {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(() => {
                    showToast('✅ Скопировано!');
                }).catch(() => {
                    fallbackCopy(text);
                });
            } else {
                fallbackCopy(text);
            }
        }
        
        function fallbackCopy(text) {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                showToast('✅ Скопировано!');
            } catch (e) {
                showToast('❌ Ошибка копирования');
            }
            document.body.removeChild(textarea);
        }
        
        function showToast(message) {
            const toast = document.createElement('div');
            toast.textContent = message;
            toast.style.cssText = `
                position: fixed;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0, 0, 0, 0.85);
                backdrop-filter: blur(10px);
                color: #fff;
                padding: 12px 24px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 500;
                z-index: 1000;
                border: 1px solid rgba(255,255,255,0.08);
                animation: fadeInUp 0.3s ease;
                max-width: 90%;
                text-align: center;
            `;
            document.body.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.5s ease';
                setTimeout(() => toast.remove(), 500);
            }, 2500);
        }
        
        function copyAllKeys() {
            const keys = document.querySelectorAll('.key-full-link');
            const texts = [];
            keys.forEach(el => {
                if (el.textContent.trim()) {
                    texts.push(el.textContent.trim());
                }
            });
            if (texts.length === 0) {
                showToast('❌ Нет ключей для копирования');
                return;
            }
            copyToClipboard(texts.join('\\n'));
        }
        
        function copyProxyLink() {
            const link = window.location.href;
            copyToClipboard(link);
        }
        
        function copyKey(link) {
            copyToClipboard(link);
        }
        
        // Добавляем стили для анимации
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateX(-50%) translateY(20px); }
                to { opacity: 1; transform: translateX(-50%) translateY(0); }
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>
"""

# === ПАРСИНГ КОНФИГОВ ===

def parse_configs(content: str) -> List[str]:
    """Извлекает все конфиги (vless://, trojan://, hy2://) из текста."""
    patterns = [
        r'vless://[^\s<>"\'{}|\\^`\[\]]+',
        r'trojan://[^\s<>"\'{}|\\^`\[\]]+',
        r'(?:hysteria2|hy2)://[^\s<>"\'{}|\\^`\[\]]+',
    ]
    configs = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        configs.extend(matches)
    return configs

def extract_param(url: str, param: str) -> Optional[str]:
    """Извлекает параметр из URL-строки запроса."""
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    return params.get(param, [None])[0]

def format_config_for_display(config: str) -> Dict[str, Any]:
    """Форматирует конфиг для отображения в карточке."""
    if not config.startswith(("vless://", "trojan://", "hysteria2://", "hy2://")):
        return None
    
    parsed = urllib.parse.urlparse(config)
    scheme = parsed.scheme
    
    # Извлекаем адрес и порт
    netloc = parsed.netloc
    if '@' in netloc:
        userinfo, hostport = netloc.split('@', 1)
    else:
        userinfo = ""
        hostport = netloc
    
    if ':' in hostport:
        host, port = hostport.split(':', 1)
    else:
        host = hostport
        port = "443"
    
    # Параметры
    params = urllib.parse.parse_qs(parsed.query)
    params_flat = {k: v[0] if v else "" for k, v in params.items()}
    
    # Определяем протокол
    protocol = scheme.upper().replace("HY2", "HYSTERIA2")
    
    # Формируем данные для карточки
    display = {
        "protocol": protocol,
        "host": host,
        "port": port,
        "full": config,
        "params": {}
    }
    
    # Важные параметры для отображения
    important = ["type", "security", "flow", "sni", "fp", "pbk", "sid", "path", "host", "serviceName"]
    for key in important:
        if key in params_flat and params_flat[key]:
            display["params"][key] = params_flat[key]
    
    return display

def parse_subscription_status(content: str) -> Dict[str, str]:
    """Парсит статус подписки (трафик, срок, лимиты)."""
    status = {
        "used": "0 ГБ",
        "remaining": "∞",
        "limit": "без лимита",
        "expiry": "бессрочно"
    }
    
    # Ищем использованный трафик
    used_match = re.search(r'Использовано\s*(\d+\.?\d*)\s*(ГБ|МБ|TB|GB|MB)', content, re.IGNORECASE)
    if used_match:
        status["used"] = f"{used_match.group(1)} {used_match.group(2)}"
    
    # Ищем остаток
    remaining_match = re.search(r'Осталось\s*(\d+\.?\d*)\s*(ГБ|МБ|TB|GB|MB)', content, re.IGNORECASE)
    if remaining_match:
        status["remaining"] = f"{remaining_match.group(1)} {remaining_match.group(2)}"
    
    # Ищем лимит
    limit_match = re.search(r'Лимит\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
    if limit_match:
        limit_text = limit_match.group(1).strip()
        if "без лимита" in limit_text.lower() or "∞" in limit_text:
            status["limit"] = "без лимита"
        else:
            status["limit"] = limit_text
    
    # Ищем дату окончания
    expiry_match = re.search(r'Действует\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
    if expiry_match:
        expiry_text = expiry_match.group(1).strip()
        if "бессрочно" in expiry_text.lower() or "∞" in expiry_text:
            status["expiry"] = "бессрочно"
        else:
            status["expiry"] = expiry_text
    
    return status

# === ОСНОВНОЙ ЭНДПОИНТ ===

@app.get("/{path:path}")
async def proxy_handler(request: Request, path: str):
    """Обрабатывает все запросы к прокси."""
    # Получаем оригинальную ссылку из пути
    original_url = path
    
    if not original_url.startswith(("http://", "https://")):
        original_url = "https://" + original_url
    
    # Получаем параметры запроса
    query_params = dict(request.query_params)
    client = query_params.get("u", "Happ")
    device = query_params.get("d", "Android")
    model = query_params.get("model", "")
    os_ver = query_params.get("os", "")
    hwid = query_params.get("h", HWID)
    
    try:
        # Запрашиваем оригинальную подписку
        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": f"{client}/{device}",
                "X-HWID": hwid,
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
            }
            if model:
                headers["X-Device-Model"] = model
            if os_ver:
                headers["X-OS-Version"] = os_ver
            
            async with session.get(original_url, headers=headers, timeout=30) as resp:
                content = await resp.text()
        
        # Парсим статус
        status = parse_subscription_status(content)
        
        # Извлекаем конфиги
        configs = parse_configs(content)
        
        # Формируем HTML-страницу
        if configs:
            keys_html = ""
            for config in configs:
                display = format_config_for_display(config)
                if not display:
                    continue
                
                # Строим строку параметров
                params_str = ""
                for key, value in display["params"].items():
                    params_str += f'<span class="tag"><span class="label">{key}:</span> <span class="value highlight">{value}</span></span>'
                
                if not params_str:
                    params_str = '<span class="tag">нет параметров</span>'
                
                keys_html += f"""
                <div class="key-card">
                    <div class="key-header">
                        <div>
                            <span class="key-protocol">{display["protocol"]}</span>
                            <span class="key-address">{display["host"]}:{display["port"]}</span>
                        </div>
                        <button class="btn-copy-key" onclick="copyKey('{display['full']}')">📋 Копировать</button>
                    </div>
                    <div class="key-details" style="display:none;">
                        {params_str}
                    </div>
                    <div class="key-full-link" style="display:none;">{display['full']}</div>
                </div>
                """
            
            # Заменяем плейсхолдеры
            page = HTML_TEMPLATE.format(
                used=status["used"],
                remaining=status["remaining"],
                limit=status["limit"],
                expiry=status["expiry"],
                count=len(configs),
                keys_html=keys_html,
                channel=CHANNEL_USERNAME
            )
            
            return HTMLResponse(content=page)
        else:
            # Если конфигов нет, показываем ошибку
            error_page = f"""
            <!DOCTYPE html>
            <html>
            <head><title>PotyjnoVPN</title>
            <style>
                body {{ background: #0a0a0a; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                .error {{ text-align: center; padding: 40px; }}
                .error h1 {{ color: #f87171; }}
                .error p {{ color: #94a3b8; }}
            </style>
            </head>
            <body>
                <div class="error">
                    <h1>⚠️ Нет конфигов</h1>
                    <p>Не удалось найти ключи в подписке</p>
                    <p style="font-size:12px;color:#475569;margin-top:20px;">⚡ proxied через PotyjnoVPN</p>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=error_page, status_code=404)
            
    except asyncio.TimeoutError:
        error_page = """
        <!DOCTYPE html>
        <html>
        <head><title>PotyjnoVPN</title>
        <style>
            body { background: #0a0a0a; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .error { text-align: center; padding: 40px; }
            .error h1 { color: #fbbf24; }
            .error p { color: #94a3b8; }
        </style>
        </head>
        <body>
            <div class="error">
                <h1>⏱️ Таймаут</h1>
                <p>Сервер подписки не отвечает</p>
                <p style="font-size:12px;color:#475569;margin-top:20px;">⚡ proxied через PotyjnoVPN</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_page, status_code=504)
        
    except Exception as e:
        error_page = f"""
        <!DOCTYPE html>
        <html>
        <head><title>PotyjnoVPN</title>
        <style>
            body {{ background: #0a0a0a; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .error {{ text-align: center; padding: 40px; }}
            .error h1 {{ color: #f87171; }}
            .error p {{ color: #94a3b8; }}
        </style>
        </head>
        <body>
            <div class="error">
                <h1>❌ Ошибка</h1>
                <p>{str(e)[:200]}</p>
                <p style="font-size:12px;color:#475569;margin-top:20px;">⚡ proxied через PotyjnoVPN</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_page, status_code=500)

# === ЗАПУСК ===
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "proxy_server:app",
        host="0.0.0.0",
        port=port,
        reload=False
)
  
