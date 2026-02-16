import argparse
import csv
import re
from collections import defaultdict
from urllib.request import urlopen
from io import StringIO
import sys


def download_data(url):
    """Download the CSV data from given URL"""
    try:
        response = urlopen(url)
        data = response.read().decode('utf-8')
        return StringIO(data)
    except Exception as e:
        print(f"Error downloading data: {e}")
        sys.exit(1)


def process_file(file_handle):
    """Process the CSV file and return structured data"""
    data = []
    csv_reader = csv.reader(file_handle)

    for row in csv_reader:
        if len(row) == 5:  # Ensure we have all 5 fields
            data.append({
                'path': row[0].strip(),
                'datetime': row[1].strip(),
                'browser': row[2].strip(),
                'status': row[3].strip(),
                'size': int(row[4].strip())
            })

    return data


def is_image_file(path):
    """Check if the path represents an image file using regex"""
    # Pattern for common image extensions
    image_pattern = r'\.(jpg|jpeg|png|gif|bmp|svg)$'
    return bool(re.search(image_pattern, path.lower()))


def get_browser_name(user_agent):
    """Extract the browser name from the user agent string"""
    browser_patterns = {
        'Firefox': r'Firefox/\d+',
        'Chrome': r'Chrome/\d+',
        'Safari': r'Safari/\d+',
        'Internet Explorer': r'MSIE \d+|Trident/\d+',
        'Edge': r'Edge/\d+'
    }

    for browser, pattern in browser_patterns.items():
        if re.search(pattern, user_agent):
            return browser

    return 'Unknown'


def analyze_images(data):
    """Analyze image hits and return statistics"""
    image_hits = [hit for hit in data if is_image_file(hit['path'])]
    total_images = len(image_hits)
    total_size = sum(hit['size'] for hit in image_hits)

    return {
        'total_images': total_images,
        'total_size': total_size,
        'average_size': total_size / total_images if total_images > 0 else 0
    }


def find_popular_browser(data):
    """Find the most popular browser among all hits"""
    browser_counts = defaultdict(int)

    for hit in data:
        browser_name = get_browser_name(hit['browser'])
        browser_counts[browser_name] += 1

    # Find the browser with maximum count
    if browser_counts:
        popular_browser = max(browser_counts.items(), key=lambda x: x[1])
        return popular_browser
    return None, 0


def main(url):
    """Main function to process the web log"""
    print(f"Downloading data from {url}...")

    # Download the data
    file_handle = download_data(url)

    print("Processing file...")
    # Process the file
    data = process_file(file_handle)

    if not data:
        print("No data found in the file.")
        return

    print(f"Total hits processed: {len(data)}")
    print("\n" + "=" * 50)

    # Analyze images
    print("\nIMAGE STATISTICS:")
    image_stats = analyze_images(data)
    print(f"Total image hits: {image_stats['total_images']}")
    print(f"Total image bytes transferred: {image_stats['total_size']:,} bytes")
    print(f"Average image size: {image_stats['average_size']:.2f} bytes")

    print("\n" + "=" * 50)

    # Find most popular browser
    print("\nBROWSER STATISTICS:")
    popular_browser, count = find_popular_browser(data)
    if popular_browser:
        total_hits = len(data)
        percentage = (count / total_hits) * 100
        print(f"Most popular browser: {popular_browser}")
        print(f"Number of hits: {count}")
        print(f"Percentage of total: {percentage:.1f}%")
    else:
        print("Could not determine browser statistics")


if __name__ == "__main__":
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Process web server log file')
    parser.add_argument("--url", help="URL to the datafile", type=str,
                        default="http://s3.amazonaws.com/cuny-is211-spring2015/weblog.csv",
                        required=False)
    args = parser.parse_args()

    main(args.url)

#documents and information for test
# document location on device for test - /Users/stephanbluitt/Downloads/weblog.csv
# link document URL http://s3.amazonaws.com/cuny-is211-spring2015/weblog.csv
