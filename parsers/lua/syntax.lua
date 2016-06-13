a = 2 + 3 - 5 * (6 + 7)
a = {}     -- create a table and store its reference in `a'
k = "x"
a[k] = 10        -- new entry, with key="x" and value=10
a[20] = "great"  -- new entry, with key=20 and value="great"
print(a["x"])    --> 10
print(a[k])      --> "great"
a["x"] = a["x"] + 1     -- increments entry "x"

a = {}; a.x = 1; a.y = 0
b = {}; b.x = 1; b.y = 0
c = a

-- break on juxtaposition
a = 2 + 3
+ 4 b = 2  c = add(13, 15)

days = {"Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday"}

tab = {sin(1), sin(2), sin(3), sin(4),
           sin(5), sin(6), sin(7), sin(8)}

a = {x=0, y=1}

polyline = {color="blue", thickness=2, npoints=4,
                 {x=0,   y=0},
                 {x=-10, y=0},
                 {x=-10, y=1},
                 {x=0,   y=1}
               }

opnames = {["+"] = "add", ["-"] = "sub",
               ["*"] = "mul", ["/"] = "div"}

i = 20; s = "-"
s_a = {[i+0] = s, [i+1] = s..s, [i+2] = s..s..s}

a = {x=10, y=45, "one", "two", "three"}

local a, b = 1, 10
local a = 1
local a
local a,b,c

if a<b then
      print(a)   --> 1
      local a    -- `= nil' is implicit
      print(a)   --> nil
end          -- ends the block started at `then'

if i > 20 then
    local x          -- local to the "then" body
    x = 20
    print(x + 2)
else
    print(x)         --> 10  (the global one)
end


if op == "+" then
    r = a + b
elseif op == "-" then
    r = a - b
elseif op == "*" then
    r = a*b
elseif op == "/" then
    r = a/b
else
    error("invalid operation")
end

while a[i] do
   print(a[i])
   i = i + 1
end

repeat
   line = os.read()
until line ~= ""

for i=1,f(x) do print(i) end
for i=10,1,-1 do print(i) end

local found = nil
for i=1,a.n do
    if a[i] == value then
        found = i      -- save value of `i'
        break
    end
end

for i,v in ipairs(a) do print(v) end

function add (a)
      local sum = 0
      for i,v in ipairs(a) do
        sum = sum + v
      end
      return sum
end

function maximum (a)
    local mi = 1          -- maximum index
    local m = a[mi]       -- maximum value
    for i,val in ipairs(a) do
        if val > m then
            mi = i
            m = val
        end
    end
    return m, mi
end

reduce({1,2,3,4}, function (el, acc) return el + acc, acc + 42, 42 end)

function fwrite (fmt, ...)
    return io.write(string.format(fmt, unpack(arg)))
end
