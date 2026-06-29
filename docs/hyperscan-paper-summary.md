# Hyperscan: A Fast Multi-pattern Regex Matcher for Modern CPUs

## Introduction

Main usecases: deep packet inspection.

String matching prefilter is a good practice. However,

1. String keywords are often defined manually by humans (Snort).
2. String matching triggers subregex matching, which may result in duplicate matchings.
3. Large automata.

Improvement in Hyperscan's philosophy

1. Identify string components automatically by performing rigorous structural analyses on the NFA graph of a regex.
2. String matching controls regex matching, aiming to avoid redundant operations. FA component matching is executed only when all relevant string and FA components are matched.
3. Try to build small FA.
4. SIMD: extend Shift-Or for string matching, bit representation for FA matching.

