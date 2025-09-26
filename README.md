# AI-Powered Codebase Refactoring Agent (Gemini)

An intelligent codebase analysis and refactoring system that helps improve code quality, maintainability, and generates insights about your projects using Google's Gemini AI.

## Features

- **🔍 Codebase Analysis**: Analyzes code structure, complexity, and quality metrics
- **🤖 AI-Powered Insights**: Uses Google Gemini AI for intelligent code analysis and suggestions
- **✨ Code Refactoring**: Automated code improvements while preserving functionality
- **🌐 Multi-language Support**: Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, and more
- **🗺️ Repository Mapping**: Complete file tree analysis with metadata
- **🎙️ Interview Questions**: Generates technical interview questions based on code analysis
- **📊 Comprehensive Reports**: Detailed recommendations for codebase improvements
- **⚡ Rate Limit Management**: Built-in delays and retry logic for API stability

## Supported Languages

- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`, `.hpp`)
- C# (`.cs`)
- Go (`.go`)
- Rust (`.rs`)
- PHP (`.php`)
- Ruby (`.rb`)
- Swift (`.swift`)
- Kotlin (`.kt`)
- Scala (`.scala`)
- R (`.r`)
- HTML/CSS (`.html`, `.css`)
- Shell scripts (`.sh`)
- SQL (`.sql`)
- And many more...

## Installation

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd code-refactoring-agent
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Get your Gemini API key**:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

### Manual Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

## Usage

### Basic Usage

**Analyze a local codebase**:
```bash
python main.py /path/to/your/project
```

**Analyze a GitHub repository**:
```bash
python main.py https://github.com/username/repository.git
```

**Specify custom output directory**:
```bash
python main.py /path/to/project --output-dir my_refactored_code
```

### Model Selection

Choose between Gemini models based on your needs:

**Test your API key and find working models**:
```bash
python test_gemini_models.py
```

**Fast processing (recommended for most cases)**:
```bash
python main.py /path/to/project --model gemini-1.5-flash-latest
```

**Higher quality analysis and refactoring**:
```bash
python main.py /path/to/project --model gemini-1.5-pro-latest
```

### Rate Limit Management

**Adjust delay between API calls**:
```bash
python main.py /path/to/project --delay 5  # 5 seconds between calls
```

**Process only specific phases**:
```bash
python main.py /path/to/project --skip-refactoring  # Analysis only
python main.py /path/to/project --skip-analysis     # Refactoring only
```

### Advanced Options

**Get help**:
```bash
python main.py --help
```

**Complete example with all options**:
```bash
python main.py https://github.com/user/repo.git \
  --output-dir custom_output \
  --model gemini-1.5-pro-latest \
  --delay 3
```

## Output Structure

The tool generates several outputs in your specified directory:

```
refactored_codebase/
├── 📁 src/                          # Refactored source code
│   ├── 🐍 main.py                   # Improved Python files
│   └── 🟨 utils.js                  # Refactored JavaScript
├── 📝 CODEBASE_RECOMMENDATIONS.md   # Overall improvement suggestions
└── 📝 INTERVIEW_QUESTIONS.md        # Generated interview questions
```

## How It Works

1. **Analysis Phase**: 
   - Scans your codebase for supported file types
   - Analyzes each file for complexity, maintainability, and code smells
   - Generates detailed quality reports using Gemini AI

2. **Refactoring Phase**:
   - Applies AI-powered improvements to your code
   - Maintains original functionality while improving readability
   - Adds comments and documentation where appropriate

3. **Insights Generation**:
   - Creates overall codebase recommendations
   - Generates technical interview questions
   - Provides actionable improvement suggestions

## Configuration

### Environment Variables

You can customize the behavior using environment variables in your `.env` file:

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional model configuration
GEMINI_MODEL=gemini-1.5-flash-latest     # or gemini-1.5-pro-latest
GEMINI_TEMPERATURE=0.2                 # Creativity level (0.0-1.0)
GEMINI_MAX_RETRIES=3                   # API retry attempts
GEMINI_REQUEST_TIMEOUT=30              # Request timeout in seconds

# File processing limits
MAX_FILE_SIZE_FOR_REFACTORING=15000    # Max characters for refactoring
MAX_FILE_SIZE_FOR_ANALYSIS=12000       # Max characters for analysis
```

### Gemini Models Comparison

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `gemini-1.5-flash-latest` | ⚡ Fast | Good | General analysis, large codebases |
| `gemini-1.5-pro-latest` | 🐌 Slower | Excellent | Complex refactoring, detailed analysis |
| `gemini-pro` | ⚡ Fast | Good | Legacy model, stable |

### Ignored Patterns

The tool automatically ignores common directories and files:
- Version control: `.git`, `.svn`
- Dependencies: `node_modules`, `venv`, `__pycache__`
- Build outputs: `dist`, `build`, `target`
- IDE files: `.idea`, `.vscode`

## Troubleshooting

### Common Issues

**"GEMINI_API_KEY not found"**:
- Ensure your `.env` file exists and contains your API key
- Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

**"Rate limit exceeded" or "Quota exceeded"**:
- Increase the `--delay` parameter (try `--delay 5` or higher)
- Use `--skip-analysis` or `--skip-refactoring` to reduce API calls
- Check your Gemini API quota in Google AI Studio

**Model not found (404 error)**:
- Run `python test_gemini_models.py` to check available models
- Use `gemini-1.5-flash-latest` or `gemini-pro` instead
- Your API key might not have access to newer models
**"Git command not found"**:
- Install Git: [https://git-scm.com/downloads](https://git-scm.com/downloads)
- Ensure Git is in your system PATH

**Large files being skipped**:
- Files over 15KB are copied without refactoring
- Files over 12KB are truncated for analysis
- This prevents API token limit issues

### Performance Tips

1. **For large codebases**:
   - Start with `--skip-refactoring` to get analysis results quickly
   - Use `gemini-1.5-flash-latest` for faster processing
   - Run `python test_gemini_models.py` first to find working models
   - Increase `--delay` to avoid rate limits

2. **For detailed analysis**:
   - Use `gemini-1.5-pro-latest` for better quality
   - Process smaller codebases or specific directories
   - Use `--skip-analysis` if you only need refactored code

3. **Rate limit management**:
   - The tool automatically adds delays between requests
   - Implements exponential backoff for retries
   - Monitors for rate limit responses

## API Limits and Pricing

- **Gemini 1.5 Flash**: Fast and efficient, generous free tier
- **Gemini 1.5 Pro**: More capable, limited free requests per minute
- Check current limits at: [Google AI Studio](https://aistudio.google.com/)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Google Gemini AI](https://ai.google.dev/) for powerful code analysis
- Uses the latest Gemini 1.5 models for optimal performance
- Designed with rate limiting and error handling for production use

## Roadmap

- [ ] Support for more programming languages
- [ ] Custom refactoring rules and templates
- [ ] Integration with popular IDEs
- [ ] Batch processing for multiple repositories
- [ ] Web-based interface
- [ ] Custom analysis rules
- [ ] Team collaboration features

## Support

For issues, feature requests, or questions:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include error messages and your configuration

**Common support scenarios**:
- Rate limiting issues → Adjust `--delay` parameter
- Large codebases → Use `--skip-analysis` or `--skip-refactoring`
- API errors → Check your Gemini API key and quota
- Installation issues → Run `python setup.py` again

## Version History

- **v2.0.0**: Migrated to Google Gemini AI with improved rate limiting
- **v1.0.0**: Initial release with Groq API support