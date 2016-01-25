import re


def get_nameservers():
    """
    Return a list of nameservers from parsing /etc/resolv.conf
    """
    nameservers = []
    with open('/etc/resolv.conf') as f:
        for line in f:
            match = re.match(r'\s*nameserver\s+(.*)', line)
            print(line)
            if match:
                nameservers.append(match.groups()[0])
    return nameservers
