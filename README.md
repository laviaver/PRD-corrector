# PRD Reviewer

AI-powered Product Requirements Document (PRD) analysis and review tool.

## 🚀 Quick Start

### One-Command Launch

```bash
./start.sh
```

This will:
- ✅ Check and install dependencies
- ✅ Start backend server (http://localhost:8000)
- ✅ Start frontend server (http://localhost:5173)
- ✅ Show logs and status

### Run backend only

If you need to start just the backend (e.g. for API work):

```bash
./start.sh   # starts both backend + frontend
```

Or run the backend by itself:

```bash
./backend/run.sh
```

Or manually (from `backend/` with venv activated):

```bash
cd backend && source venv/bin/activate
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

> **If you get "uvicorn: command not found"** — do not run `uvicorn` directly. Use `python -m uvicorn` (or `python3 -m uvicorn`) as above, or use `./backend/run.sh`.

### Manual setup (full)

See [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) for detailed setup instructions.

## 📋 Features

### ✅ Implemented (MVP + Enhanced)

- **File Upload & Text Paste**: Support for .txt, .md, .docx files
- **AI-Powered Analysis**: OpenAI GPT-4 integration for PRD review
- **Suggestion Viewing**: Categorized, prioritized suggestions with details
- **Export Functionality**: Markdown, JSON, PDF export
- **Interactive Editor**: Edit PRD content with auto-save
- **Best Practices Library**: Browseable PRD best practices
- **Comparison Mode**: Compare PRDs against templates

### ⏸️ Planned (Require Database/Auth)

- Version History
- Team Collaboration
- Custom Best Practices

## 📁 Project Structure

```
PRD-corrector/
├── backend/          # FastAPI backend
├── frontend/         # React TypeScript frontend
├── specs/            # Specifications and documentation
├── start.sh          # Launch script
└── IMPLEMENTATION_STATUS.md  # Detailed status
```

## 🔧 Requirements

- Python 3.11+
- Node.js 18+
- OpenAI API key

## 📚 Documentation

- **Implementation Status**: [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)
- **Quickstart Guide**: [specs/002-prd-reviewer/quickstart.md](./specs/002-prd-reviewer/quickstart.md)
- **API Documentation**: http://localhost:8000/docs (when running)

## 🎯 Current Status

- **Completed**: 98/122 tasks (80%)
- **MVP**: ✅ Complete
- **Enhanced Features**: ✅ Complete
- **Production Ready**: ⏸️ Testing phase

## 📝 License

[Add your license here]

---

**Last Updated**: 2024-12-19
