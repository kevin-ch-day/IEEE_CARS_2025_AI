# Candidate manuscript language (not inserted)

## Abstract
One use of **privacy and security risk posture**.

## Introduction
Risk denotes evidence-supported exposure to conditions that may enable privacy or security harm, rather than a calibrated probability of exploitation or realized harm.

## Methodology
Static indicators characterize potential exposure. Runtime indicators characterize behavior observed during controlled execution. Tracker association, when reported, identifies communication with infrastructure independently classified as tracking-related. The layers are not collapsed into a composite risk score.

## Discussion
Disagreement between static exposure and observed runtime behavior is itself risk-relevant: low observed activity does not negate a broad packaged surface, and high runtime activity does not by itself establish exploitation.

## Limitations
Tracker-associated hostnames identify infrastructure context only; they do not reveal encrypted payload contents or demonstrate private-data leakage.

## Conclusion
Together, the evidence layers provide an auditable characterization of app-level privacy and security risk posture while preserving the distinction between potential exposure and observed runtime behavior.
