# one_of treats True, 1 and "1" as the same value

Hello,

`Query().count.one_of([1, 2])` matches a document whose count is True. In our data True means the row is enabled and 1 is a count. They are not the same value. `one_of([True])` also matches 1, and `one_of([1])` matches the string "1". `one_of([1])` also matches 1.0.

Please match a candidate only when it is equal to an entry and has the same type. 1 matches 1. True matches True. 1.0 matches 1.0. 1 does not match True, 1.0 or "1".

String lists should keep working: `one_of(['a', 'b'])` still matches 'a' and still does not match 'c'.
