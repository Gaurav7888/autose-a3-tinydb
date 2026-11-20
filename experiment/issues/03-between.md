# Add an inclusive between test to Query

I would like a query for inclusive ranges.

`Query().age.between(18, 65)` should match 18, 65 and 40. It should not match 17 or 66. The same test should work for strings, so `Query().name.between('b', 'd')` matches 'c' and 'b' and does not match 'a' or 'e'.

If the value cannot be compared with the bounds, the query should be false. None, a dict and a list are the cases I hit. It should not raise.

Two ranges that differ in either bound are different queries. `between(1, 5)` and `between(1, 9)` must not compare equal and must not share a hash.
