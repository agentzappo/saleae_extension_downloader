import json
import os
import re
import urllib.request


def process_json(url):
    with urllib.request.urlopen(url) as response:
        json_data = json.load(response)

    download_folder = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(download_folder):
        os.mkdir(download_folder)

    num_releases = len(json_data)
    for i, release_data in enumerate(json_data):
        release_name = release_data['currentRelease']['name']

        # Replace invalid characters in release name
        release_name = re.sub(r'[<>:"/\\|?*]', '_', release_name)
        # Remove trailing whitespace from release name
        release_name = release_name.strip()

        release_folder = os.path.join(download_folder, release_name)

        if not os.path.exists(release_folder):
            os.mkdir(release_folder)

        print(f"[{i + 1}/{num_releases}] Processing release {release_name}...")

        metadata_path = os.path.join(release_folder, 'metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as metadata_file:
                existing_release_data = json.load(metadata_file)
            if existing_release_data['id'] == release_data['id']:
                print(f"  - Release {release_name} already downloaded and up to date.")
                continue

        with open(metadata_path, 'w') as metadata_file:
            json.dump(release_data, metadata_file, indent=4)

        readme_url = release_data['currentRelease']['readmeUrl']
        download_url = release_data['currentRelease']['downloadUrl']

        print(f"  - Downloading {readme_url}...")
        with urllib.request.urlopen(readme_url) as readme_response:
            with open(os.path.join(release_folder, 'README.md'), 'wb') as readme_file:
                readme_file.write(readme_response.read())

        print(f"  - Downloading {download_url}...")
        with urllib.request.urlopen(download_url) as download_response:
            total_size = int(download_response.headers.get('content-length', 0))
            block_size = 8192
            bytes_read = 0
            with open(os.path.join(release_folder, 'release.zip'), 'wb') as download_file:
                while True:
                    buffer = download_response.read(block_size)
                    if not buffer:
                        break
                    download_file.write(buffer)
                    bytes_read += len(buffer)
                    if total_size > 0:
                        percent_complete = bytes_read * 100 / total_size
                        print(f"    - Downloaded {bytes_read}/{total_size} bytes ({percent_complete:.2f}%)...",
                              end="\r")
                print("")  # Print newline after progress bar finishes downloading

    print("All releases processed.")


def main():
    url = "https://logic2api.saleae.com/marketplace/v1/list"
    print(f"Fetching JSON data from {url}...")
    process_json(url)
    print("All done!")


if __name__ == "__main__":
    main()