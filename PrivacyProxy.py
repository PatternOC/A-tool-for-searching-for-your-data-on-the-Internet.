import webbrowser
import re
import getpass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
import requests
import random
import socket
import threading
import json
from bs4 import BeautifulSoup
import whois

# Список бесплатных прокси (будет обновляться автоматически)
PROXY_LIST = [
    "http://20.206.106.192:80",
    "http://72.10.164.178:80",
    "http://103.187.168.149:8080",
]

# Функция для обновления списка прокси
def update_proxy_list():
    global PROXY_LIST
    try:
        response = requests.get("https://free-proxy-list.net/", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:10]  # Первые 10 прокси
            PROXY_LIST = [f"http://{row.find_all('td')[0].text}:{row.find_all('td')[1].text}" for row in rows if row.find_all('td')]
        print("Список прокси обновлён.")
    except Exception as e:
        print(f"Ошибка при обновлении прокси: {str(e)}")

# Функция для проверки силы пароля
def check_password_strength(password):
    if len(password) < 8:
        return "Пароль слишком короткий. Используйте минимум 8 символов."
    if not re.search(r"[A-Z]", password):
        return "Пароль должен содержать хотя бы одну заглавную букву."
    if not re.search(r"[0-9]", password):
        return "Пароль должен содержать хотя бы одну цифру."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Пароль должен содержать хотя бы один специальный символ."
    return "Пароль надёжен!"

# Функция для выбора случайного прокси
def get_random_proxy():
    return {"http": random.choice(PROXY_LIST), "https": random.choice(PROXY_LIST)}

# Функция для проверки доступности прокси
def check_proxy(proxy):
    try:
        response = requests.get("http://www.google.com", proxies=proxy, timeout=5)
        return response.status_code == 200
    except:
        return False

# Функция для проверки открытых портов
def check_open_ports():
    common_ports = [21, 22, 23, 80, 443, 3389]  # FTP, SSH, Telnet, HTTP, HTTPS, RDP
    open_ports = []
    
    def scan_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                open_ports.append(port)
        except:
            pass
        sock.close()

    threads = []
    for port in common_ports:
        thread = threading.Thread(target=scan_port, args=(port,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return open_ports

# Функция для поиска информации в поисковых системах через прокси
def search_personal_info(name, email, phone, username):
    queries = [
        f'"{name}"',
        f'"{email}"',
        f'"{phone}"' if phone else None,
        f'"{username}"' if username else None
    ]
    search_engines = {
        "Google": "https://www.google.com/search?q={}",
        "Bing": "https://www.bing.com/search?q={}"
    }
    search_results = []
    proxy = get_random_proxy()
    if not check_proxy(proxy):
        print("Прокси не работает, выполняем поиск без прокси.")
        proxy = None

    for engine, base_url in search_engines.items():
        for query in queries:
            if query:
                url = base_url.format(urllib.parse.quote(query))
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    response = requests.get(url, proxies=proxy, headers=headers, timeout=10) if proxy else requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        titles = [h.text for h in soup.find_all(['h1', 'h2', 'h3'])[:3]]
                        search_results.append(f"{engine} поиск для {query}: {url}\nРезультаты: {', '.join(titles) if titles else 'Нет заголовков'}")
                        webbrowser.open(url)
                    else:
                        search_results.append(f"{engine} поиск для {query} не удался (ошибка {response.status_code}).")
                except Exception as e:
                    search_results.append(f"{engine} поиск для {query} не удался: {str(e)}")
    return search_results

# Функция для проверки профилей в соцсетях
def check_social_media(username):
    social_media = {
        "ВКонтакте": "https://vk.com/{}",
        "Twitter": "https://x.com/{}",
        "Instagram": "https://www.instagram.com/{}",
        "Facebook": "https://www.facebook.com/{}",
        "LinkedIn": "https://www.linkedin.com/in/{}",
        "Reddit": "https://www.reddit.com/user/{}",
        "GitHub": "https://github.com/{}"
    }
    social_results = []
    proxy = get_random_proxy()
    if not check_proxy(proxy):
        print("Прокси не работает для соцсетей, проверяем без прокси.")
        proxy = None

    for platform, base_url in social_media.items():
        url = base_url.format(urllib.parse.quote(username))
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, proxies=proxy, headers=headers, timeout=10) if proxy else requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title').text if soup.find('title') else 'Нет заголовка'
                social_results.append(f"{platform} профиль: {url}\nЗаголовок: {title}")
                webbrowser.open(url)
            else:
                social_results.append(f"{platform} профиль не доступен (ошибка {response.status_code}).")
        except Exception as e:
            social_results.append(f"{platform} профиль не доступен: {str(e)}")
    return social_results

# Функция для проверки Telegram
def check_telegram(username):
    telegram_results = []
    url = f"https://t.me/{urllib.parse.quote(username)}"
    proxy = get_random_proxy()
    if not check_proxy(proxy):
        print("Прокси не работает для Telegram, проверяем без прокси.")
        proxy = None

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, proxies=proxy, headers=headers, timeout=10) if proxy else requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title').text if soup.find('title') else 'Нет заголовка'
            telegram_results.append(f"Telegram профиль: {url}\nЗаголовок: {title}")
            webbrowser.open(url)
        else:
            telegram_results.append(f"Telegram профиль не доступен (ошибка {response.status_code}).")
    except Exception as e:
        telegram_results.append(f"Telegram профиль не доступен: {str(e)}")
    return telegram_results

# Функция для проверки на сайтах с данными
def check_people_finder(name, email):
    people_finders = {
        "Spokeo": "https://www.spokeo.com/{}",
        "Whitepages": "https://www.whitepages.com/name/{}",
        "Pipl": "https://pipl.com/search/?q={}"
    }
    finder_results = []
    proxy = get_random_proxy()
    if not check_proxy(proxy):
        print("Прокси не работает для сайтов с данными, проверяем без прокси.")
        proxy = None

    for site, base_url in people_finders.items():
        query = name if "Pipl" not in site else email
        url = base_url.format(urllib.parse.quote(query.replace(" ", "-")))
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, proxies=proxy, headers=headers, timeout=10) if proxy else requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title').text if soup.find('title') else 'Нет заголовка'
                finder_results.append(f"{site} поиск: {url}\nЗаголовок: {title}")
                webbrowser.open(url)
            else:
                finder_results.append(f"{site} поиск не удался (ошибка {response.status_code}).")
        except Exception as e:
            finder_results.append(f"{site} поиск не удался: {str(e)}")
    return finder_results

# Функция для проверки WHOIS
def check_whois(email):
    whois_results = []
    domain = email.split('@')[1]
    try:
        w = whois.whois(domain)
        whois_results.append(f"WHOIS для домена {domain}:\n{w}")
    except Exception as e:
        whois_results.append(f"WHOIS для домена {domain} не удался: {str(e)}")
    return whois_results

# Функция для отправки уведомления на email
def send_alert_email(user_email, subject, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "YOUR_EMAIL@gmail.com"  # Замените на ваш email
    sender_password = getpass.getpass("Введите пароль от вашего email: ")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()
        print("Уведомление отправлено на ваш email!")
    except Exception as e:
        print(f"Ошибка при отправке email: {str(e)}")

# Функция для сохранения отчёта в файл
def save_report(report, format_type="txt"):
    filename = f"privacy_report_{format_type}.{format_type}"
    try:
        if format_type == "json":
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({"report": report.split("\n")}, f, ensure_ascii=False, indent=4)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
        print(f"Отчёт сохранён в файл: {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении отчёта: {str(e)}")

# Функция для отображения меню
def display_menu():
    print("\n=== Anubis Privacy Tool ===")
    print("1. Проверка силы пароля")
    print("2. Проверка открытых портов")
    print("3. Поиск в поисковых системах")
    print("4. Проверка профилей в соцсетях")
    print("5. Проверка профиля в Telegram")
    print("6. Проверка на сайтах с персональными данными")
    print("7. Проверка WHOIS по email")
    print("8. Обновить список прокси")
    print("9. Выполнить все проверки и отправить/сохранить отчёт")
    print("10. Выход")
    return input("Выберите опцию (1-10): ")

# Основная функция
def main():
    print("=== Anubis Privacy Tool: Анализ цифрового следа и защита ===")
    name = input("Введите полное имя: ")
    email = input("Введите email: ")
    phone = input("Введите номер телефона (или оставьте пустым): ")
    username = input("Введите имя пользователя (никнейм, если есть, или оставьте пустым): ")

    while True:
        choice = display_menu()

        if choice == "1":
            password = getpass.getpass("Введите пароль для проверки (не сохраняется): ")
            print("\nПроверка силы пароля:")
            password_result = check_password_strength(password)
            print(password_result)

        elif choice == "2":
            print("\nПроверка открытых портов на вашем устройстве...")
            open_ports = check_open_ports()
            if open_ports:
                port_result = f"Обнаружены открытые порты: {open_ports}. Рекомендуется закрыть их через файрвол."
            else:
                port_result = "Открытые порты не обнаружены."
            print(port_result)

        elif choice == "3":
            print("\nПоиск информации в поисковых системах через прокси...")
            search_results = search_personal_info(name, email, phone, username)
            print("\n".join(search_results))

        elif choice == "4":
            if username:
                print("\nПроверка профилей в социальных сетях через прокси...")
                social_results = check_social_media(username)
                print("\n".join(social_results))
            else:
                print("Пропущена проверка соцсетей: имя пользователя не указано.")

        elif choice == "5":
            if username:
                print("\nПроверка профиля в Telegram через прокси...")
                telegram_results = check_telegram(username)
                print("\n".join(telegram_results))
            else:
                print("Пропущена проверка Telegram: имя пользователя не указано.")

        elif choice == "6":
            print("\nПроверка на сайтах с персональными данными через прокси...")
            finder_results = check_people_finder(name, email)
            print("\n".join(finder_results))

        elif choice == "7":
            print("\nПроверка WHOIS по домену email...")
            whois_results = check_whois(email)
            print("\n".join(whois_results))

        elif choice == "8":
            print("\nОбновление списка прокси...")
            update_proxy_list()

        elif choice == "9":
            password = getpass.getpass("Введите пароль для проверки (не сохраняется): ")
            print("\nВыполняем все проверки...")

            # Проверка пароля
            password_result = check_password_strength(password)

            # Проверка портов
            open_ports = check_open_ports()
            if open_ports:
                port_result = f"Обнаружены открытые порты: {open_ports}. Рекомендуется закрыть их через файрвол."
            else:
                port_result = "Открытые порты не обнаружены."

            # Поиск в поисковиках
            search_results = search_personal_info(name, email, phone, username)

            # Проверка соцсетей
            social_results = check_social_media(username) if username else ["Пропущена проверка соцсетей: имя пользователя не указано."]

            # Проверка Telegram
            telegram_results = check_telegram(username) if username else ["Пропущена проверка Telegram: имя пользователя не указано."]

            # Проверка сайтов с данными
            finder_results = check_people_finder(name, email)

            # Проверка WHOIS
            whois_results = check_whois(email)

            # Формирование отчёта
            report = (
                f"Результаты проверки (Anubis Privacy Tool):\n\n"
                f"Сила пароля: {password_result}\n\n"
                f"Проверка портов: {port_result}\n\n"
                f"Поисковые системы:\n" + "\n".join(search_results) + "\n\n"
                f"Социальные сети:\n" + "\n".join(social_results) + "\n\n"
                f"Telegram:\n" + "\n".join(telegram_results) + "\n\n"
                f"Сайты с данными:\n" + "\n".join(finder_results) + "\n\n"
                f"WHOIS:\n" + "\n".join(whois_results) + "\n\n"
                f"Рекомендации по защите от доксинга и DDoS:\n"
                f"- Проверьте результаты поиска и запросите удаление данных через формы сайтов (Spokeo → 'Privacy', Whitepages → 'Opt-Out').\n"
                f"- Сделайте профили в соцсетях и Telegram приватными или удалите неиспользуемые.\n"
                f"- Используйте VPN (например, ProtonVPN, Windscribe) для сокрытия IP.\n"
                f"- Проверьте утечки email вручную на haveibeenpwned.com.\n"
                f"- Включите двухфакторную аутентификацию (2FA) везде, где возможно.\n"
                f"- Используйте менеджер паролей (например, Bitwarden) для сложных паролей.\n"
                f"- Настройте файрвол для закрытия открытых портов (iptables или Windows Firewall).\n"
                f"- Используйте CDN (например, Cloudflare Free) для защиты сайта от DDoS.\n"
                f"- Регулярно обновляйте прокси через опцию 8.\n"
                f"- Проверьте WHOIS-домен и убедитесь, что ваши данные не раскрыты."
            )

            # Отправка отчёта на email
            send_alert_email(email, "Полный отчёт Anubis Privacy Tool", report)

            # Сохранение отчёта
            save_format = input("Сохранить отчёт в файл? (txt/json/нет): ").lower()
            if save_format in ["txt", "json"]:
                save_report(report, save_format)
            print("\nПолный отчёт отправлен на ваш email.")

        elif choice == "10":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()
