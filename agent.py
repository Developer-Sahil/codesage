# /code-refactoring-agent/agent.py

import os
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from utils import extract_code_from_markdown
from config import Config
import openai
import anthropic
from groq import Groq


class RefactoringAgent:
    """
    An agent that analyzes and refactors a codebase using Google's Gemini API.
    """
    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.analysis_results = []
        
        # Configure Gemini API
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=Config.GEMINI_MODEL,
            generation_config=Config.GEMINI_GENERATION_CONFIG,
            safety_settings=Config.GEMINI_SAFETY_SETTINGS
        )

    def _call_model_api(self, prompt: str, system_prompt: str) -> str:
        model = Config.GEMINI_MODEL

        # =====================
        # 🧠 GEMINI
        # =====================
        if "gemini" in model:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            response = self.model.generate_content(
                f"{system_prompt}\n\nUser Request:\n{prompt}",
                request_options={"timeout": Config.GEMINI_REQUEST_TIMEOUT}
            )
            return response.text

        # =====================
        # 🧠 GPT-4o (OpenAI)
        # =====================
        elif "gpt" in model:
            openai.api_key = Config.OPENAI_API_KEY
            response = openai.chat.completions.create(
                model=model,  # "gpt-4o" or "gpt-4-turbo"
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content

        # =====================
        # 🧠 Claude (Anthropic)
        # =====================
        elif "claude" in model:
            client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            response = client.messages.create(
                model=model,  # e.g. "claude-3-sonnet-20240229"
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        # =====================
        # 🧠 Grok / Groq API
        # =====================
        elif "grok" in model:
            client = Groq(api_key=Config.GROQ_API_KEY)
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content

        else:
            raise ValueError(f"❌ Unsupported model: {model}")

    

    def _is_supported_file(self, file_name: str) -> bool:
        """Check if a file has a supported extension."""
        return Config.is_supported_file(file_name)

    def analyze_code(self, file_path: str, code_content: str) -> str:
        """Analyzes a single code file for metrics and code smells."""
        print(f"\n🔍 Analyzing: {file_path}")
        
        # Truncate very long files to prevent API limits
        if len(code_content) > Config.MAX_FILE_SIZE_FOR_ANALYSIS:
            code_content = code_content[:Config.MAX_FILE_SIZE_FOR_ANALYSIS] + "\n... (file truncated for analysis)"
            
        prompt = f"""
        Analyze the following code from the file '{file_path}':

        ```
        {code_content}
        ```

        Provide the following metrics and analysis:
        1. **Code Complexity:** Give a qualitative assessment (e.g., Low, Medium, High) and explain why.
        2. **Maintainability:** Score it from 1-10 (1=very difficult, 10=very easy) and justify your score.
        3. **Code Smells:** List up to 3 major code smells you identify (e.g., long method, duplicate code, large class).
        4. **Brief Summary:** A one-sentence summary of the code's purpose and quality.
        """
        analysis = self._call_model_api(prompt, Config.ANALYSIS_SYSTEM_PROMPT)
        print("✅ Analysis complete.")
        return analysis

    def refactor_code(self, file_path: str, code_content: str) -> str:
        """Refactors a single code file for clarity and best practices."""
        print(f"✨ Refactoring: {file_path}")
        
        # Skip refactoring for very large files to prevent issues
        if len(code_content) > Config.MAX_FILE_SIZE_FOR_REFACTORING:
            print(f"⚠️ File {file_path} is too large for refactoring. Copying original.")
            return code_content
            
        prompt = f"""
        Refactor the following code from the file '{file_path}'.
        Return ONLY the complete, refactored code inside a single markdown code block. Do not add any explanations before or after the code block.

        Original Code:
        ```
        {code_content}
        ```
        """
        refactored_content = self._call_model_api(prompt, Config.REFACTORING_SYSTEM_PROMPT)
        extracted_code = extract_code_from_markdown(refactored_content)
        
        # If extraction failed or returned empty, use original code
        if not extracted_code or extracted_code.startswith("Error:"):
            print(f"⚠️ Refactoring failed for {file_path}. Using original code.")
            return code_content
            
        print("✅ Refactoring complete.")
        return extracted_code

    def run(self):
        """
        The main method to walk the file tree and orchestrate the analysis and refactoring.
        """
        print(f"🚀 Starting codebase processing for: {self.source_dir}")
        print(f"💾 Output will be saved to: {self.output_dir}")
        print(f"🤖 Using LLM model: {Config.GEMINI_MODEL}")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        processed_files = 0
        
        for root, dirs, files in os.walk(self.source_dir, topdown=True):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if not Config.should_ignore(d)]

            for file in files:
                if self._is_supported_file(file) and not Config.should_ignore(file):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.source_dir)

                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            original_code = f.read()
                        
                        if not original_code.strip():
                            print(f"\n🟡 Skipping empty file: {relative_path}")
                            continue

                        # 1. Analyze the code
                        analysis = self.analyze_code(relative_path, original_code)
                        self.analysis_results.append(f"File: {relative_path}\n{analysis}\n")
                        print("--- Analysis Report ---")
                        print(analysis)
                        print("-----------------------\n")
                        
                        # Small delay to respect rate limits
                        time.sleep(1)
                        
                        # 2. Refactor the code
                        refactored_code = self.refactor_code(relative_path, original_code)

                        # 3. Save the refactored code
                        output_file_path = os.path.join(self.output_dir, relative_path)
                        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                        with open(output_file_path, 'w', encoding='utf-8') as f:
                            f.write(refactored_code)
                        print(f"💾 Refactored file saved to: {output_file_path}")
                        
                        processed_files += 1
                        
                        # Small delay between files to respect rate limits
                        time.sleep(2)

                    except Exception as e:
                        print(f"❌ Error processing file {file_path}: {e}")
        
        print(f"\n📊 Processing complete! {processed_files} files processed.")
        
        if processed_files > 0:
            self.generate_overall_recommendations()
        else:
            print("⚠️ No supported code files found for processing.")

    def generate_overall_recommendations(self):
        """Generates high-level recommendations for the entire codebase."""
        print("\n\n" + "="*50)
        print("💡 Generating Overall Codebase Recommendations...")
        print("="*50)

        if not self.analysis_results:
            print("No files were analyzed, so no recommendations can be generated.")
            return

        summary_of_analyses = "\n".join(self.analysis_results)
        
        # Split into chunks if too long
        max_chunk_size = 20000  # Conservative limit for Gemini
        if len(summary_of_analyses) > max_chunk_size:
            summary_of_analyses = summary_of_analyses[:max_chunk_size] + "\n... (analysis truncated due to length)"
        
        prompt = f"""
        Here are the analysis reports for several files in a codebase:
        ---
        {summary_of_analyses}
        ---
        Based on these reports, please provide a high-level summary and actionable recommendations for the entire project.
        Focus on patterns you observe (e.g., inconsistent styling, lack of documentation, high complexity in multiple modules).
        Structure your response with:
        1. **Overall Summary:** A brief paragraph about the general state of the codebase.
        2. **Key Recommendations:** A bulleted list of the top 3-5 most impactful recommendations.
        """
        recommendations = self._call_model_api(prompt, Config.RECOMMENDATIONS_SYSTEM_PROMPT)
        print(recommendations)
        
        # Save recommendations to a file
        recommendations_path = os.path.join(self.output_dir, "CODEBASE_RECOMMENDATIONS.md")
        with open(recommendations_path, 'w', encoding='utf-8') as f:
            f.write("# Codebase Recommendations\n\n")
            f.write(recommendations)
        print(f"\n💾 Overall recommendations saved to: {recommendations_path}")

    def generate_interview_questions(self):
        """
        Generates interview questions based on the codebase analysis.
        """
        print("\n\n" + "="*50)
        print("🎙️ Generating Interview Questions...")
        print("="*50)

        if not self.analysis_results:
            print("No files were analyzed, so no questions can be generated.")
            return

        summary_of_analyses = "\n".join(self.analysis_results)
        
        # Split into chunks if too long
        max_chunk_size = 20000  # Conservative limit for Gemini
        if len(summary_of_analyses) > max_chunk_size:
            summary_of_analyses = summary_of_analyses[:max_chunk_size] + "\n... (analysis truncated due to length)"
        
        prompt = f"""
        Here are analysis reports for several files from a candidate's codebase:
        ---
        {summary_of_analyses}
        ---
        Based on these reports, generate a set of 5-7 interview questions. The questions should be:
        1. **Conceptual:** Ask about the architectural choices, design patterns, or high-level decisions.
        2. **Code-Specific:** Refer to potential issues (like high complexity or code smells) and ask how the candidate would justify or improve them.
        3. **Refactoring-Oriented:** Propose a hypothetical new requirement and ask how they would adapt the existing code.
        
        Format the output clearly with headings for each question.
        """
        questions = self._call_model_api(prompt, Config.INTERVIEW_QUESTIONS_SYSTEM_PROMPT)
        print(questions)
        
        # Save questions to a file
        questions_path = os.path.join(self.output_dir, "INTERVIEW_QUESTIONS.md")
        with open(questions_path, 'w', encoding='utf-8') as f:
            f.write("# Interview Questions\n\n")
            f.write(questions)
        print(f"\n💾 Interview questions saved to: {questions_path}")