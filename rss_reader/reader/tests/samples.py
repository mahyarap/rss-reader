valid_feed = b"""
<rss version="2.0">
<channel>
  <title>Planet Ubuntu</title>
  <link>http://planet.ubuntu.com/</link>
  <language>en</language>
  <description>Planet Ubuntu - http://planet.ubuntu.com/</description>
  <item>
    <title>Kees Cook: package hardening asymptote</title>
    <guid isPermaLink="false">https://outflux.net/blog/?p=1304</guid>
    <link>https://outflux.net/blog/archives/2019/06/27/package-hardening-asymptote/</link>
    <description>
      <p>Forever ago I set up tooling to generate graphs representing the adoption</p>
    </description>
    <pubDate>Thu, 27 Jun 2019 22:35:09 +0000</pubDate>
  </item>
</channel>
</rss>
"""

invalid_feed = b"""
<rss version="2.0">
<channel>
  <title>Planet Ubuntu</title>
  <link>http://planet.ubuntu.com/</link>
  <language>en</language>
  <description>Planet Ubuntu - http://planet.ubuntu.com/</description>
  <item>
    <title>Kees Cook: package hardening asymptote</title>
    <guid isPermaLink="false">https://outflux.net/blog/?p=1304</guid>
    <link>https://outflux.net/blog/archives/2019/06/27/package-hardening-asymptote/</link>
    <description>
      <p>Forever ago I set up tooling to generate graphs representing the adoption</p>
    </description>
    <pubDate>Thu, 27 Jun 2019 22:35:09 +0000</pubDate>
  </item>
</rss>
"""

invalid_feed_no_pubdate = b"""
<rss version="2.0">
<channel>
  <title>Planet Ubuntu</title>
  <link>http://planet.ubuntu.com/</link>
  <language>en</language>
  <description>Planet Ubuntu - http://planet.ubuntu.com/</description>
  <item>
    <title>Kees Cook: package hardening asymptote</title>
    <guid isPermaLink="false">https://outflux.net/blog/?p=1304</guid>
    <link>https://outflux.net/blog/archives/2019/06/27/package-hardening-asymptote/</link>
    <description>
      <p>Forever ago I set up tooling to generate graphs representing the adoption</p>
    </description>
  </item>
</channel>
</rss>
"""
