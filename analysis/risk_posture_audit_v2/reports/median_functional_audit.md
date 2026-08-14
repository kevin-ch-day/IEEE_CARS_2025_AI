# Median functional audit (smoothed PPS shift)

z_i = log2((I+1)/(B+1)); B = strict-idle median if that class exists, else QFG.
Sorted apps: The Guardian, CNN, Reddit, BBC News, X, Snapchat, Pinterest, TikTok, Facebook Messenger, LinkedIn, Instagram, Facebook, Telegram, Signal, WhatsApp
8th of 15 (median app): **TikTok** z=3.385245 → formatted **3.39** (paper 3.39).
7th=Pinterest 3.377383; 9th=Facebook Messenger 3.620363.

Local derivative of the sample median is piecewise: while the order is fixed and n is odd,
d median / d z_i = 1 for the current median observation and 0 otherwise.
It is nondifferentiable at order crossings. Finite perturbations confirm this only inside
a neighborhood that does not reorder the 8th order statistic.
TikTok is the only QFG baseline fallback.
