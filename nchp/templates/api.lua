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
    local user = body["user"]
    if target == nil then
        ngx.exit(400)
    end

    local routespec = string.sub(ngx.var.request_uri, 12)

    ngx.shared.routes:set(routespec, target)
    ngx.shared.users:set(routespec, user)
    ngx.shared.lastaccess:set(routespec, os.time())
    ngx.exit(201)
elseif ngx.req.get_method() == "DELETE" then
    local routespec = string.sub(ngx.var.request_uri, 12)

    ngx.shared.routes:delete(routespec)
    ngx.shared.users:delete(routespec)
    ngx.shared.lastaccess:delete(routespec)
elseif ngx.req.get_method() == "GET" then
    local cjson = require "cjson"
    local routes = {}

    local routespecs = ngx.shared.routes:get_keys()
    for i, spec in pairs(routespecs) do
        routes[spec] = {
            target = ngx.shared.routes:get(spec),
            user = ngx.shared.users:get(spec),
            last_activity = os.date("!%Y-%m-%dT%TZ", ngx.shared.lastaccess:get(spec))
        }
    end

    ngx.say(cjson.encode(routes))
end
