# Sakoe–Chiba citation review

Reviewed commit `fd48aa8` on `redesign`, specifically `content/05-dtw.md:53` and `content/_sources.toml:1–7`. Independently opened the supplied paper and checked publisher-indexed metadata. No builds or tests ran. The handoff still describes the earlier `pilot` planning state, but the current commit matches the request. Only this answer file was written.

1. **Support and locator: OK.** Printed p. 44, PDF page 2, section II-B, “Restrictions on Warping Function”, item 4, equation (8), gives `|i(k) - j(k)| <= r`. Renaming `r` to the course's `w` preserves the condition. The locator is correct. [Paper, p. 44](https://jeffe.cs.illinois.edu/teaching/compgeom/refs/Sakoe-Chiba-DTW.pdf#page=2).

2. **Band interpretation: OK.** Algebraically, the inequality places every path point between `j = i - r` and `j = i + r`. “A band around the diagonal” is a fair geometric paraphrase, not an additional performance claim. [Paper, equation (8)](https://jeffe.cs.illinois.edu/teaching/compgeom/refs/Sakoe-Chiba-DTW.pdf#page=2).

3. **Zero and no window: OK in context.** The paper specifies positive integer `r`. The course's zero-width case is the boundary extension of the inequality, while “no window” removes this restriction. Those are course choices, not settings attributed to the paper. The new sentence attributes the band condition, not the original algorithm's entire parameter domain. The surrounding lesson distinguishes zero width and no window at lines 55–57, and `AGENTS.md:50` states the course contract. No wording change is required. [Paper, condition 4](https://jeffe.cs.illinois.edu/teaching/compgeom/refs/Sakoe-Chiba-DTW.pdf#page=2).

4. **Metadata: OK.** The scan's first page confirms **Hiroaki Sakoe** and **Seibi Chiba**. The title, journal, volume **26**, issue **1**, pages **43–49**, year **1978**, and DOI **10.1109/TASSP.1978.1163055** match the publisher's indexed record. The scan's volume styling `ASSP-26` does not make `26(1)` incorrect. [Paper title page](https://jeffe.cs.illinois.edu/teaching/compgeom/refs/Sakoe-Chiba-DTW.pdf#page=1), [IEEE metadata](https://ieeexplore.ieee.org/abstract/document/1163055/authors). Direct IEEE access presented an anti-bot page and Crossref retrieval failed, so this is not a successful independent Crossref API check.

5. **Hosted copy: OK for checking the text, with authorization unverified.** Its journal pages and bibliographic identity support treating it as a scan of the published paper. University hosting alone does not establish permission to repost it. The scan carries an IEEE copyright notice and a Saint Louis University licensed-download restriction. I cannot certify the host's redistribution authorization. Retain the DOI-only public link as proposed. [Inspected scan and notices](https://jeffe.cs.illinois.edu/teaching/compgeom/refs/Sakoe-Chiba-DTW.pdf).

**Verdict: approved as is.** This approves the new sentence, locator and `sakoe78` metadata, not the entire lesson or the scan's redistribution rights.

**Handoff:** Claude may record this review for the inspected citation. No content correction is required. No other open task is known to depend on retaining this chat.
