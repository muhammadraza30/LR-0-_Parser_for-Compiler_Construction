# 🧠 SimpleLang Parser (with Urdu Keywords)

A lightweight parser for **SimpleLang**, a custom language using Urdu-style programming keywords. This project tokenizes source code and parses it using a Recursive Descent Parser (LR(0)) to identify valid syntax and provide meaningful error messages.

---

## 📝 Urdu Keyword Mapping

| English Keyword | Urdu Equivalent |
|------------------|-----------------|
| `if`             | `agar`          |
| `else`           | `varna`         |
| `while`          | `jabtak`        |
| `for`            | `tabtak`        |
| `print`          | `dikhao`        |
| `input`          | `likho`         |

---

## ⚙️ Project Features

- Lexical analysis (token generation)
- Syntax analysis with Recursive Descent Parser (LR(0))
- Clear syntax error messages with line references
- Interactive mode for real-time parsing and finding syntax errors
- Test automation for all test files

---

## 🚀 Getting Started

### Step 1: Navigate to the source directory

```bash
cd .\src
```

### Parse a test file
```bash
python main.py filename.sl
```

### Show tokens for a file
```bash
python main.py --tokens filename.sl
```

### Interactive mode
```bash
python main.py --interactive
```

### Run all tests
```bash
python tests/test_runner.py
```

## Common Examples

### Parse a test file
```bash
python main.py tests/example.sl
```


### View tokens for a test file
```bash
python main.py --tokens example.sl
```

### Run test suite from project root
```bash
python -m tests.test_runner
```
<div align="center"><h2 >THANK YOU</h2></div>
