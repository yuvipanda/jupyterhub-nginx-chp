import jinja2
import os
from traitlets.config import Application
from traitlets import Unicode, Integer, Dict
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit, urlunsplit

from nchp.dnsutils import get_nameservers


class NCHPApp(Application):
    name = Unicode("nchp")

    aliases = Dict({
        'ip': 'NCHPApp.public_ip',
        'port': 'NCHPApp.public_port',
        'api-ip': 'NCHPApp.api_ip',
        'api-port': 'NCHPApp.api_port',
        'default-target': 'NCHPApp.default_target',
        'ssl-key': 'NCHPApp.public_ssl_key',
        'ssl-cert': 'NCHPApp.public_ssl_cert',
        'api-ssl-key': 'NCHPApp.api_ssl_key',
        'api-ssl-cert': 'NCHPApp.api_ssl_cert'
    })

    dns_resolver = Unicode(
        config=True,
        help='DNS resolver for nginx to use'
    )

    def _dns_resolver_default(self):
        return get_nameservers()[0]

    public_ip = Unicode(
        '0.0.0.0',
        config=True,
        help='Public facing IP of the proxy'
    )

    public_port = Integer(
        8000,
        config=True,
        help='Public facing port of the proxy'
    )

    default_target = Unicode(
        config=True,
        help='Default proxy target (proto://host[:port])'
    )

    api_port = Integer(
        8001,
        config=True,
        help='Inward facing port for API requests'
    )

    api_ip = Unicode(
        '127.0.0.1',
        config=True,
        help='Inward facing IP for API requests'
    )

    auth_token = Unicode(
        os.environ.get('CONFIGPROXY_AUTH_TOKEN', ''),
        config=True,
        help='Auth token to use when talking to the proxy'
    )

    nginx_path = Unicode(
        '/usr/sbin/nginx',
        config=True,
        help='Full path to nginx executable to use'
    )

    public_ssl_cert = Unicode(
        config=True,
        help='Path to the SSL certificate for public facing proxy'
    )

    public_ssl_key = Unicode(
        config=True,
        help='Path to the SSL key for public facing proxy'
    )

    api_ssl_cert = Unicode(
        config=True,
        help='Path to the SSL certificate for private api'
    )

    api_ssl_key = Unicode(
        config=True,
        help='Path to the SSL key for private API'
    )

    def initialize(self, argv=None):
        self.parse_command_line(argv)

    def build_nginx_conf(self):
        # FIXME: Use PackageLoader here!
        env = jinja2.Environment(
            loader=jinja2.PackageLoader(
                'nchp',
                'templates'
            )
        )
        template = env.get_template('nginx.conf')

        # HACK: Replace localhost with 127.0.0.1
        # Reasons:
        #   - Some DNS servers do not resolve localhost
        #     to 127.0.0.1 (such as 8.8.8.8). So anyone
        #     using such DNS servers will have this fail,
        #     since nginx uses the DNS server only for
        #     name resolution
        #   - Some DNS servers resolve localhost in A but
        #     not AAAA records (like Wikimedia's!). This too
        #     causes nginx to fail, since the AAAA returns
        #     NXDOMAIN, which makes nginx fail hard
        #   - Even when all of this works, it is slightly
        #     faster to just avoid the DNS lookup for something
        #     as trivial as looking up localhost
        if self.default_target:
            parts = urlsplit(self.default_target)
            self.default_target = urlunsplit(
                (parts[0],
                 parts[1].replace('localhost', '127.0.0.1'),
                 parts[2], parts[3], parts[4])
            )

        public_ssl = self.public_ssl_cert != ''
        api_ssl = self.api_ssl_cert != ''

        context = {
            'dns_resolver': self.dns_resolver,
            'public_port': self.public_port,
            'public_ip': self.public_ip,
            'api_port': self.api_port,
            'api_ip': self.api_ip,
            'authtoken': self.auth_token,
            'default_target': self.default_target,
            'api_ssl': api_ssl,
            'public_ssl': public_ssl,
            'public_ssl_cert': self.public_ssl_cert,
            'public_ssl_key': self.public_ssl_key,
            'api_ssl_cert': self.api_ssl_cert,
            'api_ssl_key': self.api_ssl_key
        }
        return template.render(**context)

    def start(self):
        conf = self.build_nginx_conf()
        with NamedTemporaryFile() as f:
            f.write(conf.encode('utf-8'))
            f.flush()
            os.execle(self.nginx_path, self.nginx_path, '-c', f.name, {})
