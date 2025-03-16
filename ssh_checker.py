import paramiko
import socket
import re

# تابع برای تست اتصال SSH
def check_ssh(host, port, username, password, failed_file):
    try:
        # ایجاد یک SSHClient
        client = paramiko.SSHClient()
        
        # قبول کلیدهای ناشناخته (از سرورهای جدید)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # اتصال به سرور
        client.connect(host, username=username, password=password, timeout=10, port=port)
        
        # اگر اتصال موفقیت‌آمیز بود، پیام موفقیت را ثبت می‌کنیم
        message = f"SSH success for {host} on port {port} with {username} / {password}\n"
        failed_file.write(message)
        failed_file.flush()  # ذخیره بلافاصله پیام
        return message
    except paramiko.AuthenticationException:
        # اگر نام کاربری یا رمز عبور اشتباه باشد
        message = f"Authentication failed for {host} on port {port} with {username} / {password}\n"
        failed_file.write(message)
        failed_file.flush()
        return message
    except paramiko.SSHException as e:
        # اگر خطای عمومی SSH باشد
        message = f"SSH error for {host} on port {port}: {e}\n"
        failed_file.write(message)
        failed_file.flush()
        return message
    except Exception as e:
        # اگر هر خطای دیگری پیش آید
        message = f"Error connecting to {host} on port {port}: {e}\n"
        failed_file.write(message)
        failed_file.flush()
        return message
    finally:
        # بستن اتصال
        client.close()

# تابع برای بررسی پورت باز
def is_port_open(host, port, failed_file):
    try:
        with socket.create_connection((host, port), timeout=5):
            message = f"Port {port} is open on {host}. Trying SSH...\n"
            failed_file.write(message)
            failed_file.flush()
            return True
    except (socket.timeout, socket.error):
        message = f"Port {port} is closed on {host}\n"
        failed_file.write(message)
        failed_file.flush()
        return False

# فایل hit.txt رو باز می‌کنیم
with open('hit.txt', 'r') as file, open('failed.txt', 'a') as failed_file:
    
    # خواندن هر خط از فایل
    for line in file.readlines():
        # جداسازی آی‌پی، یوزرنیم و پسورد
        parts = line.split(' | ')
        if len(parts) == 2:
            url, creds = parts

            # حذف کردن / آخرین کاراکتر
            url = url.rstrip('/')

            match = re.match(r"(https?://)?([^:/]+)(?::(\d+))?", url)

            if match:
                host = match.group(2)  # هاست
                port = match.group(3) if match.group(3) else 22  # پورت (اگر موجود نبود پورت 22 پیش‌فرض است)
            else:
                message = f"Invalid URL format: {url}\n"
                failed_file.write(message)
                failed_file.flush()
                continue

            creds = creds.split('&')
            password = creds[0].split('=')[1].strip()
            username = creds[1].split('=')[1].strip()

            # چک کردن باز بودن پورت
            if is_port_open(host, int(port), failed_file):
                # چک کردن SSH
                result = check_ssh(host=host, port=int(port), username=username, password=password, failed_file=failed_file)

# پیام نهایی
print("end process. All errors saved in 'failed.txt'")