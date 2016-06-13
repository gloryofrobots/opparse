a = 2 + 3 - 5 * (6 + 7)
a = {}     -- create a table and store its reference in `a'
k = "x"
a[k] = 10        -- new entry, with key="x" and value=10
a[20] = "great"  -- new entry, with key=20 and value="great"
print(a["x"])    --> 10
print(a[k])      --> "great"
a["x"] = a["x"] + 1     -- increments entry "x"

-- a = {}; a.x = 1; a.y = 0
-- b = {}; b.x = 1; b.y = 0
-- c = a