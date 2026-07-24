# CF Mobile Preferred-Domain Feed

This GitHub Pages feed is rebuilt daily from VPS789's `cfIpTop20` endpoint.

Selection rule: only entries with China Mobile (`ydPkgLostRate`) equal to `0%` are retained. Latency is shown in the node label but is not used as a filter.

Stable subscription URL after Pages is enabled:

```text
https://zhikun-dev.github.io/cfip-mobile-sub/cf-mobile.txt
```

The entries are Cloudflare connection addresses. When using them with EdgeTunnel, keep your own EdgeTunnel domain in the TLS SNI and HTTP Host fields; do not replace those fields with a selected address.
