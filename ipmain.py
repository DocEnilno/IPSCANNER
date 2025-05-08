import socket
import sqlite3
import requests
import datetime
import os

# Setup logging
import logging

# Rename old error log file
if os.path.exists('error.log'):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    os.rename('error.log', f'error_{timestamp}.log')

logging.basicConfig(filename='error.log', level=logging.ERROR)

# Connect to the database
try:
    database = sqlite3.connect("database.db")
    cursor = database.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS domains (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, domain TEXT UNIQUE, date TEXT, websitetitle TEXT, protocol TEXT, response_code INTEGER)")
    database.commit()
except sqlite3.Error as e:
    logging.error(f"Database error: {e}")

debug=True

headers= {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0'}
#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}

for a in range(1,255):
    for b in range(255):
        for c in range(255):
            for d in range(d_start, 255):
                if d != 127:
                    ipaddress=f"{d}.{c}.{b}.{a}"
                    if debug:
                        print(ipaddress)
                    try:
                        domain=socket.gethostbyaddr(ipaddress)[0]
                    except socket.herror as e:
                        logging.error(f"Error resolving domain for IP {ipaddress}: {e}")
                        continue
                    except Exception as e:
                        logging.error(f"Unknown error resolving domain for IP {ipaddress}: {e}")
                        continue

                    if domain:
                        try:
                            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.settimeout(2)
                            port_80 = s.connect_ex((domain, 80))
                            port_443= s.connect_ex((domain, 443))
                            if debug:
                                print("Portscan: ")
                                print(port_80)
                                print(port_443)
                            s.close()
                        except Exception as e:
                            logging.error(f"Error during port scan for {domain}: {e}")
                            continue

                        try:
                            if port_443==0:
                                response = requests.get(f"https://{domain}", headers=headers)
                                start_title = response.text.find('<title>')
                                end_title = response.text.find('</title>', start_title)
                                if debug:
                                    print(start_title)
                                    print(end_title)
                                if start_title != -1 and end_title != -1:
                                    title = response.text[start_title + 7:end_title].strip()
                                    protocol="https"
                                    response_code=response.status_code
                                    if debug:
                                        print(title)
                                        print(protocol)
                                        print(response_code)
                                cursor.execute(f'INSERT INTO domains (ip, domain, date, websitetitle, protocol, response_code) VALUES ("{ipaddress}", "{domain}", "{datetime.datetime.now()}", "{title}", "{protocol}", "{int(response_code)}")')
                                database.commit()
                            elif port_80==0:
                                response = requests.get(f"http://{domain}", headers=headers)
                                start_title = response.text.find('<title>')
                                end_title = response.text.find('</title>', start_title)
                                if debug:
                                    print(start_title)
                                    print(end_title)
                                if start_title != -1 and end_title != -1:
                                    title = response.text[start_title + 7:end_title].strip()
                                    protocol="http"
                                    response_code=response.status_code
                                    if debug:
                                        print(title)
                                        print(protocol)
                                        print(response_code)
                                cursor.execute(f'INSERT INTO domains (ip, domain, date, websitetitle, protocol, response_code) VALUES ("{ipaddress}", "{domain}", "{datetime.datetime.now()}", "{title}", "{protocol}", {int(response_code)})')
                                database.commit()
                        except requests.RequestException as e:
                            logging.error(f"Request error for {domain}: {e}")
                            continue
                        except sqlite3.Error as e:
                            logging.error(f"Database error while inserting data for {domain}: {e}")
                            continue
                        except Exception as e:
                            logging.error(f"Unknown error for {domain}: {e}")
                            continue
