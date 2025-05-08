import socket
import sqlite3
import requests
import datetime
import os
import logging
import threading
import time

# Setup logging
if os.path.exists('error.log'):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    os.rename('error.log', f'error_{timestamp}.log')

logging.basicConfig(filename='error.log', level=logging.ERROR)

debug = True

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0'}

# Define the number of threads you want to use
NUM_THREADS = 1000

# Function to check internet connectivity by pinging a website
def check_internet():
    while True:
        try:
            requests.get('http://www.google.com', timeout=5)
            return True
        except requests.RequestException:
            logging.error("Internet connection lost. Waiting for connection to be restored...")
            time.sleep(60)  # Wait for 60 seconds before checking again

def create_database_connection():
    try:
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS domains (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, domain TEXT UNIQUE, date TEXT, websitetitle TEXT, protocol TEXT, response_code INTEGER)")
        connection.commit()
        return connection, cursor
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None, None

def scan_ip(ipaddress):
    connection, cursor = create_database_connection()
    if connection and cursor:
        try:
            domain = socket.gethostbyaddr(ipaddress)[0]
        except socket.herror as e:
            logging.error(f"Error resolving domain for IP {ipaddress}: {e}")
            return
        except Exception as e:
            logging.error(f"Unknown error resolving domain for IP {ipaddress}: {e}")
            return

        if domain:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                port_80 = s.connect_ex((domain, 80))
                port_443 = s.connect_ex((domain, 443))
                s.close()
            except Exception as e:
                logging.error(f"Error during port scan for {domain}: {e}")
                return

            try:
                if port_443 == 0:
                    protocol = "https"
                    response = requests.get(f"https://{domain}", headers=headers)
                elif port_80 == 0:
                    protocol = "http"
                    response = requests.get(f"http://{domain}", headers=headers)
                else:
                    return

                start_title = response.text.find('<title>')
                end_title = response.text.find('</title>', start_title)
                if start_title != -1 and end_title != -1:
                    title = response.text[start_title + 7:end_title].strip()
                    response_code = response.status_code
                    cursor.execute(f'INSERT INTO domains (ip, domain, date, websitetitle, protocol, response_code) VALUES (?, ?, ?, ?, ?, ?)',
                                   (ipaddress, domain, datetime.datetime.now(), title, protocol, response_code))
                    connection.commit()
            except requests.RequestException as e:
                logging.error(f"Request error for {domain}: {e}")
            except sqlite3.Error as e:
                logging.error(f"Database error while inserting data for {domain}: {e}")
            except Exception as e:
                logging.error(f"Unknown error for {domain}: {e}")
            finally:
                connection.close()

def main():
    threads = []
    for a in range(1, 255):
        for b in range(255):
            for c in range(255):
                for d in range(1, 255):
                    if d != 127:
                        ipaddress = f"{d}.{c}.{b}.{a}"
                        if debug:
                            print(ipaddress)
                        thread = threading.Thread(target=scan_ip, args=(ipaddress,))
                        threads.append(thread)
                        thread.start()

                        # Limit the number of threads
                        if len(threads) >= NUM_THREADS:
                            for thread in threads:
                                thread.join()
                            threads = []
                            
                            # Check internet connectivity every 5000 IPs
                            if a % 50 == 0:
                                if not check_internet():
                                    continue

    # Wait for any remaining threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
