---
name: Cookie expired / paywall fetch fails
about: The brief shows ⚠️ FT/WSJ cookie may need refresh, or fetch_ft.sh / fetch_wsj.sh return ## ERROR
title: "[Cookie] "
labels: cookie
---

## Which outlet

- [ ] FT
- [ ] WSJ

## What you've tried

- [ ] Re-exported the cookie via Cookie-Editor (Export as Header String)
- [ ] Confirmed I can read paywalled articles in my logged-in browser
- [ ] Saved the new cookie to `ft_cookie.txt` / `wsj_cookie.txt` with `chmod 600`
- [ ] Ran the fetcher manually with a known-good URL — still errors

## Output of manual fetcher run

```
<!-- For FT: paste the output of `./fetch_ft.sh <url>` -->
<!-- For WSJ: try `./discover_wsj.sh --max 3` first (URL discovery), then -->
<!-- `./fetch_wsj.sh <url>` (body fetch). Paste both outputs. -->
<!-- IMPORTANT: do NOT paste the contents of your cookie file. -->
```

## Possible reasons (rule out first)

- [ ] Subscription actually expired? (Try logging in via browser)
- [ ] Wrong Cookie-Editor export format? (Should be "Export as Header String", not JSON)
- [ ] Cookie file has trailing whitespace or newlines that broke parsing?
- [ ] Subscription is on a different account from the browser session you exported from?
