# jupyterhub-nginx-chp #

A replacement for [configurable-http-proxy](http://github.com/jupyter/configurable-http-proxy) that uses nginx+lua instead of NodeJS.

## Pre-requisites ##

It needs a version of nginx with the [Lua module](https://github.com/openresty/lua-nginx-module) installed. It also requires the lua [cjson](http://www.kyne.com.au/~mark/software/lua-cjson.php) package installed.

### Debian / Ubuntu ##

On most Debian / Ubuntu systems, just installing the following packages should be enough:

```
sudo apt-get install nginx-extras lua-cjson
```

## Installation ##

You can install it easily via pip:

```
pip install nchp
```

## Usage ##

The simplest way to use it is to just let jupyterhub manage it directly. You can pass jupyterhub the path to the proxy it should start by either commandline:

```
--JupyterHub.proxy_cmd='/usr/local/bin/nchp'
```

or by adding the following line to your `jupyterhub_config.py`:

```
c.JupyterHub.proxy_cmd='/usr/local/bin/nchp'
```

This assumes that `/usr/local/bin/nchp` is the path to the `nchp` script. You can verify this by running `which nchp` on the commandline after installing it to find the full path.
