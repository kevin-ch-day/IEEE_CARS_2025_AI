# Paper 3 Reference and Citation Validation Audit

Date: 2026-07-13

## Scope

This audit covers citation placement, reference metadata, DOI usage, duplicate/orphan references, and claim-level support for the current Paper 3 manuscript. It does not change datasets, measurements, tables, figures, scientific values, or evidence.

## Summary

- Bibliography entries before cleanup: 20
- Bibliography entries after cleanup: 17
- Cited entries after cleanup: 17
- Uncited entries after cleanup: 0
- Missing BibTeX entries after cleanup: 0
- Duplicate titles: 0
- Duplicate DOIs: 0
- Self-citations: 0
- References removed: 3
- References corrected: 6
- References replaced with published versions: 0
- References left unresolved: 0

## Citation Range Policy

The manuscript now uses:

```tex
\usepackage[nocompress]{cite}
```

All multi-key citation commands were removed or split into claim-specific sentences. PDF text extraction was searched for compressed citation ranges such as `[4]-[6]`, `[4]-[6]`, and `[4-6]`; none were found.

Resolved multi-key citation commands:

- `\cite{androidPermissions2026,googlePlayDataSafety2026}` was split into separate Android permission and Google Play Data Safety claims.
- `\cite{arkalakis2024datasafety,khandelwal2024privacylabels,zhang2024privacysdks}` was split into source-specific claims about longitudinal Data Safety incompleteness, privacy-label over/under-reporting, and privacy-configurable SDK risk.
- `\cite{androidPermissions2026,androidPrivacyChecklist2026,androidSecurityBestPractices2026}` was split into permission, privacy-minimization, and security-practice claims.
- `\cite{yang2022maniscope,zhu2024sastandroid}` was split into manifest-exposure and Android SAST-tool consistency claims.

## Metadata Corrections

- `yang2022maniscope`: corrected author list, title, and pages using the ACM/DOI metadata for "Detecting and Measuring Misconfigured Manifests in Android Apps."
- `wang2023runtimepermissions`: added verified DOI `10.1109/TSE.2022.3148258`.
- `sutter2024dynamic`: added verified IEEE Access volume, page range, and DOI.
- `paci2023tracking`: added verified ACM ARES page range.
- `androidPermissions2026`, `androidPrivacyChecklist2026`, `androidSecurityBestPractices2026`, and `androidAppBundles2026`: updated title capitalization and last-updated notes from official Android Developers pages.
- `googlePlayDataSafety2026`: removed unsupported calendar-year publication value and retained official Google Play Help URL plus access date.
- `owaspMasvs2024`: retained as official OWASP MASVS web standard, version 2.1.0, and added a direct manuscript citation.

## Removed References

- `mejri2024timeseries`: uncited after claim audit.
- `neth2023androidtriage`: uncited after claim audit.
- `owaspMastg2024`: uncited after claim audit; MASVS remains cited where MASVS-aligned categories are discussed.

## DOI Policy

DOIs are included only where verified against publisher or DOI metadata. No DOI was added for Android documentation, Google Play Help, OWASP MASVS, USENIX web proceedings pages, or the arXiv-only Karyotakis preprint.

## Author List Check

The BibTeX file contains no `and others` entries and no manually inserted `et al.` author lists. PDF reference text contains no bibliography `et al.` entries. IEEEtran abbreviates given names as expected. One consecutive Google Android Developers web reference is rendered with the IEEE repeated-author dash; this is a bibliography style convention and not author-list truncation.

## Claim-Level Result

Every remaining citation is marked `DIRECT` in `generated/reference_claim_audit.csv`. No citation marked `NOT_SUPPORTED` remains. Table I rows were checked against the cited sources and do not cite the "This study" row.

## Verification Artifacts

- Claim-level CSV: `generated/reference_claim_audit.csv`
- Reference verification CSV: `generated/reference_verification.csv`

## Remaining Concerns

No unresolved reference concerns remain. The Karyotakis messaging-app comparison is retained as an arXiv preprint because a newer peer-reviewed version was not found during this pass.
