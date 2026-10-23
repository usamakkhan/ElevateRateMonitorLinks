# Elevate domain discovery

GitHub Pages publishes [domain.json](https://usamakkhan.github.io/ElevateRateMonitorLinks/domain.json) as the stable discovery URL for the Android app. The public file contains only the current HTTPS web domain and up to three previous fallbacks. No rates or account data are published here.

The hourly workflow checks `/api/site-domain` on the current domain. A `repository_dispatch` event of type `elevate_domain_changed` can refresh it promptly after an admin changes the web app setting. The proposed domain must answer `/api/latest` successfully before publication. Keep the previous domain online until the manifest changes and clients have checked it.

The web app can send the dispatch if its server has `ELEVATE_PAGES_TOKEN`, a fine-grained GitHub token with Actions write access to this repository. Without that token, the hourly workflow remains the fallback. A manual workflow dispatch also accepts a new domain.
