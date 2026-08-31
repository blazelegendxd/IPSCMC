# IPSCMC Status
Upload this folder to a PUBLIC GitHub repository and enable GitHub Pages.

1. Settings → Pages → Deploy from branch → main → /(root)
2. Settings → Actions → General → allow workflows to write repository contents if prompted.
3. Actions → IPSCMC Status Monitor → Run workflow once.
4. It will then run every 5 minutes and build uptime history.
5. Add `status.ipsmc.fun` under Settings → Pages → Custom domain.

Live Minecraft data uses mcstatus.io for `play.ipsmc.fun:19145`. Discord counts are approximate Discord counts. The displayed Minecraft latency is the API monitor's latency, not each visitor's personal ping.

Important: your hostname `status.ipsmc.fun` can point to either QUICCSTATUS OR GitHub Pages, not both. If you move the status hostname to GitHub Pages, keep QUICCSTATUS available on its default domain or another hostname for its independent uptime history.
