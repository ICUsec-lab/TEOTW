# TEOTW - The Eye Of The Web 👁️

**TEOTW** (*The Eye Of The Web*) is a lightweight Python-based crawler and reconnaissance tool built for ethical hackers and bug bounty hunters.

It crawls web targets recursively, extracts forms and links, searches for sensitive keywords, and tests basic form submissions — all from one terminal command.

## 🛠️ Features

- 🔗 Recursive link crawler
- 📝 HTML form extractor + auto submit
- 🕵️ Sensitive keyword sniffer (`password`, `username`, `secret`, `pass`)
- 📶 Session-aware with response handling
- 🧠 Depth-limited crawling to prevent loops

## 📦 Requirements

- Python 3.6+
- `requests`
- `beautifulsoup4`

```bash
pip install requests beautifulsoup4
```
## 🚀 Usage
```bash
python teotw.py
```

## 📚 Example Output
```yaml
Crawling URL (depth 1): http://example.com
  Forms Found: 1
    - Action: /login
    - Inputs: username, password
  Keywords Found:
    - password: "Enter your password to continue"
  Links Found: 8
```

### ⚠️ Legal Disclaimer
Use TEOTW only on systems you own or have explicit permission to test. Unauthorized scanning is illegal and unethical.

