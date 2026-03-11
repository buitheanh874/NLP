# Step 04 - TF-IDF Stats
- Variant: V6 (char=True, clause_split=False, negation=True).
- Feature dims: total 100000, primary vocab ~50000; components: {'word_tfidf': 50000, 'char_tfidf': 50000}.
- Matrix shapes: train (104397, 100000), val (14914, 100000), test (29828, 100000)
- Avg nnz per sample: train 225.8, test 224.4
- Top 20 tokens by IDF saved in 04_tfidf_stats.json (when available).