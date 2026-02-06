# File Classifier - Super Simple Guide

## What does it do?

**It automatically sorts your files into 3 types by reading what's inside them.**

## The 3 Types

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  📊 SIMPLE = Tables/Data                           │
│     • Rows and columns                             │
│     • Example: weather.cli, parameters.bsn         │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🔗 CONNECT = Links Between Things                 │
│     • Connects components                          │
│     • Example: hru.con, channel.con                │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ⚙️  UNIQUE = Master Settings                      │
│     • Configuration files                          │
│     • Example: file.cio, management.sch            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## How to Use It

**Step 1:** Run the command
```bash
python -m ford.classify_files your_file.txt
```

**Step 2:** See the result
```
File             Classification
---------------  --------------
your_file.txt    Simple
```

That's it! 

## Example

Let's classify 3 files:

```bash
python -m ford.classify_files weather.cli hru.con file.cio
```

**Output:**
```
File          Type      Why?
-----------   -------   ----------------------
weather.cli   Simple    Table with data rows
hru.con       Connect   Links HRUs & channels  
file.cio      Unique    Master config file
```

## Why is this useful?

Instead of you telling the computer "this file is type X", the computer **figures it out** by looking at the file's content.

**Magic!** ✨ No manual work needed.

---

**Need more details?** See [HOW_IT_WORKS.md](HOW_IT_WORKS.md)
