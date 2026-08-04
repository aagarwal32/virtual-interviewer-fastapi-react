'''
The source dataset stripped HTML <sup> tags without inserting a caret, so
exponent notation collapsed into plain digit runs, e.g.:
    "10<sup>9</sup>"  ->  "109"   (should be "10^9")
    "2<sup>31</sup>"  ->  "231"   (should be "2^31")
    "O(n<sup>2</sup>)" -> "O(n2)" (should be "O(n^2)")

These tables were built by scanning both problem_lists JSONL files for
digit tokens on constraint lines (lines containing "<=") and letter+digit
tokens anywhere in the description, then cross-checking each candidate
against sample context lines to rule out legitimate literal numbers.
'''

# Numeric base-10 / base-2 exponents found on constraint ("<=") lines.
# Only apply these within <=-context lines -- these same digit strings are
# common legitimate literals elsewhere in a description (e.g. "100" as a
# plain array length), so a global find/replace would corrupt unrelated text.
SUPERSCRIPT_FIXES = {
    "103": "10^3",
    "104": "10^4",
    "105": "10^5",
    "106": "10^6",
    "107": "10^7",
    "108": "10^8",
    "109": "10^9",
    "1012": "10^12",
    "1014": "10^14",
    "1015": "10^15",
    "1018": "10^18",
    "216": "2^16",
    "231": "2^31",
}

# Big-O complexity notation. "n2" reliably means n^2 when it shows up inside
# O(...) (e.g. "O(n2) time complexity"), but NOT always outside that context --
# at least one problem uses "n1" and "n2" as two distinct integer variable
# names ("two integers n1 and n2"), which this table would wrongly mangle if
# applied as a blind global replace. Scope this to Big-O expressions
# specifically (e.g. only inside "O(...)"), not the whole description.
BIGO_FIXES = {
    "n2": "n^2",
}

# task_id is a hyphenated slug (e.g. "two-sum") used to derive a human-readable
# title ("Two Sum") by replacing hyphens with spaces and capitalizing each word.
# These words are genuine acronyms/initialisms that should render fully
# uppercase instead -- plain word-capitalization would otherwise give "Xor"
# instead of "XOR", "Bst" instead of "BST", etc. Found by scanning every
# distinct word across all task_ids in both problem_lists JSONL files.
TITLE_WORD_OVERRIDES = {
    "xor": "XOR",
    "bst": "BST",
    "bsts": "BSTS",
    "gcd": "GCD",
    "gcds": "GCDS",
    "ip": "IP",
    "lcm": "LCM",
    "dfs": "DFS",
    "dna": "DNA",
    "utf": "UTF",
    "ipo": "IPO",
    "rgb": "RGB",
    "html": "HTML",
    "lcp": "LCP",
    "cpu": "CPU",
}

# task_ids that don't split cleanly into words at all (no hyphen boundary to
# work with), so no per-word casing rule can fix them -- these need the whole
# title given as a literal override instead.
TASK_ID_OVERRIDES = {
    "sqrtx": "Sqrt(x)",
}

# Reviewed and deliberately left out of SUPERSCRIPT_FIXES above -- each of
# these is either a common legitimate literal in this dataset (confirmed by
# sampling actual context lines), or too rare/ambiguous to fix confidently.
# Listed here so the reasoning isn't lost if you want to revisit any of them.
AMBIGUOUS_NOT_INCLUDED = {
    "100": "confirmed literal 100 in context (e.g. '1 <= n <= 100'), far more common than a 10^0 bound",
    "1000": "confirmed literal 1000, common round-number constraint",
    "10000": "confirmed literal 10000",
    "1024": "confirmed literal 1024 (2^10 used directly as a value, e.g. '[1024,512,256,...]'), not 10^24",
    "1010": "only 5 occurrences -- could be literal 1010 or 10^10, unclear from context",
    "1022": "only 1 occurrence, unclear",
    "102": "only 1 occurrence, unclear -- could be literal or 10^2",
    "10100": "irregular pattern, likely an unrelated data artifact",
    "200": "confirmed literal 200, common round-number constraint",
    "250": "confirmed literal 250",
    "255": "confirmed literal 255 (byte/IP-address value range '0 <= data[i] <= 255'), not 2^55",
    "256": "confirmed literal 256 (2^8 used directly as a value), not 2^56",
    "228": "only 2 occurrences, ambiguous with literal 228",
    "220": "only 2 occurrences, ambiguous with literal 220 or 2^20",
    "210": "only 2 occurrences, ambiguous with literal 210 or 2^10",
    "230": "only 2 occurrences, ambiguous with literal 230 or 2^30",
    "215": "only 1 occurrence, ambiguous",
}
