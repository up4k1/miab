import requests
from requests.auth import HTTPBasicAuth
import random
import string
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from dkimgen import generate_dkim_key
from usernamegen import generate_friendly_username


def load_config(filename):
    config = {}
    with open(filename, 'r') as file:
        for line in file:
            name, value = line.strip().split('=')
            config[name] = value
    return config

def load_redirect_urls(filename):
    urls = []
    with open(filename, 'r') as file:
        for line in file:
            urls.append(line.strip())
    return urls

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))




# Загрузка конфигурации из файла
config = load_config('config.txt')

email = config['email']
password = config['password']
base_url = config['base_url']
base_url_dns = f"{base_url}/admin/dns/custom"
base_url_alias = f"{base_url}/admin/mail/aliases"
base_url_user = f"{base_url}/admin/mail/users"
ip = config['ip']
forward_to = config['forward_to']
domain_count = int(config['domain_count'])
main_domain = base_url.split('//')[1].split('.')[1] + '.' + base_url.split('//')[1].split('.')[2]

# Загрузка ссылок для редиректа из файла
redirect_urls = load_redirect_urls('redirect_urls.txt')

# Открытие файла для записи результата
output_file = open('output.txt', 'w')

for _ in range(domain_count):
    # Создание субдомена
    subdomain_prefix = generate_random_string()
    subdomain = f"{subdomain_prefix}.{main_domain}"
    url_dns = f"{base_url_dns}/{subdomain}/a"
    response_dns = requests.put(url_dns, auth=HTTPBasicAuth(email, password), data=ip)
    
    if response_dns.status_code == 200:
        print(f"Successfully created subdomain {subdomain}")
        
        # Создание почтового пользователя для субдомена
        friendly_username = generate_friendly_username()
        user_email = f"{friendly_username}@{subdomain}"
        user_password = generate_random_string(12)  # Генерация случайного пароля
        data_user = {
            "email": user_email,
            "password": user_password
        }
        response_user = requests.post(f"{base_url_user}/add", auth=HTTPBasicAuth(email, password), data=data_user)
        
        if response_user.status_code == 200:
            print(f"Successfully created email user {user_email} with password {user_password}")
            
            # Создание почтового алиаса для субдомена
            data_alias = {
                "address": user_email,
                "forwards_to": forward_to,
                "permitted_senders": user_email
            }
            response_alias = requests.post(f"{base_url_alias}/add", auth=HTTPBasicAuth(email, password), data=data_alias)
            
            if response_alias.status_code == 200:
                print(f"Successfully created email alias {user_email}")
                
                # Генерация DKIM ключей
                private_key, public_key = generate_dkim_key()
                
                # Кодирование открытого ключа в формат, подходящий для записи DNS
                dkim_selector = "default"
                dkim_record = public_key.replace("-----BEGIN PUBLIC KEY-----\n", "").replace("-----END PUBLIC KEY-----\n", "").replace("\n", "")
                
                # Добавление записи DNS для DKIM
                dkim_name = f"{dkim_selector}._domainkey.{subdomain}"
                dkim_value = f"v=DKIM1; k=rsa; p={dkim_record}"
                
                data_dkim = {
                    "qname": dkim_name,
                    "rtype": "TXT",
                    "value": dkim_value
                }
                response_dkim = requests.post(f"{base_url_dns}/{dkim_name}/txt", auth=HTTPBasicAuth(email, password), data=data_dkim)
                
                if response_dkim.status_code == 200:
                    print(f"Successfully created DKIM record for {subdomain}")
                    
                    # Выбор случайной ссылки для редиректа
                    redirect_url = random.choice(redirect_urls)
                    
                    # Запись данных в выходной файл
                    output_file.write(f"{subdomain}|465|15|3|0|false|1|1|1|0|{user_email}:::{user_email}|{user_password}|0|1|1|30|8||||{redirect_url}|CustomBody:|\n")
                else:
                    print(f"Failed to create DKIM record for {subdomain}: {response_dkim.text}")
            else:
                print(f"Failed to create email alias {user_email}: {response_alias.text}")
        else:
            print(f"Failed to create email user {user_email}: {response_user.text}")
    else:
        print(f"Failed to create subdomain {subdomain}: {response_dns.text}")

# Закрытие файла после записи всех данных
output_file.close()
