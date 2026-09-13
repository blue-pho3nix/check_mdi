# check_mdi
Python script to enumerate valid Microsoft 365 domains, retrieve the tenant name, and check for an MDI instance.


Based on: https://github.com/expl0itabl3/check_mdi/


<img width="800" height="1200" alt="check_mdi" src="https://github.com/user-attachments/assets/39cc66f0-6306-4b07-914b-1b90c47e5e53" />


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
If you don't get any domains after the default 10x retries, go for a higher retry... `-r` 
```
python check_mdi.py -d <domain> -r 30
```
