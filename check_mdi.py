#!/usr/bin/env python3
"""
Enumerate M365 domains, get tenant, check for MDI instance.
based on: https://github.com/expl0itabl3/check_mdi
"""

import argparse
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

import dns.resolver


def _fetch_federation_response(domain):
    """Make a single GetFederationInformation request, return decoded XML or None."""
    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:a="http://www.w3.org/2005/08/addressing"
        xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header>
        <a:RequestedServerVersion>Exchange2010</a:RequestedServerVersion>
        <a:MessageID>urn:uuid:6389558d-9e05-465e-ade9-aae14c4bcd10</a:MessageID>
        <a:Action soap:mustUnderstand="1">http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation</a:Action>
        <a:To soap:mustUnderstand="1">https://autodiscover.byfcxu-dom.extest.microsoft.com/autodiscover/autodiscover.svc</a:To>
        <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
    </soap:Header>
    <soap:Body>
        <GetFederationInformationRequestMessage xmlns="http://schemas.microsoft.com/exchange/2010/Autodiscover">
        <Request><Domain>{domain}</Domain></Request>
        </GetFederationInformationRequestMessage>
    </soap:Body>
    </soap:Envelope>"""

    headers = {
        "Content-type": "text/xml; charset=utf-8",
        "User-agent": "AutodiscoverClient",
        "SOAPAction": '"http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation"',
    }

    try:
        req = Request("https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc",
                      headers=headers, data=body.encode())
        with urlopen(req) as resp:
            return resp.read().decode()
    except (HTTPError, URLError) as e:
        print(f"[-] Request error: {e}")
        return None


def get_domains(args):
    domain = args.domain
    ns = "{http://schemas.microsoft.com/exchange/2010/Autodiscover}Domain"

    max_attempts = args.retries
    best_domains = []

    for attempt in range(1, max_attempts + 1):
        response = _fetch_federation_response(domain)
        if response is None:
            continue

        tree = ET.fromstring(response)
        domains = [e.text for e in tree.iter() if e.tag == ns]

        # Keep the fullest list we've seen so far
        if len(domains) > len(best_domains):
            best_domains = domains

        # Stop as soon as we get a response containing the tenant domain
        if any(d and d.lower().endswith(".onmicrosoft.com") for d in domains):
            print(f"[i] Full response on attempt {attempt} ({len(domains)} domains)")
            best_domains = domains
            break
        else:
            print(f"[i] Attempt {attempt}: partial response ({len(domains)} domains), retrying...")

    if not best_domains:
        print(f"\n[-] No domains returned for {domain} after {max_attempts} attempts.")
        print("[-] Domain may not be a Microsoft 365 tenant.")
        return

    print("\n[+] Domains found:")
    print(*best_domains, sep="\n")

    tenant = next(
        (d.split(".")[0] for d in best_domains
         if d.lower().endswith(".onmicrosoft.com")
         and not d.lower().endswith(".mail.onmicrosoft.com")),
        "",
    )
    if not tenant:
        print("\n[-] No onmicrosoft.com domain found; can't derive tenant.")
        return

    print(f"\n[+] Tenant found:\n{tenant}")
    check_mdi(tenant)


def check_mdi(tenant):
    target = tenant + "sensorapi.atp.azure.com"
    try:
        dns.resolver.resolve(target)
        print(f"\n[+] An MDI instance was found for {target}!\n")
    except Exception:
        print(f"\n[-] No MDI instance was found for {target}\n")

banner = r"""
[0;97;40m█▀[0;37;40m [0;97;40m█[0;37;40m   [0;97;40m█▀█[0;37;40m [0;97;40m█▀[0;37;40m [0;97;40m█[0;37;40m        [0;97;40m█▀█▀█[0;37;40m [0;97;40m  █[0;37;40m [0;97;40m ▀[0;37;40m   [0;97;40m▀█▀█[0;37;40m [0;97;40m█ █[0m
[0;91;40m█[0;37;40m  [0;91;40m█▀█[0;37;40m [0;91;40m█▀▀[0;37;40m [0;91;40m█[0;37;40m  [0;91;40m█▄▀[0;37;40m      [0;91;40m█ ▀ █[0;37;40m [0;91;40m█▀█[0;37;40m [0;97;40m [0;91;40m█[0;37;40m [0;97;40m▄[0;37;40m [0;97;40m [0;91;40m█▀▀[0;37;40m [0;91;40m▀▀█[0m
[0;91;40m▀▀[0;37;40m [0;91;40m▀[0;97;40m [0;91;40m▀[0;37;40m [0;91;40m▀▀▀[0;37;40m [0;91;40m▀▀[0;37;40m [0;91;40m▀[0;97;40m [0;91;40m▀[0;37;40m [0;91;40m▄▄▄▄[0;37;40m [0;91;40m▀[0;97;40m   [0;91;40m▀[0;37;40m [0;91;40m▀▀▀[0;37;40m [0;97;40m [0;91;40m▀[0;37;40m [0;91;40m▀[0;37;40m [0;97;40m [0;91;40m▀[0;37;40m   [0;91;40m▀▀▀[0m
"""

if __name__ == "__main__":
    print(banner)
    parser = argparse.ArgumentParser(
        description="Enumerate M365 domains, retrieve tenant, check for MDI instance")
    parser.add_argument("-d", "--domain", required=True,
                        help="domain name, e.g. example.com")
    parser.add_argument("-r", "--retries", type=int, default=10,
                        help="max number of attempts to get a full response (default: 10)")
    get_domains(parser.parse_args())
