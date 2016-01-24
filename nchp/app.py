import jinja2
import os
from traitlets.config import Application
from traitlets import Unicode, Integer, Dict
from tempfile import NamedTemporaryFile


class NCHPApp(Application):
    name = Unicode("nchp")

    aliases = Dict({
        'ip': 'NCHPApp.public_ip',
        'port': 'NCHPApp.public_port',
        'api-ip': 'NCHPApp.api_ip',
        'api-port': 'NCHPApp.api_port',
        'default-target': 'NCHPApp.default_target',
    })

    dns_resolver = Unicode(
        '8.8.8.8',
        config=True,
        help='DNS resolver for nginx to use'
    )

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

    def initialize(self, argv=None):
        self.parse_command_line(argv)

    def build_nginx_conf(self):
        # FIXME: Use PackageLoader here!
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(
                    os.path.dirname(__file__),
                    'templates'
                )
            )
        )
        template = env.get_template('nginx.conf')
        context = {
            'dns_resolver': self.dns_resolver,
            'public_port': self.public_port,
            'public_ip': self.public_ip,
            'api_port': self.api_port,
            'api_ip': self.api_ip,
            'authtoken': self.auth_token,
        }
        return template.render(**context)

    def start(self):
        conf = self.build_nginx_conf()
        with NamedTemporaryFile() as f:
            f.write(conf.encode('utf-8'))
            f.flush()
            os.execle(self.nginx_path, self.nginx_path, '-c', f.name, {})


app = NCHPApp()
app.initialize()
app.start()
