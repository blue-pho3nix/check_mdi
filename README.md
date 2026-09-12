# check_mdi
Python script to enumerate valid Microsoft 365 domains, retrieve tenant name, and check for an MDI instance.


Based on: https://github.com/expl0itabl3/check_mdi/

## Usage
```
git clone https://github.com/blue-pho3nix/check_mdi.git
chmod +x check_mdi.py
./check_mdi.py -d <domain>
```
If needed..
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
If you don't get any domains on 10x retries go for 
```
python check_mdi.py -d <domain> -r 25
```
