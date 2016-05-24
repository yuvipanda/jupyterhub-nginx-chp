local routespec = ngx.var.request_uri

local specs = ngx.shared.routes:get_keys()

-- FIXME: This is a O(nlogn) algorithm for routing, where we
-- first sort the table in descending order of length and then
-- route to the first prefix that matches. The sorting is O(nlogn)
-- so the entire thing is O(logn). We can easily get this to O(n)
-- and with a trie, even lower.
table.sort(specs, function(a, b) return string.len(a) < string.len(b) end)
for i, spec in pairs(specs) do
    ngx.log(ngx.ERR, spec .. routespec)
    if string.sub(routespec,1,string.len(spec)) == spec then
        ngx.var.upstream = ngx.shared.routes:get(spec)

        -- Update the lastaccesstime for this route!
        ngx.shared.lastaccess:set(spec, os.time())
        return
    end
end
if target == nil then
    {% if default_target -%}
        ngx.var.upstream = "{{default_target}}"
    {% else -%}
        ngx.exit(404)
    {% endif -%}
end
