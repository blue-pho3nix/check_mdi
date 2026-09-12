# check_mdi
Python script to enumerate valid Microsoft 365 domains, retrieve the tenant name, and check for an MDI instance.


Based on: https://github.com/expl0itabl3/check_mdi/

![]("https://github.com/user-attachments/assets/17577d4d-cf7a-4495-ac5d-a34b3f4c3a06")

## Usage
```
git clone https://github.com/blue-pho3nix/check_mdi.git
python check_mdi.py -d <domain>
```
If needed..
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
If you don't get any domains after 10x retries, go for a higher `-r`... sometimes need `40–50` 
```
python check_mdi.py -d <domain> -r 30
```
