#!/usr/bin/env python3
"""
Flask web application for the AI-Powered Codebase Refactoring Agent.
This provides a web UI for the refactoring agent with download functionality.
Cloud Run compatible version.
"""

import os
import sys
import time
import shutil
import threading
import zipfile
from io import BytesIO
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

from agent import RefactoringAgent
from utils import is_git_repo, clone_repo, validate_source_directory
from config import Config

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Global state for tracking progress
processing_state = {
    'active': False,
    'progress': 0,
    'files_processed': 0,
    'files_analyzed': 0,
    'files_refactored': 0,
    'current_file': '',
    'status': 'idle',
    'logs': [],
    'error': None,
    'temp_dir': None,
    'output_dir': None,
    'recommendations': None,
    'interview_questions': None,
    'processed_files': []
}

def add_log(message, log_type='info'):
    """Add a log entry to the processing state."""
    processing_state['logs'].append({
        'message': message,
        'type': log_type,
        'timestamp': time.strftime('%H:%M:%S')
    })

def create_zip_file(source_dir):
    """Create a ZIP file from the output directory."""
    memory_file = BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
    
    memory_file.seek(0)
    return memory_file

def run_refactoring_task(source_path, output_dir, model, skip_analysis, skip_refactoring, delay):
    """Run the refactoring task in a background thread."""
    temp_dir = None
    
    try:
        processing_state['active'] = True
        processing_state['status'] = 'running'
        processing_state['error'] = None
        processing_state['logs'] = []
        processing_state['output_dir'] = output_dir
        processing_state['recommendations'] = None
        processing_state['interview_questions'] = None
        processing_state['processed_files'] = []
        
        add_log('🚀 Starting codebase processing...', 'info')
        
        # Validate API key
        if not Config.validate():
            add_log('❌ Error: GEMINI_API_KEY not found', 'error')
            processing_state['error'] = 'API key not configured'
            processing_state['status'] = 'error'
            return
        
        # Handle GitHub repository URLs
        if is_git_repo(source_path):
            add_log(f'🔄 Cloning repository: {source_path}', 'info')
            temp_dir = clone_repo(source_path)
            if not temp_dir:
                add_log('❌ Failed to clone repository', 'error')
                processing_state['error'] = 'Failed to clone repository'
                processing_state['status'] = 'error'
                return
            source_path = temp_dir
            processing_state['temp_dir'] = temp_dir
            add_log('✅ Repository cloned successfully', 'success')
        
        # Validate source directory
        if not validate_source_directory(source_path):
            add_log('❌ Invalid source directory', 'error')
            processing_state['error'] = 'Invalid source directory'
            processing_state['status'] = 'error'
            return
        
        add_log(f'📂 Source: {source_path}', 'info')
        add_log(f'💾 Output: {output_dir}', 'info')
        add_log(f'🤖 Model: {model}', 'info')
        
        # Clean up existing output directory
        if os.path.exists(output_dir):
            add_log(f'🧹 Cleaning output directory', 'info')
            shutil.rmtree(output_dir)
        
        # Create agent with custom configuration
        Config.GEMINI_MODEL = model
        agent = RefactoringAgent(source_path, output_dir)
        
        # Override agent's run method to track progress
        original_analyze = agent.analyze_code
        original_refactor = agent.refactor_code
        
        def tracked_analyze(file_path, code_content):
            processing_state['current_file'] = file_path
            add_log(f'🔍 Analyzing: {file_path}', 'info')
            result = original_analyze(file_path, code_content)
            processing_state['files_analyzed'] += 1
            processing_state['processed_files'].append({
                'name': os.path.basename(file_path),
                'path': file_path,
                'icon': Config.get_file_icon(os.path.splitext(file_path)[1])
            })
            time.sleep(delay)
            return result
        
        def tracked_refactor(file_path, code_content):
            add_log(f'✨ Refactoring: {file_path}', 'info')
            result = original_refactor(file_path, code_content)
            processing_state['files_refactored'] += 1
            processing_state['files_processed'] += 1
            time.sleep(delay)
            return result
        
        agent.analyze_code = tracked_analyze
        agent.refactor_code = tracked_refactor
        
        # Run the agent
        add_log('⚙️ Processing files...', 'info')
        agent.run()
        
        # Read recommendations if available
        recommendations_path = os.path.join(output_dir, "CODEBASE_RECOMMENDATIONS.md")
        if os.path.exists(recommendations_path):
            add_log('📖 Reading recommendations...', 'info')
            with open(recommendations_path, 'r', encoding='utf-8') as f:
                processing_state['recommendations'] = f.read()
        
        # Generate interview questions if analysis was performed
        if not skip_analysis and agent.analysis_results:
            add_log('🎙️ Generating interview questions...', 'info')
            agent.generate_interview_questions()
            
            # Read interview questions
            questions_path = os.path.join(output_dir, "INTERVIEW_QUESTIONS.md")
            if os.path.exists(questions_path):
                with open(questions_path, 'r', encoding='utf-8') as f:
                    processing_state['interview_questions'] = f.read()
        
        processing_state['progress'] = 100
        processing_state['status'] = 'completed'
        add_log('🎉 Processing complete!', 'success')
        add_log('📦 Ready for download', 'success')
        
    except Exception as e:
        add_log(f'❌ Error: {str(e)}', 'error')
        processing_state['error'] = str(e)
        processing_state['status'] = 'error'
        
    finally:
        processing_state['active'] = False
        
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            add_log('🧹 Cleaning up temporary files', 'info')
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                add_log(f'⚠️ Warning: Could not clean up temp directory: {e}', 'warning')

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for Cloud Run."""
    return jsonify({'status': 'healthy', 'api_configured': bool(Config.GEMINI_API_KEY)}), 200

@app.route('/api/start', methods=['POST'])
def start_refactoring():
    """Start the refactoring process."""
    if processing_state['active']:
        return jsonify({'error': 'A task is already running'}), 400
    
    data = request.json
    source_path = data.get('sourcePath', '').strip()
    output_dir = data.get('outputDir', 'refactored_codebase')
    model = data.get('model', 'gemini-2.5-flash-lite')
    skip_analysis = data.get('skipAnalysis', False)
    skip_refactoring = data.get('skipRefactoring', False)
    delay = int(data.get('delay', 2))
    
    if not source_path:
        return jsonify({'error': 'Source path is required'}), 400
    
    # Reset state
    processing_state['progress'] = 0
    processing_state['files_processed'] = 0
    processing_state['files_analyzed'] = 0
    processing_state['files_refactored'] = 0
    processing_state['current_file'] = ''
    
    # Start background thread
    thread = threading.Thread(
        target=run_refactoring_task,
        args=(source_path, output_dir, model, skip_analysis, skip_refactoring, delay)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Processing started', 'status': 'started'})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current processing status."""
    return jsonify({
        'active': processing_state['active'],
        'progress': processing_state['progress'],
        'files_processed': processing_state['files_processed'],
        'files_analyzed': processing_state['files_analyzed'],
        'files_refactored': processing_state['files_refactored'],
        'current_file': processing_state['current_file'],
        'status': processing_state['status'],
        'logs': processing_state['logs'],
        'error': processing_state['error'],
        'recommendations': processing_state['recommendations'],
        'interview_questions': processing_state['interview_questions'],
        'processed_files': processing_state['processed_files']
    })

@app.route('/api/download', methods=['GET'])
def download_refactored_code():
    """Download the refactored codebase as a ZIP file."""
    output_dir = processing_state.get('output_dir')
    
    if not output_dir or not os.path.exists(output_dir):
        return jsonify({'error': 'No refactored code available for download'}), 404
    
    try:
        # Create ZIP file in memory
        memory_file = create_zip_file(output_dir)
        
        # Generate filename with timestamp
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f'refactored_codebase_{timestamp}.zip'
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'Failed to create download: {str(e)}'}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get the current configuration."""
    return jsonify({
        'api_key_configured': bool(Config.GEMINI_API_KEY),
        'model': Config.GEMINI_MODEL,
        'supported_extensions': list(Config.SUPPORTED_EXTENSIONS),
        'models': [
            'gemini-2.5-flash-lite',
            'gemini-1.5-flash-8b',
            'gemini-pro'
        ]
    })

def main():
    """Run the Flask application."""
    # Get port from environment variable (Cloud Run sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Check if running on Cloud Run
    is_cloud_run = os.environ.get('K_SERVICE') is not None
    
    if is_cloud_run:
        print("🌐 Running on Google Cloud Run")
        print(f"📍 Port: {port}")
        print(f"🔑 API Key configured: {bool(Config.GEMINI_API_KEY)}")
    else:
        print("=" * 60)
        print("🚀 AI Codebase Refactoring Agent - Web Interface")
        print("=" * 60)
        print(f"\n📍 Server starting on http://localhost:{port}")
        print("🔑 Make sure GEMINI_API_KEY is set in your .env file")
        print(f"\n🌐 Open your browser and navigate to: http://localhost:{port}")
        print("\n📦 Features:")
        print("  • Real-time progress tracking")
        print("  • Download refactored code as ZIP")
        print("  • View recommendations and interview questions")
        print("\nPress Ctrl+C to stop the server\n")
    
    # Run with different settings based on environment
    app.run(
        debug=not is_cloud_run,
        host='0.0.0.0',
        port=port,
        use_reloader=False
    )

if __name__ == '__main__':
    main()