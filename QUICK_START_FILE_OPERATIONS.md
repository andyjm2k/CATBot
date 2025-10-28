# Quick Start Guide - File Operations Feature

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

Open a terminal in the project directory and run:

```bash
pip install -r requirements_file_operations.txt
```

### Step 2: Start the Server

Start the proxy server (which includes file operations):

```bash
python proxy_server.py
```

You should see:
```
✅ File operations libraries loaded successfully
🚀 Starting AI Assistant Proxy Server with File Operations...
📁 Scratch directory: C:\Users\andyj\AI_assistant\scratch
```

### Step 3: Use the Feature

Open your AI assistant in the browser and try these commands:

**Read a file:**
```
"Read the content from example.txt"
```

**Write a file:**
```
"Write a summary to report.txt with the following content: This is a test summary"
```

**Read a Word document:**
```
"Read the document.docx file"
```

**Create an Excel spreadsheet:**
```
"Create a spreadsheet called data.xlsx with headers Name, Age, City and add a few rows"
```

## 📁 Scratch Directory

All files are stored in:
```
C:\Users\andyj\AI_assistant\scratch
```

You can access this directory directly to:
- View saved files
- Add files manually for the assistant to read
- Delete old files

## ✅ Verify Installation

### Test 1: Check Server is Running

Open your browser and go to:
```
http://localhost:8002/v1/files/list
```

You should see a JSON response with the file list.

### Test 2: Run Unit Tests

```bash
python test_file_operations.py
```

All tests should pass (green output).

### Test 3: Try a Simple Operation

1. Create a text file in the scratch directory manually:
   - Go to `C:\Users\andyj\AI_assistant\scratch`
   - Create a file called `test.txt` with some content

2. Ask the assistant: "Read the content from test.txt"

3. The assistant should display the content of your file

## 🔧 Troubleshooting

### Issue: "Module not found" error

**Solution:** Install dependencies
```bash
pip install -r requirements_file_operations.txt
```

### Issue: Server won't start

**Solution 1:** Check if port 8002 is already in use
- Kill any existing process on port 8002
- Or change the port in `proxy_server.py`

**Solution 2:** Check Python version
```bash
python --version
```
Requires Python 3.8 or higher

### Issue: File not found

**Solution:** Make sure the file is in the scratch directory
```
C:\Users\andyj\AI_assistant\scratch\your_file.txt
```

## 📊 Supported Formats

| Format | Extension | Read | Write |
|--------|-----------|------|-------|
| Text | .txt | ✅ | ✅ |
| Word | .docx | ✅ | ✅ |
| Excel | .xlsx | ✅ | ✅ |
| PDF | .pdf | ✅ | ✅ |
| Image | .png/.jpg | ✅ | ❌ |

## 💡 Usage Examples

### Example 1: Take Notes

**User:** "Remember to write this in a note: Meeting tomorrow at 3 PM with the team about project updates"

**Assistant:** Uses `writeFile` to save to `notes.txt`

### Example 2: Read Research Data

**User:** "Read the research data from analysis.xlsx"

**Assistant:** Uses `readFile` to extract spreadsheet data

### Example 3: Create Reports

**User:** "Create a report.docx with the following sections: Introduction, Findings, Conclusion"

**Assistant:** Uses `writeFile` to create a formatted Word document

### Example 4: Work with PDFs

**User:** "Read the content from report.pdf"

**Assistant:** Uses `readFile` to extract text from the PDF

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Start the server
3. ✅ Test with a simple file operation
4. 📖 Read the full documentation: `FILE_OPERATIONS_README.md`
5. 🧪 Run the test suite: `python test_file_operations.py`

## 🆘 Getting Help

For more detailed information, see:
- Full documentation: `FILE_OPERATIONS_README.md`
- API reference: See the "API Endpoints" section in the full docs
- Test examples: Check `test_file_operations.py` for code examples

## 🎉 You're Ready!

The file operations feature is now set up and ready to use. The assistant can now:
- Read documents you provide
- Create and save documents
- Work with multiple file formats
- Maintain persistent storage

Enjoy your enhanced AI assistant! 🚀

