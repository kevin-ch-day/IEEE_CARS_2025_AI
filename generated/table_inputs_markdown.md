# Generated Tables


## Fifteen-app cohort and selected cutoff evidence.

| App | Category | Package | Version | PCAPs | Idle/QFG/Int |
| --- | --- | --- | --- | --- | --- |
| BBC News | News | bbc.mobile.news.ww | 2026.5.0 | 10 | 4/0/6 |
| CNN | News | com.cnn.mobile.android.phone | 26.13.0 | 12 | 4/1/7 |
| Facebook | Social/content | com.facebook.katana | 567.1.0.52.74 | 8 | 3/1/4 |
| Messenger | Messaging | com.facebook.orca | 567.1.0.53.87 | 9 | 4/0/5 |
| Instagram | Social/content | com.instagram.android | 436.0.0.41.73 | 7 | 2/4/1 |
| LinkedIn | Professional social | com.linkedin.android | 4.1.1218 | 8 | 3/1/4 |
| Pinterest | Social/content | com.pinterest | 14.26.0 | 7 | 5/0/2 |
| Reddit | Social/content | com.reddit.frontpage | 2026.26.0 | 6 | 2/3/1 |
| Signal | Messaging | org.thoughtcrime.securesms | 8.18.2 | 7 | 3/0/4 |
| Snapchat | Messaging/social | com.snapchat.android | 14.14.0.43 | 5 | 1/2/2 |
| Telegram | Messaging | org.telegram.messenger | 12.8.3 | 7 | 3/0/4 |
| The Guardian | News | com.guardian | 6.226.23011 | 9 | 3/2/4 |
| TikTok | Social/video | com.zhiliaoapp.musically | 45.7.3 | 11 | 0/8/3 |
| WhatsApp | Messaging | com.whatsapp | 2.26.25.80 | 9 | 4/0/5 |
| X | Social/content | com.twitter.android | 12.5.0-release.0 | 8 | 3/1/4 |


## Static exposure summary for selected app builds.

| App | Risk | Grade | Danger Perm. | High | Privacy | Platform | Network | Provider ACL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BBC News | 0.72 | A | 4 | 2 | 0 | 20 | 1 | 0 |
| CNN | 0.12 | A | 1 | 1 | 1 | 29 | 2 | 0 |
| Facebook | 6.00 | C | 18 | 27 | 4 | 161 | 5 | 0 |
| Messenger | 5.88 | C | 18 | 18 | 2 | 98 | 2 | 0 |
| Instagram | 5.48 | C | 19 | 37 | 1 | 124 | 2 | 0 |
| LinkedIn | 4.08 | C | 14 | 4 | 1 | 55 | 1 | 0 |
| Pinterest | 2.84 | B | 11 | 2 | 2 | 16 | 2 | 0 |
| Reddit | 3.16 | B | 10 | 1 | 1 | 47 | 0 | 0 |
| Signal | 5.52 | C | 18 | 1 | 1 | 34 | 0 | 0 |
| Snapchat | 6.04 | C | 18 | 1 | 1 | 323 | 1 | 0 |
| Telegram | 6.59 | D | 20 | 3 | 1 | 41 | 2 | 0 |
| The Guardian | 0.74 | A | 2 | 1 | 0 | 23 | 1 | 0 |
| TikTok | 4.40 | C | 16 | 13 | 1 | 75 | 1 | 0 |
| WhatsApp | 7.55 | D | 20 | 12 | 1 | 99 | 0 | 0 |
| X | 4.48 | C | 14 | 1 | 1 | 84 | 2 | 0 |


## Runtime evidence coverage and selected behavior indicators.

| App | Idle | QFG | Int | PCAPs | Domains | Services | Shift Metric | Effect |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BBC News | 4 | 0 | 6 | 10 | 54 | 16 | packets_per_second | large |
| CNN | 4 | 1 | 7 | 12 | 52 | 20 | pcap_bytes | large |
| Facebook | 3 | 1 | 4 | 8 | 73 | 9 |  |  |
| Messenger | 4 | 0 | 5 | 9 | 18 | 3 | packets_per_second | large |
| Instagram | 2 | 4 | 1 | 7 | 43 | 4 |  |  |
| LinkedIn | 3 | 1 | 4 | 8 | 21 | 5 | packets_per_second | large |
| Pinterest | 5 | 0 | 2 | 7 | 11 | 6 |  |  |
| Reddit | 2 | 3 | 1 | 6 | 15 | 4 |  |  |
| Signal | 3 | 0 | 4 | 7 | 1 | 1 |  |  |
| Snapchat | 1 | 2 | 2 | 5 | 13 | 4 |  |  |
| Telegram | 3 | 0 | 4 | 7 | 1 | 1 |  |  |
| The Guardian | 3 | 2 | 4 | 9 | 42 | 13 | packets_per_second | large |
| TikTok | 0 | 8 | 3 | 11 | 43 | 7 | pcap_bytes | large |
| WhatsApp | 4 | 0 | 5 | 9 | 13 | 2 | packets_per_second | large |
| X | 3 | 1 | 4 | 8 | 18 | 5 | pcap_bytes | large |


## Cross-layer examples linking static posture and runtime coverage.

| App | Risk | PCAPs | Domains | Interpretation cue |
| --- | --- | --- | --- | --- |
| WhatsApp | 7.55 | 9 | 13 | high-priority static findings; strong interactive coverage |
| Telegram | 6.59 | 7 | 1 | high-priority static findings; strong interactive coverage |
| Snapchat | 6.04 | 5 | 13 | QFG foreground baseline present |
| Facebook | 6.00 | 8 | 73 | high-priority static findings; broad observed domain surface |
| Messenger | 5.88 | 9 | 18 | high-priority static findings; strong interactive coverage |
| Signal | 5.52 | 7 | 1 | strong interactive coverage |
| Instagram | 5.48 | 7 | 43 | high-priority static findings; broad observed domain surface |
| X | 4.48 | 8 | 18 | QFG foreground baseline present; strong interactive coverage |
| TikTok | 4.40 | 11 | 43 | high-priority static findings; broad observed domain surface |
| LinkedIn | 4.08 | 8 | 21 | high-priority static findings; QFG foreground baseline present |
