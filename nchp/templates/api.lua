-- Check for an authentication token. This is shared
-- with JupyterHub
local reqAuth = "token {{authtoken}}"

if ngx.var.http_AUTHORIZATION ~= reqAuth then
    ngx.exit(403);
end

if ngx.req.get_method() == "POST" then
    local cjson = require "cjson"
    local string = require "string"

    ngx.req.read_body()
    local body = cjson.decode(ngx.var.request_body)
    local target = body["target"]
    if target == nil then
        ngx.exit(400)
    end

    local routespec = string.sub(ngx.var.request_uri, 12)

    ngx.shared.routes:set(routespec, target)
    ngx.shared.lastaccess:set(routespec, os.time())
    ngx.log(ngx.ERR, ngx.var.request_uri)
    ngx.log(ngx.ERR, routespec)
    ngx.log(ngx.ERR, target)
    ngx.exit(201)
elseif ngx.req.get_method() == "DELETE" then
    local routespec = string.sub(ngx.var.request_uri, 12)

    ngx.shared.routes:delete(routespec)
    ngx.shared.lastaccess:delete(routespec)
elseif ngx.req.get_method() == "GET" then
    local cjson = require "cjson"
    local routes = {}

    local routespecs = ngx.shared.routes:get_keys()
    ngx.log(ngx.ERR, ngx.shared.routes:get_keys()[0])
    for i, spec in pairs(routespecs) do
        ngx.log(ngx.ERR, spec)
        routes[spec] = {
            target = ngx.shared.routes:get(spec),
            lastaccess = os.date("!%Y-%m-%dT%TZ", ngx.shared.lastaccess:get(spec))
        }
    end

    ngx.say(cjson.encode(routes))
end
