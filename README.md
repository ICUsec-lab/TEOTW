# TEOTW - The Eye Of The Web

TEOTW is a Python-based web crawler and scanner designed to help security researchers and pentesters perform reconnaissance on web applications. It fetches pages, extracts links and forms, searches for sensitive keywords, and optionally submits forms with test data.

## Features

- Recursive crawling up to a configurable depth
- Extraction of hyperlinks within the same domain
- Identification and submission of HTML forms with dummy data
- Detection of sensitive keywords such as passwords, secrets, and usernames
- Supports scanning a single URL or a list of URLs from a file
- Session handling and request headers customization
- Pretty ASCII banners at startup

## Requirements

- Python 3.x
- `requests` library
- `beautifulsoup4` library

Install dependencies with:

```bash
pip install requests beautifulsoup4
```

## Usage
Run the tool with one of the following options:

Scan a single URL:

```bash
python teotw.py -u http://example.com
```
Scan multiple URLs from a file:
```bash
python teotw.py -l targets.txt
```
The targets.txt file should contain one URL per line.


## Notes
By default, the crawler limits recursion depth to 2.

URLs without http:// or https:// will have http:// prepended automatically.

The tool submits forms with a dummy value "admin" for all input fields.

Use responsibly and only against sites you have permission to test.



