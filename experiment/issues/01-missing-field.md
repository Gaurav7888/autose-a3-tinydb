# delete, increment and decrement throw when the field is missing

Hi,

I run `db.update(delete('nickname'))` over a table where some documents have a nickname and some do not. TinyDB raises KeyError on the first document that does not have the field, and the documents that did have it are left unchanged because the write never happens.

The same thing happens with increment and decrement on a counter that a few older documents do not have yet.

What I need:

- delete of a field that is not there should do nothing to that document. Other documents in the same update should still lose the field.
- increment of a missing field should treat it as 0 and then add 1, so the stored value is 1.
- decrement of a missing field should treat it as 0 and then subtract 1, so the stored value is -1.
- add and subtract should keep raising if the field is missing. I do not want a missing field to be guessed for those two, because add is also used on strings.

Thanks.
