import argparse
import os
import json
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI
import gradio as gr

load_dotenv(override=True)

api_key= os.getenv('OPENAI_API_KEY')

if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    print("API key found and looks good so far!")

openai = OpenAI()
MODEL = 'gpt-4o-mini'


# Some websites need you to use proper headers when fetching them:
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

#This class downloads a webpage, removes unnecessary elements, and extracts clean, readable text along with the title
class Website:
 def __init__(self,url):
#1.Fetch Webpage
#Uses the requests library to download the webpage content.
#headers=headers is optional but often used to mimic a real browser (so some websites don’t block the request).

     self.url = url
     response = requests.get(url, headers=headers)

#2.Parse HTML with BeautifulSoup
     soup = BeautifulSoup(requests.get(self.url).content, "html.parser")
     self.title = soup.title.string if soup.title else "No title found"

#3.Remove Irrelevant Elements and Extract clean text
     if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True) #adds newlines between different blocks of text and removes leading/trailing spaces from each line
     else:
            self.text = ""
            #finds all <a> tags in the HTML (these are usually hyperlinks).
            #For each <a> tag, link.get('href') extracts the value of the href attribute (the actual link)
     links = [link.get('href') for link in soup.find_all('a')]
     self.links = [link for link in links if link]

 def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to include in a brochure about the company, \
such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
link_system_prompt += "You should respond in JSON as in this example:"
link_system_prompt += """
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""
#The above example is a single shot prompt.

def link_user_prompt_for(website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt



def messages_for(website):
    return [
        {"role": "system", "content": link_system_prompt},
        {"role": "user", "content": link_user_prompt_for(website)}
    ]

def get_useful_links(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model=MODEL,
        messages= messages_for(website),
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)



#Make the brochure
def get_all_details(url):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_useful_links(url)
    # print("Found links:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result

brochure_system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
Include details of company culture, customers and careers/jobs if you have the information."

def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:10_000] # Truncate if more than 10,000 characters
    return user_prompt

#print the data chunk by chunk and will not wait for full response to be printed at the same time.
def create_brochure(company_name, url):
        stream = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": brochure_system_prompt},
                {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
            ],
            stream=True
        )

        response = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                response += content
                yield response


with gr.Blocks() as demo:
    gr.Markdown("## 📄 Company Brochure Generator")

    with gr.Row():
        url_input = gr.Textbox(label="Enter Website URL")
        company_input = gr.Textbox(label="Enter Company Name")

    output = gr.Markdown(label="Generated Brochure")

    generate_btn = gr.Button("Generate Brochure")
    generate_btn.click(fn=create_brochure, inputs=[company_input, url_input], outputs=output, queue = True)

demo.launch()
