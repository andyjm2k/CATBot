# File Operations Feature

## Overview

The File Operations feature enables the AI assistant to read and write files in various formats from a local scratch directory. This provides persistent storage capabilities without breaking existing functionality.

## Supported File Formats

### Reading Support
- **Text Files (.txt)**: Plain text files with UTF-8 encoding
- **Word Documents (.docx)**: Microsoft Word documents
- **Excel Spreadsheets (.xlsx, .xls)**: Microsoft Excel files
- **PDF Documents (.pdf)**: Portable Document Format files
- **Images (.png, .jpg, .jpeg)**: Image files with metadata extraction

### Writing Support
- **Text Files (.txt)**: Plain text files
- **Word Documents (.docx)**: Microsoft Word documents with automatic paragraph formatting
- **Excel Spreadsheets (.xlsx)**: Excel files with auto-formatting and column width adjustment
- **PDF Documents (.pdf)**: PDF files with text content

## Architecture

The feature is integrated into the existing proxy server:

### 1. Python Backend Server (`proxy_server.py`)
- FastAPI-based REST API server
- Runs on port 8002 (same as existing proxy server)
- Handles all file I/O operations
- Manages the scratch directory
- No separate server needed!

### 2. Frontend Integration (`index-dev.html`)
- Two new tools: `readFile` and `writeFile`
- JavaScript handlers that communicate with the proxy server
- Integrated into the existing tool system

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements_file_operations.txt
```

This will install:
- python-docx (Word document support)
- openpyxl (Excel file support)
- PyPDF2 (PDF reading)
- reportlab (PDF writing)
- Pillow (Image processing)

### 2. Start the Proxy Server

```bash
python proxy_server.py
```

The server will start on `http://localhost:8002` with file operations included.

### 3. Verify the Server is Running

Open your browser and navigate to:
```
http://localhost:8002/v1/files/list
```

You should see a JSON response with the list of files in the scratch directory.

## Usage

### Using the readFile Tool

The assistant can read files from the scratch directory by using the `readFile` tool:

**Example 1: Read a text file**
```
User: "Read the content from notes.txt"
Assistant: <tool>readFile</tool>
<parameters>
{
    "filename": "notes.txt"
}
</parameters>
```

**Example 2: Read a Word document**
```
User: "Read the report.docx file"
Assistant: <tool>readFile</tool>
<parameters>
{
    "filename": "report.docx"
}
</parameters>
```

**Example 3: Read an Excel spreadsheet**
```
User: "Read the data from sales.xlsx"
Assistant: <tool>readFile</tool>
<parameters>
{
    "filename": "sales.xlsx"
}
</parameters>
```

### Using the writeFile Tool

The assistant can write files to the scratch directory by using the `writeFile` tool:

**Example 1: Write a text file**
```
User: "Save this summary to summary.txt"
Assistant: <tool>writeFile</tool>
<parameters>
{
    "filename": "summary.txt",
    "content": "This is the summary content...",
    "format": "txt"
}
</parameters>
```

**Example 2: Write a Word document**
```
User: "Create a report.docx with this content"
Assistant: <tool>writeFile</tool>
<parameters>
{
    "filename": "report.docx",
    "content": "Executive Summary\n\nKey Findings:\n1. ...\n2. ...",
    "format": "docx"
}
</parameters>
```

**Example 3: Write an Excel spreadsheet**
```
User: "Save this data to data.xlsx"
Assistant: <tool>writeFile</tool>
<parameters>
{
    "filename": "data.xlsx",
    "content": "Name\tAge\tCity\nJohn\t30\tNew York\nJane\t25\tLos Angeles",
    "format": "xlsx"
}
</parameters>
```

**Example 4: Write a PDF document**
```
User: "Create a PDF report"
Assistant: <tool>writeFile</tool>
<parameters>
{
    "filename": "report.pdf",
    "content": "Annual Report\n\nThis document contains...",
    "format": "pdf"
}
</parameters>
```

## Scratch Directory

The scratch directory is located at:
```
C:/Users/andyj/AI_assistant/scratch
```

This directory:
- Is automatically created if it doesn't exist
- Has full read/write permissions
- Is isolated from other system files
- Can be manually accessed by the user at any time

## API Endpoints

### POST /v1/files/read
Read a file from the scratch directory

**Request Body:**
```json
{
    "filename": "example.txt"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Successfully read example.txt",
    "data": {
        "content": "File content here...",
        "type": "text"
    }
}
```

### POST /v1/files/write
Write content to a file in the scratch directory

**Request Body:**
```json
{
    "filename": "example.txt",
    "content": "Content to write...",
    "format": "txt"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Successfully wrote example.txt",
    "data": {
        "filepath": "C:/Users/andyj/AI_assistant/scratch/example.txt",
        "size": 1234
    }
}
```

### GET /v1/files/list
List all files in the scratch directory

**Response:**
```json
{
    "success": true,
    "count": 3,
    "files": [
        {
            "name": "example.txt",
            "size": 1234,
            "modified": 1234567890.0,
            "extension": ".txt"
        }
    ],
    "scratch_dir": "C:/Users/andyj/AI_assistant/scratch"
}
```

### DELETE /v1/files/delete/{filename}
Delete a file from the scratch directory

## Testing

Run the unit tests to verify the file operations are working correctly:

```bash
python test_file_operations.py
```

The test suite covers:
- Reading and writing text files
- Reading and writing Word documents
- Reading and writing Excel spreadsheets
- Reading and writing PDF files
- Reading image files
- Special character handling
- Roundtrip tests (write then read back)
- Error handling

Test coverage: 70%+ of methods

## Troubleshooting

### Server Won't Start

**Problem:** `ModuleNotFoundError: No module named 'docx'` or similar

**Solution:** Install the required dependencies:
```bash
pip install -r requirements_file_operations.txt
```

### File Not Found Error

**Problem:** The assistant reports that a file cannot be found

**Solution:** 
1. Verify the file exists in the scratch directory
2. Check the filename is correct (including extension)
3. Make sure the file is in `C:/Users/andyj/AI_assistant/scratch`

### Server Connection Error

**Problem:** The frontend reports "Make sure the proxy server is running on port 8002"

**Solution:**
1. Start the server: `python proxy_server.py`
2. Verify the server is running: Open `http://localhost:8002/v1/files/list` in a browser
3. Check if another application is using port 8002

### PDF Writing Error

**Problem:** "PDF writing requires reportlab library"

**Solution:** Install reportlab:
```bash
pip install reportlab
```

## Security Considerations

1. **Isolated Directory**: All file operations are restricted to the scratch directory
2. **Path Validation**: The server prevents directory traversal attacks
3. **Local Only**: The server only accepts connections from localhost (127.0.0.1)
4. **No Arbitrary Execution**: Files are read/written as data only, never executed

## Future Enhancements

Possible improvements for future versions:

1. **Additional Format Support**:
   - CSV files with pandas
   - JSON files
   - XML files
   - Markdown files

2. **File Management**:
   - File search functionality
   - Batch operations
   - File versioning
   - Automatic backups

3. **Advanced Features**:
   - OCR for image-to-text conversion
   - Document format conversion
   - File compression/decompression
   - Encryption/decryption

4. **User Interface**:
   - File browser in the web interface
   - Drag-and-drop file upload
   - File preview functionality

## Compatibility

- **Python Version**: 3.8 or higher
- **Operating Systems**: Windows, macOS, Linux
- **Browser Requirements**: Modern browsers with fetch API support
- **Dependencies**: See `requirements_file_operations.txt`

## Contributing

When making changes to the file operations feature:

1. Update the unit tests if adding new functionality
2. Maintain at least 70% test coverage
3. Update this documentation
4. Test with all supported file formats
5. Verify existing features are not broken

## License

This feature is part of the AI Assistant project and follows the same license terms.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the test output for specific error messages
3. Check the server logs for detailed error information
4. Verify all dependencies are installed correctly

## Changelog

### Version 1.0.0 (Initial Release)
- Read support for txt, docx, xlsx, pdf, png
- Write support for txt, docx, xlsx, pdf
- RESTful API with FastAPI
- Integration with existing tool system
- Comprehensive unit tests
- Full documentation

