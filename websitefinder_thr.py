import json
import requests
from bs4 import BeautifulSoup
import threading
import os

def get_website_info(domain):
    protocols = ['https', 'http']

    for protocol in protocols:
        try:
            # Send a request to the website with the current protocol
            response = requests.get(f"{protocol}://{domain}", timeout=5)

            # Extract the title from the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No Title Found"

            # Return the title, response code, and protocol
            return title, response.status_code, protocol
        except requests.RequestException as e:
            # Log and handle errors
            print(f"Error processing {protocol}://{domain}: {e}")

    # Return None if both protocols fail
    return None

def process_domains(thread_num, domains, results_folder):
    results = []

    for i, domain in enumerate(domains, start=1):
        # Get website info
        result = get_website_info(domain)

        if result:
            title, response_code, protocol = result

            # Store the result in real-time
            result_data = {'domain': domain, 'title': title, 'response_code': response_code, 'protocol': protocol}
            results.append(result_data)

            with open(os.path.join(results_folder, f"result_{thread_num}.json"), 'a') as json_file:
                json.dump(result_data, json_file, indent=2)
                json_file.write('\n')

        # Calculate progress and print to console
        progress = i / len(domains) * 100
        print(f"Thread {thread_num} - Progress: {progress:.2f}%")

    # Save results to a text file for each thread
    with open(os.path.join(results_folder, f"result_{thread_num}.txt"), 'w') as txt_file:
        for result in results:
            txt_file.write(f"{result['domain']} - {result['title']} - {result['response_code']} - {result['protocol']}\n")

def main():
    # Read domains from file
    with open('onlydomains.txt', 'r') as file:
        domains = [line.strip() for line in file]

    # Create a folder to store results
    results_folder = 'result'
    os.makedirs(results_folder, exist_ok=True)

    # Split domains into 20 roughly equal parts for 20 threads
    chunk_size = len(domains) // 20
    domain_chunks = [domains[i:i + chunk_size] for i in range(0, len(domains), chunk_size)]

    # Create and start 20 threads
    threads = []
    for i in range(20):
        thread = threading.Thread(target=process_domains, args=(i + 1, domain_chunks[i], results_folder))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("All threads done")

if __name__ == "__main__":
    main()
