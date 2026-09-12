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


def get_domains(args):
    domain = args.domain
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
            status = resp.status
            response = resp.read().decode()
    except HTTPError as e:
        print(f"[-] HTTP {e.code} {e.reason}")
        print(e.read().decode(errors="replace"))
        return
    except URLError as e:
        print(f"[-] Network/TLS error: {e.reason}")
        return

    print(f"[i] HTTP {status}, {len(response)} bytes received")
    tree = ET.fromstring(response)

    for elem in tree.iter():
        if elem.tag.endswith("}ErrorCode") and elem.text and elem.text != "NoError":
            print(f"[-] Service returned ErrorCode: {elem.text}")

    ns = "{http://schemas.microsoft.com/exchange/2010/Autodiscover}Domain"
    domains = [e.text for e in tree.iter() if e.tag == ns]

    if not domains:
        print("[-] No <Domain> elements in response. Raw response:\n")
        print(response)
        return

    print("\n[+] Domains found:")
    print(*domains, sep="\n")

    tenant = next((d.split(".")[0] for d in domains if "onmicrosoft.com" in d), "")
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enumerate M365 domains, retrieve tenant, check for MDI instance")
    parser.add_argument("-d", "--domain", required=True,
                        help="domain name, e.g. example.com")
    get_domains(parser.parse_args())
