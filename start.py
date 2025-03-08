import os
import sys
import json
import asyncio
import subprocess
from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError, SessionPasswordNeededError, PhoneCodeExpiredError

# Конфигурация
accounts_dir = "accounts"

def clear_screen():
    """Очистка экрана терминала"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Печать заголовка программы"""
    print("\n" + "=" * 50)
    print("🔮  UGCLAWS USERBOT - Управление  🔮")
    print("=" * 50 + "\n")

def get_accounts():
    """Получение списка всех аккаунтов"""
    if not os.path.exists(accounts_dir):
        os.makedirs(accounts_dir)
    accounts = []
    for item in os.listdir(accounts_dir):
        if os.path.isdir(os.path.join(accounts_dir, item)):
            accounts.append(item)
    return accounts

async def authenticate_account(phone, api_id, api_hash):
    """Авторизация аккаунта в Telegram"""
    account_name = phone.replace('+', '').strip()
    account_dir = os.path.join(accounts_dir, account_name)

    # Создаем директорию для аккаунта, если её нет
    if not os.path.exists(account_dir):
        os.makedirs(account_dir)

    # Сохраняем конфигурацию аккаунта
    account_config = {
        "phone": phone,
        "api_id": api_id,
        "api_hash": api_hash
    }

    config_path = os.path.join(account_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(account_config, f)

    session_path = os.path.join(account_dir, "session")

    # Создаем клиент Telethon
    client = TelegramClient(
        session_path, 
        int(api_id), 
        api_hash,
        device_model="Samsung Galaxy S21",
        system_version="Android 12",
        app_version="8.4.4",
        lang_code="ru",
        system_lang_code="ru"
    )

    await client.connect()

    # Проверяем, авторизован ли уже клиент
    if await client.is_user_authorized():
        print(f"✅ Аккаунт {phone} уже авторизован!")
        await client.disconnect()
        return True

    # Отправляем запрос на получение кода
    await client.send_code_request(phone)
    print(f"📱 Код отправлен на номер {phone}")

    # Запрашиваем код у пользователя
    for attempt in range(1, 4):
        try:
            code = input(f"Введите код из Telegram (попытка {attempt}/3): ")
            await client.sign_in(phone, code)
            print(f"✅ Аккаунт {phone} успешно авторизован!")
            await client.disconnect()
            return True
        except PhoneCodeInvalidError:
            print(f"❌ Неверный код!")
            if attempt == 3:
                print(f"❌ Все попытки исчерпаны!")
                await client.disconnect()
                return False
        except SessionPasswordNeededError:
            # Если включена двухфакторная аутентификация
            print(f"⚠️ Требуется пароль двухфакторной аутентификации")
            for pw_attempt in range(1, 4):
                try:
                    password = input(f"Введите пароль 2FA (попытка {pw_attempt}/3): ")
                    await client.sign_in(password=password)
                    print(f"✅ Аккаунт {phone} успешно авторизован с 2FA!")
                    await client.disconnect()
                    return True
                except:
                    print(f"❌ Неверный пароль!")
                    if pw_attempt == 3:
                        print(f"❌ Все попытки ввода пароля исчерпаны!")
                        await client.disconnect()
                        return False
        except PhoneCodeExpiredError:
            print(f"❌ Код истёк, запрашиваем новый...")
            await client.send_code_request(phone)

    await client.disconnect()
    return False

async def add_account():
    """Добавление и авторизация нового аккаунта"""
    clear_screen()
    print_header()
    print("📱 АВТОРИЗАЦИЯ НОВОГО АККАУНТА 📱\n")

    # Запрашиваем данные аккаунта
    phone = input("Введите номер телефона (с кодом страны, например +79123456789): ")
    api_id = input("Введите API ID: ")
    api_hash = input("Введите API Hash: ")

    # Авторизуем аккаунт
    success = await authenticate_account(phone, api_id, api_hash)

    if success:
        print("\n✅ Аккаунт успешно добавлен и авторизован!")
    else:
        print("\n❌ Не удалось авторизовать аккаунт!")

    input("\nНажмите Enter, чтобы вернуться в главное меню...")

async def start_single_bot():
    """Запуск бота для одного аккаунта"""
    print("\n🚀 Запускаем бота...")
    
    accounts = get_accounts()
    if not accounts:
        print("❌ Нет доступных аккаунтов!")
        input("\nНажмите Enter, чтобы вернуться в главное меню...")
        return
        
    print("\nВыберите аккаунт:")
    for i, account in enumerate(accounts, 1):
        print(f"{i}. {account}")
    
    account_choice = input(f"\nВыберите аккаунт (1-{len(accounts)}): ")
    try:
        account_index = int(account_choice) - 1
        if 0 <= account_index < len(accounts):
            account_name = accounts[account_index]
            print(f"\n🚀 Запускаем бота для аккаунта {account_name}...")
            # Запускаем бота в том же процессе
            try:
                process = subprocess.run([sys.executable, "bot.py", f"--account={account_name}"], check=True)
                print(f"✅ Бот запущен для аккаунта {account_name}!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка при запуске бота: {e}")
            except FileNotFoundError:
                print("❌ Файл bot.py не найден!")
        else:
            print("❌ Неверный выбор аккаунта!")
    except ValueError:
        print("❌ Пожалуйста, введите число!")
    
    input("\nНажмите Enter, чтобы вернуться в главное меню...")

async def start_all_bots():
    """Запуск ботов для всех аккаунтов"""
    print("\n🚀 Запускаем ботов для ВСЕХ аккаунтов...")
    
    accounts = get_accounts()
    if not accounts:
        print("❌ Нет доступных аккаунтов!")
        input("\nНажмите Enter, чтобы вернуться в главное меню...")
        return
    
    # Запускаем ботов для всех аккаунтов
    processes = []
    for account_name in accounts:
        print(f"\n🚀 Запускаем бота для аккаунта {account_name}...")
        try:
            # Используем nohup для запуска в фоновом режиме
            cmd = f"nohup python bot.py --account={account_name} > /dev/null 2>&1 &"
            process = subprocess.Popen(cmd, shell=True)
            processes.append((account_name, process))
            print(f"✅ Бот для аккаунта {account_name} запущен в фоновом режиме!")
        except Exception as e:
            print(f"❌ Ошибка при запуске бота для {account_name}: {e}")
    
    print("\n✅ Все боты запущены в фоновом режиме!")
    input("\nНажмите Enter, чтобы вернуться в главное меню...")

async def start_permanent_bots():
    """Запуск ботов для всех аккаунтов в постоянном режиме"""
    print("\n🚀 Запускаем ботов для ВСЕХ аккаунтов в постоянном режиме...")
    
    accounts = get_accounts()
    if not accounts:
        print("❌ Нет доступных аккаунтов!")
        input("\nНажмите Enter, чтобы вернуться в главное меню...")
        return
    
    # Создаём скрипт автозапуска
    startup_script = "#!/bin/bash\n\n"
    
    for account_name in accounts:
        startup_script += f"nohup python bot.py --account={account_name} > /dev/null 2>&1 &\n"
    
    # Сохраняем скрипт
    with open("start_bots.sh", "w") as f:
        f.write(startup_script)
    
    # Делаем скрипт исполняемым
    os.chmod("start_bots.sh", 0o755)
    
    # Запускаем ботов
    for account_name in accounts:
        print(f"\n🚀 Запускаем бота для аккаунта {account_name}...")
        try:
            # Используем disown для отвязки процесса от терминала
            cmd = f"nohup python bot.py --account={account_name} > /dev/null 2>&1 & disown"
            subprocess.run(cmd, shell=True)
            print(f"✅ Бот для аккаунта {account_name} запущен в постоянном режиме!")
        except Exception as e:
            print(f"❌ Ошибка при запуске бота для {account_name}: {e}")
    
    print("\n✅ Все боты запущены в постоянном режиме!")
    print("\n⚠️ Важно: Теперь вы можете закрыть это окно, и боты продолжат работать")
    print("📝 Для перезапуска ботов используйте созданный скрипт start_bots.sh")
    input("\nНажмите Enter, чтобы вернуться в главное меню...")

async def main_menu():
    """Главное меню программы"""
    while True:
        clear_screen()
        print_header()

        # Получаем список аккаунтов
        accounts = get_accounts()

        # Выводим информацию об аккаунтах
        if accounts:
            print(f"📱 АККАУНТЫ: {len(accounts)}\n")
            for i, account in enumerate(accounts, 1):
                print(f"{i}. {account}")
        else:
            print("⚠️ Нет доступных аккаунтов. Добавьте новый аккаунт.")

        print("\n🔍 МЕНЮ:\n")
        print("1. Авторизировать аккаунт (API ID, API Hash, номер, код, 2FA)")
        print("2. Запустить бота для одного аккаунта")
        print("3. Запустить ботов для ВСЕХ аккаунтов")
        print("4. Запустить ботов для ВСЕХ аккаунтов в постоянном режиме")
        print("5. ОСТАНОВИТЬ ТОЛЬКО ТЕКУЩИЙ ПРОЦЕСС")
        print("6. Выход")

        choice = input("\nВыберите действие (1-6): ")

        if choice == "1":
            await add_account()
        elif choice == "2":
            if not accounts:
                print("\n❌ Нет доступных аккаунтов! Сначала добавьте аккаунт.")
                input("\nНажмите Enter, чтобы вернуться в главное меню...")
                continue
            await start_single_bot()
        elif choice == "3":
            if not accounts:
                print("\n❌ Нет доступных аккаунтов! Сначала добавьте аккаунт.")
                input("\nНажмите Enter, чтобы вернуться в главное меню...")
                continue
            await start_all_bots()
        elif choice == "4":
            if not accounts:
                print("\n❌ Нет доступных аккаунтов! Сначала добавьте аккаунт.")
                input("\nНажмите Enter, чтобы вернуться в главное меню...")
                continue
            await start_permanent_bots()
        elif choice == "5":
            # Останавливаем ТОЛЬКО ТЕКУЩИЙ бот/процесс
            try:
                clear_screen()
                print("\n⚠️ ОСТАНОВКА ТЕКУЩЕГО ПРОЦЕССА ⚠️")
                print("Завершение текущего процесса Python...")
                
                # Просто выходим из программы со статусом 0 (нормальное завершение)
                print("✅ Текущий процесс будет остановлен!")
                print("\n👋 Спасибо за использование UGCLAWS USERBOT!")
                sys.exit(0)  # Корректное завершение текущего процесса
            except Exception as e:
                print(f"❌ Ошибка при остановке текущего процесса: {e}")
                input("\nНажмите Enter, чтобы вернуться в главное меню...")
        elif choice == "6":
            clear_screen()
            print("\n👋 Спасибо за использование UGCLAWS USERBOT!")
            break
        else:
            print("\n❌ Неверный выбор! Пожалуйста, выберите 1-6.")
            input("\nНажмите Enter, чтобы продолжить...")

if __name__ == "__main__":
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        clear_screen()
        print("\n👋 Программа остановлена пользователем.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        input("\nНажмите Enter, чтобы выйти...")