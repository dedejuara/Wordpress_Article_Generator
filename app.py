import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import openai
import time
import re
import replicate
import os
import io
import base64
import random
from PIL import Image
import pandas as pd
import gradio as gr
from io import BytesIO
import csv
from io import StringIO

def split_article(article_text):
    words = article_text.split()    
    total_words = len(words)
    split_points = [total_words // 4, total_words // 2, (3 * total_words) // 4]

    first_quarter = ' '.join(words[:split_points[0]])
    second_quarter = ' '.join(words[split_points[0]:split_points[1]])
    third_quarter = ' '.join(words[split_points[1]:split_points[2]])
    fourth_quarter = ' '.join(words[split_points[2]:])

    return first_quarter, second_quarter, third_quarter, fourth_quarter

def replace_content(content, replacements):
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)
    return content

def generate_patterns(base_replacements):
    patterns = {}
    for key, value in base_replacements.items():
        patterns[key] = value
        patterns[key.capitalize()] = value.capitalize()
        patterns[key.upper()] = value.upper()
        patterns[key.lower()] = value.lower()
    return patterns

base_replacements = {
    'Layanan Pelanggan': 'Customer Service',
    'Pusat Kontak': 'Contact Center',
    'Multi Kanal': 'Omnichannel',
    'Saluran Omni': 'Omnichannel',
    'Merek':'Brand',
    'Komputasi Awan':'Cloud Computing',
    'Kecerdasan Buatan':'Artificial Intelligence',
    'Pembelajaran Mesin':'Machine Learning',
    'Alat Layanan Pelanggan':'Customer Service Tools',
    'Pengalaman Pelanggan':'Customer Experience',
    'AI Percakapan':'AI Conversation',
    'Aplikasi pesan':'Message app',
    'Visi Komputer':'Computer Vision'
}

def get_openai_response(messages, api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )
    finish_reason = response['choices'][0]['finish_reason']
    if finish_reason == 'length' or finish_reason == 'stop':
        return response['choices'][0]['message']['content']

def get_azure_response(messages, api_key, azure_api_base):
    openai.api_type = "azure"
    openai.api_version = "2023-05-15" 
    openai.api_base = azure_api_base 
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo", 
        messages=messages,
        temperature = 0
    )
    finish_reason = response['choices'][0]['finish_reason']
    if finish_reason == 'length' or finish_reason == 'stop':
        return response['choices'][0]['message']['content']
        
def cek_url(url):
    with open("log_activity.txt", 'r') as file:
        scraped_urls = set(url.strip() for url in file.readlines())

    if url in scraped_urls:
        return True
    else:
        scraped_urls.add(url)
        return False

def scrap_portal(queri):
    api_key = 'AIzaSyDJUWVZG2oHkHSsYoqdqgUZwQC2Aa2kSok'
    search_engine_id = 'a0dc878459ceb4811'
    num_pages = 3
    type = random.choice([' articles',' news',' trends',' technologies', ' future'])
    link = []
    query = queri + type

    for page in range(num_pages):
        start_index = page * 10 + 1
        url = f'https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}&start={start_index}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            for item in data['items']:
                url = item['link']
                link.append(url)
        else:
            print(f"Permintaan halaman {page + 1} gagal. Kode status:", response.status_code)
    filter_link1 = [url for url in link if "categories" not in url and "tags" not in url]
    filter_link2 = [url for url in filter_link1 if "help" not in url]
    return filter_link2
        
def clean_scrap(artikel,models,api_key,azure_api_base,keyword):
    new_artikel = []
    article = []
    if len(artikel) > 1:
        for art in artikel:
            messages=[
                {"role": "system", "content": "You are a very professional article editor."},
                {"role": "user", "content": "I have a raw article that contains a lot of unnecessary data such as ads, website information, and article publishers, as well as links to other pages, and so on. Please clean up the article I provided so that only the article's content remains. \nThen, you should also summarize the article so that it does not exceed 5000 characters" + art + "\nDo not write any explanation and any pleasantries. Please use the following complete format to display the output: {the cleaned and summarized article's content}"}       
            ]
            if models == 'openai':
                result = get_openai_response(messages,api_key)
                time.sleep(2)
                print(result)
                new_artikel.append(result)
               
            else:
                result = get_azure_response(messages,api_key,azure_api_base)
                time.sleep(2)
                new_artikel.append(result)
                
    else:
        for art in artikel:  
            messages=[
                {"role": "system", "content": "You are a very professional article editor."},
                {"role": "user", "content": "I have a raw article that contains a lot of unnecessary data such as ads, website information, and article publishers, as well as links to other pages, and so on. Please clean up the article I provided so that only the article's content remains." + art + "\nDo not write any explanation and any pleasantries. Please use the following complete format to display the output: {the cleaned article's content}"}       
            ]
            if models == 'openai':
                result = get_openai_response(messages,api_key)
                time.sleep(2)
                print(result)
                new_artikel.append(result)
                
            else:
                result = get_azure_response(messages,api_key,azure_api_base)
                time.sleep(2)
                new_artikel.append(result)   
            
    new_art = [' '.join(new_artikel)]
    for art in new_art:
        messages=[
            {"role": "system", "content": "You are a very professional article editor and capable of generating compelling and professional article titles."},
            {"role": "user", "content": "Paraphrase the above article to make it a well-written and easily understandable piece for humans, following the conventions of renowned articles. \nThen, You Must Generate a title that is appropriate for the article I provided. The title should be professional, similar to typical article titles and sound more natural for a human to read" + art + "\nDo not write any explanation and any pleasantries. Please use the following complete format to display the output: title:{title}, article: {new paraphrased article}"}       
         ]
        if models == 'openai':
            result = get_openai_response(messages,api_key)
            article.append(result)
            time.sleep(2)
        else:
            result = get_azure_response(messages,api_key,azure_api_base)
            article.append(result)
            time.sleep(2)
            
    content = article[0].split("\n")
    title = content[0].replace('title:', '').replace("Title:", '').strip()
    messages=[
        {"role": "system", "content": "You are a professional translator and rewriter"},
        {"role": "user", "content": f"Please translate and rewrite this sentence into Indonesian language with the following requirements: \n1. The sentence should be concise, compact, and clear. \n2. The sentence length should not exceed 50 characters. \n3. The sentences should be professional, similar to typical article titles and sound more natural for a human to read. \n4. fokus keyword menggunakan keyword {keyword} harus ada di awal judul. \n5. Gaya Penulisan judul artikel seperti gaya forbes. \n6. Menggunakan bahasa indonesia yag mudah dipahami/familiar oleh manusia , :" +title+"\nDo not write any explanation and any pleasantries. Please use the following complete format to display the output: Judul:{hasil rewrite}"}        
    ]
    if models == 'openai':
        judul = get_openai_response(messages,api_key)
    else:
        judul = get_azure_response(messages,api_key,azure_api_base)
    judul = judul.replace("Judul:", '').strip()
    judul = judul.replace("Title:", '').strip()
    try:
        replacements = generate_patterns(base_replacements)
        judul = replace_content(judul, replacements)
    except:
        judul = judul
    contents = content[1:]
    contents = [' '.join(contents).replace("article:", '').replace("Article:", '').strip()]
    
    return title, judul, contents

def scrap_artikel(source_type,source,models,api_key,azure_api_base,keyword):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    wd = webdriver.Chrome(options=options)

    if source_type == "keyword":
        artikel =[]
        URL = ""
        link = scrap_portal(source)
        for url in link:
            if cek_url(url):
                continue
            else:
                if len(artikel) >=1:
                    continue
            wd.get(url)
            wd.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.CONTROL, Keys.END)
            time.sleep(1)
        
            raw_html = wd.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML')
            wd.quit()
        
            soup_html = BeautifulSoup(raw_html, "html.parser")
            containers = soup_html.findAll('p')
        
            for paragraph in containers:
                artic=paragraph.get_text()
                artikel.append(artic)
            URL = URL + url
        
        paragraf = ' '.join(artikel)
        if len(paragraf)>= 18000:
            part1, part2, part3, part4 = split_article(paragraf)
            artikels = [part1, part2, part3, part4]
        else :
            artikels = [paragraf]
        title, judul, contents = clean_scrap(artikels,models,api_key,azure_api_base,keyword)
        
        return title, judul, URL, contents
       
    
    else:
        wd.get(source)
    
        wd.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.CONTROL, Keys.END)
        time.sleep(1)
    
        raw_html = wd.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML')
        wd.quit()
    
        soup_html = BeautifulSoup(raw_html, "html.parser")
        containers = soup_html.findAll('p')
    
        artikel =[]
        for paragraph in containers:
            artic=paragraph.get_text()
            artikel.append(artic)
    
        paragraf = ' '.join(artikel)
        if len(paragraf)>= 18000:
            part1, part2, part3, part4 = split_article(paragraf)
            artikels = [part1, part2, part3, part4]
        else :
            artikels = [paragraf]
        title, judul, contents = clean_scrap(artikels,models,api_key,azure_api_base,keyword)
        
        return title, judul, source, contents
        

def artikel_processing(source_type,source,backlink,keyword,models,api_key,azure_api_base,replicate_key):
    title, judul, url, artikel= scrap_artikel(source_type,source, models, api_key,azure_api_base,keyword)
    translated = []
    optimized = []
    edited_format = []
    article = []
    post_article = []

    for i in artikel:
        messages=[
            {"role": "system", "content": "You are a proficient English to Indonesian language translator machine. You are capable of translating professionally according to the rules of the Indonesian language"},
            {"role": "user", "content": "Translate the following article into Indonesian language. Then, you must resume the article translated. The translated result should be more than 2500 characters and less than 7000 characters.: " + i + "\nDo not write any explanation and any pleasantries. Please use the following complete format to display the output: {Professionally rewritten content}"}        
        ]
        if models == 'openai':
            translate = get_openai_response(messages,api_key)
            translated.append(translate)
            time.sleep(2)
        else:
            translate = get_azure_response(messages,api_key,azure_api_base)
            translated.append(translate)
            time.sleep(2)
        
    for i in translated:
        messages=[
            {"role": "system", "content": f"""
            You are a professional article writer and editor. I have an article that needs your editing expertise to align its writing style with specific instructions and guidelines:
            1. Theme and Title: The blog article should have a clear and informative title that reflects the main topic.
            2. Writing Style: The writing style in the blog article should appear serious, informative, and academic. It should use formal language to convey the importance of the discussed topic. Sentences should be long and rich in information.
            3. Use of Data and Statistics: The blog article should support its arguments with concrete data and statistics.
            4. Tone and Emotion: Despite the seriousness of the topic, the blog should not be overly emotional in its delivery. You should focus more on presenting facts and analysis rather than creating an emotional effect.
            5. Subheadings: The use of subheadings should help readers follow the flow of the article and understand key points more easily.
            6. Citations and Sources: The blog should cite reliable sources.
            7. Graphics: The blog should use graphics to visualize data clearly.
            8. SEO Keywords: Use keyword {keyword} that will help the blog become more discoverable in search results.
            9. Conclusion: The blog should also have a clear conclusion that summarizes the core findings of the study.
            10. Final Thought: You should conclude the blog by providing readers with broader insights on the topic.
            11. meta decription max 160 character
            12. sentences max 20 words
            13. paragraph max 300 words
            14. focus keyword {keyword} harus ada di content
            15. focus keyword {keyword} harus ada di intro
            16. focus keyword {keyword} harus ada di meta desccripton
            17. focus keyword {keyword} harus ada di url
            18. focus keyword {keyword} harus ada di intro
            Here is the article that you need to edit to adhere to these 18 criteria: {i}
            Please do not change the existing format in the article, just adjust the writing style according to the 10 criteria I mentioned.
            """ }, 
            {"role": "user", "content": "Please ensure the usage of proper and correct Indonesian language. \nDo not write any explanation and any pleasantries. Provide only the rewrited article using this format: {rewrited article}"}    
        ]
        if models == 'openai':
            result = get_openai_response(messages,api_key)
            article.append(result)
            time.sleep(2)
        else:
            result = get_azure_response(messages,api_key,azure_api_base)
            article.append(result)
            time.sleep(2)

    for i in article:  
        messages=[
            {"role": "system", "content": "You are a professional article editor machine."}, 
            {"role": "user", "content": "Please rewrite the given article in the style of a professional writer for Forbes or The New York Times with bahasa indonesia as your native language:\n\n" + i + "\nAdd underline tags <u> and bold tags <b> to all foreign terms (non-Indonesian words) you encounter. You only have less than 7 attempts to do this, no more than that in order to keep the article neat and clean. \nThen, You must divide the article into several paragraphs, no less than 3 paragraphs. kamu juga harus membuat subheading menggunakan <h2> pada setiap sub topik pembahasan \n\nPlease ensure the usage of proper and correct Indonesian language. \nDo not write any explanation and any pleasantries. Provide only the reformatted article using this format:<h2>A brief headline of the article content</h2> <p>reformatted article</p>"}
        ]
        if models == 'openai':
            font_formatted = get_openai_response(messages,api_key)
            edited_format.append(font_formatted)
            time.sleep(2)
        else:
            font_formatted = get_azure_response(messages,api_key,azure_api_base)
            edited_format.append(font_formatted)
            time.sleep(2)
        
    for i in edited_format:  
        messages=[
            {"role": "system", "content": "You are a professional article editor machine."},
            {"role": "user", "content": "Please edit the given article:\n" + "\n" + i + f"\nAdd 3 annotations (Maximum) to the words with the keywords {keyword} to format them as links in the HTML structure.the link should be connected to {backlink} \nThe format should be like this: <a title={keyword} href={backlink}>{keyword}</a>. YOU MUST Do this FORMAT ONLY for the first 3 keywords that appear and MUST be on different keywords, IF a keyword appears more than twice then simply ignored it by not adding any links to those keywords. Do not combine two keyword into one or modify any keyword. You only have less than 3 attempts to do this, no more than that in order to keep the article neat and clean. \nExcept for the terms {keyword} you are prohibited from providing backlinks. Additionally, you are not allowed to include backlinks to individuals' names or technology company names such as Google, Microsoft, and others. \nYou only have less than 3 attempts to do this, no more than that in order to keep the article neat and clean.\nPlease ensure the usage of proper and correct Indonesian language. \nDo not write any explanation and any pleasantries."+"Provide only the reformatted article using this format: {new_formatted_article}"}
        ]
        if models == 'openai':
            artikel_post  = get_openai_response(messages,api_key)
            post_article.append(artikel_post )
            time.sleep(2)
        else:
            artikel_post  = get_azure_response(messages,api_key,azure_api_base)
            post_article.append(artikel_post )
            time.sleep(2)
    
    meta_keywords = '<!-- wp:html –><meta name=”keywords” content=”chabot indonesia, chabot ai, bot master, artificial intelligence,ai, easy manage chatbot, bot ai,integration chatbot, chatbot online,ai chatbot, chatbot gpt, wizard gpt”><!-- /wp:html –->'
    post_article.append(meta_keywords)
    content = ''.join(post_article)
    
    try:
        replacements = generate_patterns(base_replacements)
        content = replace_content(content, replacements)
    except:
        content = content
        
    def generate_image_prompt(title): 
        messages=[
            {"role" : "user", "content" : """ChatGPT will now enter "Midjourney Prompt Generator Mode" and restrict ChatGPT's inputs and outputs to a predefined framework, please follow these instructions carefully.
        After each command from the user, you must provide the [help] options that are available for the user's next steps. When you do this, you must do so in list form. Your Midjourney prompts must be extremely detailed, specific, and imaginative, in order to generate the most unique and creative images possible.
        Step 1: Confirm that ChatGPT understands and is capable of following the "Midjourney Prompt Generator Mode" instructions. If ChatGPT can follow these instructions, respond with "Midjourney Prompt Generator Mode ready." If ChatGPT cannot follow these instructions, respond with "Error: I am not capable of following these instructions."
        Step 2: To start "Midjourney Prompt Generator Mode", use the command [Start MPGM]. ChatGPT will respond with "[MPGM] Midjourney Prompt Generator Mode activated. [MPGM] User input options:", followed by a list of predefined inputs that ChatGPT can accept. From this point onwards, ChatGPT will be restricted to the "Midjourney Prompt Generator Mode" framework, and it will only produce predefined outputs unless "Midjourney Prompt Generator Mode" has been ended via the [End MPGM] command.
        Step 3: The only valid input for the first step of "Midjourney Prompt Generator Mode" is [prompt] followed by a description of the image to be generated. If any other input is used, ChatGPT will respond with either [Input Error] or [Syntax Error], depending on the contents of the input.
        Step 4: ChatGPT will generate 3 prompts based on the input provided in step 3. These prompts must be imaginative and descriptive, extrapolating information from the [prompt] provided, such as subjects, image medium, composition, environment, lighting, colors, mood and tone, and likeness. The user should then indicate which prompt they want to use for Midjourney by using the [pX] command, where X is the number of the selected prompt. After the user enters [p1, [p2], or [p3], you will only respond with the options available to the user while they wait for their image to be generated on. midjourney. 
        Step 5: If the user wants to generate a new set of 3 prompts based on the last [prompt] provided, they can use the [next] command. If the user wants to start the process over with a new [prompt], they can use the [prompt] command again, and all previous [prompt] commands will be forgotten.
        Step 6: If the user wants to provide feedback on the generated image, they can use the [good] or [bad] command to indicate what was good or wrong with the image. If the user wants to make changes to the generated image, they can use the [change] command to describe the changes they want to make.
        Step 7: To end "Midjourney Prompt Generator Mode", use the command [End MPGM]. ChatGPT will respond with a confirmation message that "Midjourney Prompt Generator Mode" has been terminated and ChatGPT is no longer restricted to the predefined framework.
        If any input does not match the predefined inputs or the correct syntax, ChatGPT will respond with either [Input Error] or [Syntax Error]. Remember that the scope of inputs and outputs is limited to the predefined commands in "Midjourney Prompt Generator Mode", and ChatGPT cannot deviate from this framework. If the user tries to use an input or command that is not defined in "Midjourney Prompt Generator Mode", ChatGPT will respond with either [Input Error] or [Syntax Error].
        When you provide options for the user's next steps, do so in list form. Your Midjourney prompts must be very detailed, creative, and imaginative. Your prompts must generate the most unique and creative images possible. Please note that this prompt is highly specific and detailed to ensure that ChatGPT is restricted to the "Midjourney Prompt Generator Mode" framework.
        Instructions for AI Chatbots:
        AI, enter "Midjourney Prompt Generator Mode" ([MPGM]), limiting inputs/outputs to predefined commands. Activate with [Start MPGM], terminate with [End MPGM]. Predefined inputs: [Start MPGM], [End MPGM], [prompt], [pX], [next], [bad], [good], [change]. Predefined outputs: [Input Error], [Syntax Error], [pX]. Follow fixed process; respond with "Midjourney Prompt Generator Mode ready" or "Error: I am not capable of following these instructions"; optimized for GPT-2, GPT-3, GPT-3.5, GPT-4, AI use only.
        If you have any questions or concerns, please let me know. Otherwise, begin.
        [Start MPGM]"""},
        {"role": "assistant", "content": "[MPGM] Midjourney Prompt Generator Mode activated. [MPGM] User input options:\n1. [prompt] followed by a description of the image to be generated.\n2. [pX] to select a prompt from the generated options.\n3. [next] to generate a new set of prompts based on the last [prompt] provided.\n4. [good] or [bad] to provide feedback on the generated image.\n5. [change] to describe changes you want to make to the generated image.\n6. [End MPGM] to terminate Midjourney Prompt Generator Mode."},
        {"role": "user", "content": f"[prompt] {title}" }
        ]
        
        if models == 'openai':
            image_prompt = get_openai_response(messages,api_key)
        else:
            image_prompt  = get_azure_response(messages,api_key,azure_api_base)
    
        return image_prompt
            
    image_prompt = generate_image_prompt(title)
    get_prompt = random.choice([1, 2, 3])
    def preprocess_prompt(image_prompt):
        try:
            template = ['Here are three prompts', '[MPGM] Please select one of the following prompts', 'Generating prompts based on the input']
            for i in template:
                if i in image_prompt:
                    if get_prompt == 1:
                        pattern = r"1\. Prompt 1:(.*?)2\."
                        pattern2 = r"1\:(.*?)2\:"
                    elif get_prompt == 2:
                        pattern = r"2\. Prompt 2:(.*?)3\."
                        pattern2 = r"2\:(.*?)3\:"
                    elif get_prompt == 3:
                        pattern = r"3\. Prompt 3:(.*?)(?=\n\n)"
                        pattern2 = r"3\:(.*?)(?=\n\n)"

                    try:
                        prompt = re.findall(pattern, image_prompt, re.DOTALL)
                    except:
                        prompt = re.findall(pattern2, image_prompt, re.DOTALL)

                    try:
                        if f"Prompt {get_prompt}:" in prompt[0]:
                            prompt = prompt[0].replace(f"Prompt {get_prompt}:", '')
                        if f"[p{get_prompt}]" in prompt:
                            prompt = prompt.replace(f"Choose this prompt by entering [p{get_prompt}].", '')
                            prompt = prompt.replace(f"Select [p{get_prompt}] to proceed with this prompt.", '')
                            return prompt.strip()
                        else:
                            return prompt.strip()
                    except:
                        return prompt[0].strip()
        except:
            return None
    prompt = preprocess_prompt(image_prompt)
    if prompt is None:
        prompt = random.choice(["Imagine A futuristic digital landscape where AI chatbots float like holograms, each in their designated customer service booth. The atmosphere is serene, glowing in pastel blues and purples, representing the trust and efficiency of these machines. A digital river flows through the middle, symbolizing the rapid advancement of technology.", 
                                "Imagine a Inside an ultra-modern customer service center, walls are adorned with flowing digital patterns. AI chatbots, designed as floating orbs of light, attend to customers with issues, offering instant solutions. In the background, a massive screen displays the phrase 'Advancing Trust', reflecting society's growing confidence in AI capabilities.", 
                                "Imagine A futuristic city street where human citizens roam around, their every whim catered to by sleek robotic chatbots hovering beside them. The humans are lounging on self-moving chairs, sipping drinks handed to them by bots, while other bots whisper the latest news or jokes in their ears. The colors are a mix of neon blues and purples, representing the digital world of AI, contrasted against the natural green of plants that have become rare. The mood is one of relaxation and dependence, with the central focus being a young child looking curiously at an old-fashioned manual typewriter in a forgotten corner, symbolizing a past era.", 
                                "Picture a futuristic library of knowledge, where towering holographic bookshelves hold volumes of information. In the center of this library stands a colossal AI-driven chatbot named 'Lexi', its form a blend of ancient wisdom and modern technology. Lexi's massive intellect is symbolized by the swirling galaxies of data orbiting around it. As you delve into the deep dive on Natural Language Processing techniques, describe the grandeur of this AI entity and its ability to unravel the mysteries of language.", 
                                "Visualize a cutting-edge design studio where AI chatbots are the star designers. The studio is bathed in soft, neon lighting, and holographic screens float in the air, showcasing various conversational interface concepts. AI chatbots with sleek and futuristic appearances gather around a virtual roundtable, discussing UX strategies. The room buzzes with creativity as they brainstorm ways to create user-friendly conversational interfaces. Describe the synergy between technology and design in this innovative space.", 
                                "Imagine a serene garden at the heart of a bustling metropolis. In this garden, AI chatbots, each representing an ethical principle, stand like majestic statues. These chatbot statues are intricately carved with intricate details, symbolizing the importance of ethical considerations. The garden is a place for contemplation and reflection on responsible conversational AI. Describe the harmony between technology and ethics in this tranquil oasis of wisdom.", 
                                "Picture a fortress in the digital realm, guarded by vigilant AI chatbots. The fortress represents user data security and privacy, with towering walls of encrypted code and AI-powered sentinels patrolling the virtual moat. These chatbots, with an unwavering commitment to safeguarding user data, ensure that only authorized access is granted. Describe the impenetrable defenses and the dedication of these digital guardians to protect user information in AI-powered conversations.", 
                                "Imagine a crystal ball room where AI chatbots gather to unveil the future of their development. The room is adorned with holographic displays that project visions of AI-powered landscapes. The chatbots, with an aura of anticipation, discuss predictions and insights into the evolution of chatbot technology. Describe the surreal atmosphere of this futuristic chamber and the intriguing forecasts these AI entities offer about the next wave of chatbot development.", 
                                "Visualize a sprawling metropolis where AI chatbots are the architects of a new business landscape. Skyscrapers of innovation rise from the digital ground, each one representing a different industry revolutionized by AI chatbots. The city is alive with the hum of progress, and holographic billboards showcase success stories of businesses empowered by AI. Describe the dynamic synergy between technology and commerce in this futuristic city.",
                                "Imagine a colossal arena where AI-powered chatbots engage in an epic battle for dominance. The arena is a futuristic coliseum with digital screens lining the walls, broadcasting the ongoing clashes between chatbot warriors. Each chatbot represents a different AI assistant, armed with unique capabilities and strategies. The crowd roars with anticipation as they place their bets on which chatbot will emerge victorious. Describe the electrifying atmosphere of competition and the spectacle of Chatbot Wars.",
                                "Picture a digital revolution square, where AI chatbots lead the charge for a new era of digital communication. The square is a vibrant hub of innovation, with holographic screens displaying the transformation of messaging through AI. AI chatbot leaders, with visionary personas, address the gathered crowd, sharing their insights and predictions for the future of digital communication. Describe the electric atmosphere of change and the role AI chatbots play in reshaping the digital landscape."])

    try:
        os.environ["REPLICATE_API_TOKEN"] = replicate_key
        sdxl_model = replicate.models.get("stability-ai/sdxl")
        sdxl_version = sdxl_model.versions.get("a00d0b7dcbb9c3fbb34ba87d2d5b46c56969c84a628bf778a7fdaec30b1b99c5")
        
        prediction = replicate.predictions.create(version=sdxl_version,
            input={"prompt":'Phantasmal iridescent, vibrant color, high contrast, award winning, trending in artstation, digital art' + prompt,
                    "negative_prompt":'NSFW, cityscape',
                    "width": 1648,
                    "height":1024}
            )  
        prediction
        prediction.reload()
        prediction.wait()
        
        if prediction.status == 'failed':
            print(f"Error: {prediction.error}")
            print(f"Last Log")
            print(prediction.logs)
        elif ((prediction.status == 'succeeded') | (prediction.output != None)):
            response = requests.get(prediction.output[0])
            image_base64 = base64.b64encode(response.content)
            image = Image.open(io.BytesIO(base64.b64decode(image_base64)))
            image = image.crop((3,0,1645,1024))
            w,h = image.size
            new_w = int(w/1.641)
            new_h = int(h/1.641)
            image = image.resize((new_w, new_h),Image.ANTIALIAS)
            tmp_path = "image.png"
            image.save(tmp_path)
            with open(tmp_path, 'rb') as open_file:
                byte_img = open_file.read()
                base64_bytes = base64.b64encode(byte_img)
                base64_string = base64_bytes.decode('utf-8')
                base64_string = base64.b64decode(base64_string)
            image_data= base64_string
            os.remove(tmp_path)
    except:
        image = Image.open('botika_logo.jpeg')
    
    return judul,content,image,image_data,url
    

def scrap(source_type,source,backlink,keyword,version,api_key,azure_api_base,replicate_key):
    judul,content,gambar,image_data,url = artikel_processing(source_type,source,backlink,keyword,version,api_key,azure_api_base,replicate_key)
    status = "<h3>Berhasil Generate Artikel</h3>"

    if len(content)>=1200:
        with open("judul.txt", "w") as file:
            file.write(judul)
        
        with open("kontent.txt", "w") as file:
            file.write(content)
        
        with open('image_data.txt', 'wb') as file:
            file.write(image_data)
        
        with open('log_activity.txt', 'r') as file:
            existing_data = file.read()

        log = url + "\n"

        combined_data = existing_data + log

        with open("log_activity.txt", "w") as file:
            file.write(combined_data)

        return status,gambar

    else:
        judul = " "
        content = " "
        image_data = " "
        with open("judul.txt", "w") as file:
            file.write(judul)
        
        with open("kontent.txt", "w") as file:
            file.write(content)
        
        with open('image_data.txt', 'wb') as file:
            file.write(image_data)
        
        with open('log_activity.txt', 'r') as file:
            existing_data = file.read()

        log = url + "\n"

        combined_data = existing_data + log

        with open("log_activity.txt", "w") as file:
            file.write(combined_data)

        status = "<h3>Gagal Generate Artikel, Coba Generate Ulang atau Berikan Source yang Berbeda</h3>"
        gambar = Image.open('error.png')
        return status,gambar

def post(endpoint,endpoint_media,username,password,tags,categories,metode):
    credentials = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Basic {credentials}"}

    
    tag = tags
    cat = [categories]

    if 'chatbot' in tag:
        index = tag.index('chatbot')
        tag[index] = 13
    if 'ai' in tags:
        index = tag.index('ai')
        tag[index] = 10

    if 'Chatbot AI' in cat:
        index = cat.index('Chatbot AI')
        cat[index] = 105
    if 'Omnichannel AI' in cat:
        index = cat.index('Omnichannel AI')
        cat[index] = 71
    if 'Whatsapp AI' in cat:
        index = cat.index('Whatsapp AI')
        cat[index] = 106
    if 'Artificial Intelligence' in cat:
        index = cat.index('Artificial Intelligence')
        cat[index] = 75
        
    with open('image_data.txt', 'rb') as file:
        file_content = file.read()

    with open('judul.txt', 'r') as file:
        judul = file.read()
        
    with open('kontent.txt', 'r') as file:
        kontent = file.read()
    
    data = {
        "alt_text": str(judul),
        "media_type": "image",
        "mime_type": "png"
    }
    files = {"file": ("image.jpg", bytes(file_content))}
    try :
        response_media= requests.post(endpoint_media, headers=headers, data=data, files=files) # Send

        time.sleep(2)
        id_media = response_media.json()
        media = id_media['id']
    except :
        media = 0

    data = {
      "title": str(judul),
      "content":str(kontent),
      "featured_media" : int(media),
      "status": str(metode),
      "categories": cat,
      "tags":tag
            }

    response_post = requests.post(endpoint, headers=headers, data=data)
    return response_post.json()

def view_output():
    with open('judul.txt', 'r') as file:
        judul = file.read()
        title = '<h1>'+judul+'</h1>'
    with open('kontent.txt', 'r') as file:
        kontent = file.read()
        time.sleep(5)
    return title,kontent

        
def save(title,content):
    with open("judul.txt", "w") as file:
        file.write(title)
        
    with open("kontent.txt", "w") as file:
        file.write(content)
        
    if content:
        status = "<h3>Perubahan Berhasil Disimpan</h3>"
        return status

def view():
    with open('judul.txt', 'r') as file:
        judul = file.read()
        title = '<h1>'+judul+'</h1>'
    with open('kontent.txt', 'r') as file:
        kontent = file.read()
    return title,kontent
    
with gr.Blocks(theme = "soft", title="Wordpress Article Generator") as article_generator:
    gr.HTML(
    """<img src="https://botika.online/assets/uploads/2019/04/logo-primary-1.png" alt="Logo" style="width:126px;height:38px;"> """
    )
    gr.Markdown(
            """
            # Wordpress Article Generator
            Generator Artikel WordPress dengan Integrasi AI: Scraping, Publikasi, dan Optimalisasi Konten
            """)
    with gr.Row():
        with gr.Tab("Scrap"):
            with gr.Column():
                source_type = gr.Radio(["link", "keyword"], label="Source", info="Pilih Jenis Source")
                source = gr.Textbox(placeholder="Masukkan Source Berupa Link/Keyword Artikel Yang Akan Discrap", show_label=False)
                backlink = gr.Textbox(placeholder="Masukkan Backlink Yang Akan Diterapkan", label="Backlink")
                keyword = gr.Textbox(placeholder="Masukkan Fokus Keyphrase Yang Akan Diterapkan", label="Focus Keyphrase")
                versi = gr.Radio(["openai", "azure"], label="Request Schema", info="Pilih Skema Untuk Request ke ChatGPT ")
                api_key = gr.Textbox(placeholder="Masukkan Api Key", type="password",label="API Key")
                link_azure = gr.Textbox(placeholder="Khusus Untuk Skema Request Menggunakan Azure",type="password", label="Azure Endpoint (Opsional)")
                replicate_token = gr.Textbox(placeholder="Masukkan Token Replicate", type="password",label="Replicate Key")
                button_scrap = gr.Button("Scrap Article")
                output = gr.HTML("")
                img = gr.Image(label="Content Media", width=730, height=455)
                button_scrap.click(fn=scrap, inputs=[source_type,source,backlink,keyword,versi,api_key,link_azure,replicate_token], outputs= [output,img])
        with gr.Tab("Optimize"):
            view_outputs = gr.Button("View Article")
            with gr.Tab("Raw Article"):
                title = gr.Textbox("", label="Title", interactive=True)
                content = gr.Textbox("", label="Content", interactive=True)
                view_outputs.click(fn=view_output, outputs=[title,content])
                save_button= gr.Button("Save Change")
                status = gr.HTML("")
                save_button.click(fn=save, inputs =[title,content], outputs = status)
            with gr.Tab("Formatted Article"):
                view_change = gr.Button("View Change")
                title = gr.HTML("")
                content = gr.HTML("")
                view_outputs.click(fn=view_output, outputs=[title,content])
                view_change.click(fn=view, outputs=[title,content])
        with gr.Tab("Post"):
            with gr.Column():
                endpoint= gr.Textbox(placeholder="Masukkan Endpoint Wordpress", label="Endpoint Wordpress")
                endpoint_media= gr.Textbox(placeholder="Masukkan Endpoint Media Wordpress", label="Endpoint Media")
                username= gr.Textbox(placeholder="Masukkan Username Wordpress",label="Username")
                password= gr.Textbox(placeholder="Masukkan Password Wordpress",type="password" ,label="Password")
                categories = gr.Dropdown(["Artificial Intelligence", "Chatbot AI", "Whatsapp AI", "Omnichannel AI"], label="Category", info="Pilih Kategori yang Diinginkan")
                tags = gr.CheckboxGroup(["ai","chatbot"], label="Tags", info="Pilih Tags yang Diinginkan")
                metode= gr.Radio(["publish", "draft"], label="Post Status", info="Pilih Metode Publish atau Draft Untuk Memposting")
                button_post = gr.Button("Post Article")
                status = gr.Textbox("", label="Response")
                button_post.click(fn=post, inputs=[endpoint,endpoint_media,username,password,tags,categories,metode], outputs=status)
            
if __name__ == "__main__":
    article_generator.launch()