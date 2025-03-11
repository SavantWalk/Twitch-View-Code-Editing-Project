import requests
import sys
import time
import random
from random import shuffle
from fake_useragent import UserAgent
import linecache
from threading import Thread
from streamlink import Streamlink  # Reemplazo de Livestreamer

channel_url = "https://www.twitch.tv/TwitchName"
proxies_file = "Proxies_txt/good_proxy.txt"
max_nb_of_threads = 1000

all_proxies = []

# Crear sesión para Streamlink
ua = UserAgent()
session = Streamlink()
session.set_option("http-headers", {'User-Agent': ua.random, "Client-ID": "jzkbprff40iqj646a697cyrvl0zt2m6"})

def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def get_proxies():
    try:
        lines = [line.rstrip("\n") for line in open(proxies_file)]
    except IOError as e:
        print("Error al leer la lista de proxies: %s" % e.strerror)
        sys.exit(1)
    return lines

def get_url():
    try:
        streams = session.streams(channel_url)
        if 'audio_only' in streams:
            return streams['audio_only'].url
        elif 'worst' in streams:
            return streams['worst'].url
    except Exception as e:
        print("No se pudo obtener la URL: ", e)
    return ""

def open_url(proxy_data):
    try:
        global all_proxies
        headers = {'User-Agent': ua.random}
        current_index = all_proxies.index(proxy_data)

        if not proxy_data['url']:
            proxy_data['url'] = get_url()

        current_url = proxy_data['url']
        try:
            if time.time() - proxy_data['time'] >= random.randint(1, 5):
                current_proxy = {"http": proxy_data['proxy'], "https": proxy_data['proxy']}
                with requests.Session() as s:
                    response = s.head(current_url, proxies=current_proxy, headers=headers)
                print(f"HEAD request enviado con {current_proxy['http']} | {response.status_code} | {response.request} | {response}")
                proxy_data['time'] = time.time()
                all_proxies[current_index] = proxy_data
        except:
            print("************* Error de conexión! *************")
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

if __name__ == "__main__":
    input("Presiona Enter para iniciar el proceso...")

    proxies = get_proxies()
    for p in proxies:
        all_proxies.append({'proxy': p, 'time': time.time(), 'url': ""})

    shuffle(all_proxies)

    while True:
        try:
            for i in range(min(max_nb_of_threads, len(all_proxies))):
                threaded = Thread(target=open_url, args=(all_proxies[random.randint(0, len(all_proxies) - 1)],))
                threaded.daemon = True
                threaded.start()
        except:
            print_exception()
        shuffle(all_proxies)
        time.sleep(5)
