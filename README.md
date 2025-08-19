📄 Brochure Generator
-------------
An AI-powered CLI tool that generates company brochures from their website content.
The tool crawls the company’s landing page (and relevant subpages), extracts useful text, and uses an LLM (via the OpenAI API) to create a professional, investor- and customer-ready brochure in Markdown format.

🚀 Features
---------------
🌐 Website Scraping – Fetches content from the provided company website.

🧠 AI Summarization – Uses an LLM (OpenAI) to analyze and summarize company details.

📄 Brochure Generation – Outputs structured Markdown brochures including company culture, products, customers, and careers.

⚡ Streaming Support – See the brochure generated in real-time as chunks arrive from the model.

🖥️ CLI Support – Run directly from the command line with a simple command.

▶️ Usage
-----------
Run the CLI tool with:

python create-brochure.py --company_name "Hugging Face" --url "https://huggingface.co"


Example output:

--- 📄 Brochure Output ---

Hugging Face Company Brochure

Welcome to Hugging Face

At Hugging Face, we are committed to building an AI community that shapes the future of machine learning..... 

🧑‍💻 Key Learnings
--------------------
🔑 Working with OpenAI Chat Completions API

🕸️ Extracting and processing webpage content with Python

📑 Structuring data into Markdown-formatted brochures

⚡ Handling streaming responses for real-time output

🛠️ Building modular project structures for scalability
