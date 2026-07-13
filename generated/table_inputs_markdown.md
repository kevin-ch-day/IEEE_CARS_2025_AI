# Generated Tables


## Fifteen-app cohort and selected cutoff evidence.

| App | Category | Package | Version | PCAPs | Idle/QFG/Int |
| --- | --- | --- | --- | --- | --- |
| BBC News | News | bbc.mobile.news.ww | 2026.5.0 | 10 | 4/0/6 |
| CNN | News | com.cnn.mobile.android.phone | 26.13.0 | 12 | 4/1/7 |
| Facebook | Social/content | com.facebook.katana | 567.1.0.52.74 | 8 | 3/1/4 |
| Facebook Msg | Messaging | com.facebook.orca | 567.1.0.53.87 | 9 | 4/0/5 |
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

| App | Findings | High+Med | Danger Perm. | Unguarded Comp. | Privacy | Platform | Network | Provider ACL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BBC News | 24 | 16 | 4 | 14 | 0 | 20 | 1 | 0 |
| CNN | 34 | 25 | 1 | 21 | 1 | 29 | 2 | 0 |
| Facebook | 181 | 166 | 18 | 111 | 4 | 129 | 4 | 0 |
| Facebook Msg | 113 | 98 | 18 | 67 | 2 | 86 | 2 | 0 |
| Instagram | 140 | 127 | 19 | 76 | 1 | 101 | 3 | 0 |
| LinkedIn | 58 | 52 | 14 | 26 | 1 | 32 | 1 | 0 |
| Pinterest | 20 | 16 | 11 | 11 | 1 | 15 | 0 | 0 |
| Reddit | 53 | 47 | 10 | 17 | 1 | 24 | 0 | 0 |
| Signal | 40 | 35 | 18 | 17 | 1 | 22 | 0 | 0 |
| Snapchat | 339 | 325 | 18 | 23 | 2 | 33 | 3 | 0 |
| Telegram | 51 | 43 | 20 | 27 | 1 | 34 | 2 | 0 |
| The Guardian | 28 | 22 | 2 | 15 | 0 | 22 | 1 | 0 |
| TikTok | 86 | 74 | 16 | 59 | 2 | 72 | 2 | 0 |
| WhatsApp | 115 | 104 | 20 | 58 | 1 | 72 | 3 | 0 |
| X | 93 | 83 | 14 | 28 | 1 | 36 | 2 | 0 |


## Runtime evidence coverage and selected behavior indicators.

| App | Idle | QFG | Int | PCAPs | Domains | Services | Shift Metric | Effect |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BBC News | 4 | 0 | 6 | 10 | 54 | 16 | packets_per_second | large |
| CNN | 4 | 1 | 7 | 12 | 52 | 20 | pcap_bytes | large |
| Facebook | 3 | 1 | 4 | 8 | 73 | 9 |  |  |
| Facebook Msg | 4 | 0 | 5 | 9 | 18 | 3 | packets_per_second | large |
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

| App | High+Med | PCAPs | Domains | Interpretation cue |
| --- | --- | --- | --- | --- |
| Snapchat | 325 | 5 | 13 | high-priority static findings; QFG foreground baseline present |
| Facebook | 166 | 8 | 73 | high-priority static findings; broad observed domain surface |
| Instagram | 127 | 7 | 43 | high-priority static findings; broad observed domain surface |
| WhatsApp | 104 | 9 | 13 | high-priority static findings; strong interactive coverage |
| Facebook Msg | 98 | 9 | 18 | high-priority static findings; strong interactive coverage |
| X | 83 | 8 | 18 | QFG foreground baseline present; strong interactive coverage |
| TikTok | 74 | 11 | 43 | high-priority static findings; broad observed domain surface |
| LinkedIn | 52 | 8 | 21 | high-priority static findings; QFG foreground baseline present |
| Reddit | 47 | 6 | 15 | QFG foreground baseline present |
| Telegram | 43 | 7 | 1 | high-priority static findings; strong interactive coverage |
