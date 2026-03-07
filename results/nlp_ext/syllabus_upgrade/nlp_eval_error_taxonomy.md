# Error Taxonomy Report

- total_misclassified_rows: 1454
- false_negative_0: 194
- false_positive_0: 1260

## Taxonomy Counts

| error_type       | taxonomy_category   |   count |      share |
|:-----------------|:--------------------|--------:|-----------:|
| false_negative_0 | other               |     101 | 0.520619   |
| false_negative_0 | short_text          |      45 | 0.231959   |
| false_negative_0 | negation_pattern    |      28 | 0.14433    |
| false_negative_0 | contrast_pattern    |      17 | 0.0876289  |
| false_negative_0 | domain_issue_term   |       3 | 0.0154639  |
| false_positive_0 | negation_pattern    |     627 | 0.497619   |
| false_positive_0 | other               |     408 | 0.32381    |
| false_positive_0 | contrast_pattern    |     131 | 0.103968   |
| false_positive_0 | short_text          |      49 | 0.0388889  |
| false_positive_0 | domain_issue_term   |      40 | 0.031746   |
| false_positive_0 | slang_or_abbrev     |       3 | 0.00238095 |
| false_positive_0 | punctuation_heavy   |       2 | 0.0015873  |

## Examples: false_negative_0
- other:
  row=252, p_pos=0.710, text="Way to have only one for your Prime Day."
  row=556, p_pos=0.779, text="Se equivocaron con el envío...Se fue a otra parte."
- short_text:
  row=415, p_pos=0.512, text="No envelope"
  row=1291, p_pos=0.782, text="_x"
- negation_pattern:
  row=544, p_pos=0.577, text="little security, I did not realize when I bought that gift card"
  row=1917, p_pos=0.545, text="Amazon no longer offers 2% bonus, or cash back on reloads using debit card. As a prime member I miss that very much."

## Examples: false_positive_0
- negation_pattern:
  row=36, p_pos=0.106, text="I thought I would get the $25.00 gift card ready to use, but I had to go online and activate the card.  It was easy to do, but not what I expected."
  row=101, p_pos=0.412, text="Was able to send this gift card to my daughter, was afraid it would not show who it was from, but it showed my name. Super Easy!"
- other:
  row=11, p_pos=0.133, text="Don’t like the fee"
  row=18, p_pos=0.337, text="Why not!? Pay $100 and get $110 Amazon gift card. Since I buy almost everything from Amazon I could reload the card every month if they had given me the prom..."
- contrast_pattern:
  row=142, p_pos=0.066, text="I only loaded the gift card so I could use 500 dollars off of my credit card to add onto 1600 dollars for a large purchase and I couldn’t use both my credit ..."
  row=448, p_pos=0.109, text="Disliked nothing.<br />Had a few missteps in the beginning, but recognized my error and was fine. Totally user error on my part."
