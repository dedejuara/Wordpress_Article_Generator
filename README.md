# Wordpress Article Generator
Program Wordpress Article Generator adalah sebuah aplikasi yang terintegrasi dengan Chat-GPT untuk memudahkan proses pembuatan artikel WordPress. Dengan fitur scraping, publikasi, dan optimalisasi konten, program ini dirancang untuk meningkatkan efisiensi dalam mengelola konten di platform WordPress.

## Requirements
Untuk menjalankan program ini, pastikan sistem Anda memenuhi persyaratan berikut:

- Python 3.10
- Library yang diperlukan
  - selenium 4.15.2
  - gradio 3.40.1
  - Pillow 9.2.0
  - openai 0.27.6
  - bs4
  - replicate

NB: Sangat disarankan untuk menggunakan virtual environment.

## Instalasi

1. Instal semua dependensi dengan menjalankan perintah:

    ```bash
    pip install -r requirements.txt
    ```
    
2. Download dan Install Chromedriver : [Chromedriver 119.0.6045.105](https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/win32/chromedriver-win32.zip)
3. Download dan Install Chromium : [Chrome for Testing (Chromium) 119.0.6045.105](https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/win32/chrome-win32.zip)
   
## Penggunaan

1. Jalankan aplikasi dengan perintah:

    ```bash
    python app.py
    ```

2. Buka link yang ditampilkan dalam terminal, biasanya pada [http://127.0.0.1:7860/](http://127.0.0.1:7860/).
3. Program akan menampilkan interface berupa 3 tab yang masing-masing merupakan tab scraping, tab optimize artikel dan tab post artikel.

   Berikut penjelasan dari masing-masing tab:

    ### Tab Scrap
    
    ![Screenshot of a comment on a GitHub issue showing an image, added in the Markdown, of an Octocat smiling and raising a tentacle.](https://i.imgur.com/ERfIwJC.png)
    
    Berikut adalah beberapa parameter yang harus diinputkan user.
    - Type Source (radio)
      User dapat menentukan source artikel yang akan di scrap, source dapat berupa link artikel atau keyword artikel yang ingin digenerate.
    - Source (link/str)
      - Jika type source yang dipilih adalah link, maka user dapat menginputkan link artikel yang akan discrap. contoh `https://www.ibm.com/id-en/topics/chatbots`
      - Jika type source yang dipilih adalah keyword, maka user cukup menginputkan keyword artikel yang dikehendaki untuk digenerate. contoh `ai`, `chatbot`, `omnichannel`
    - Backlink (link)
      User dapat menambahkan tautan atau hyperlink yang mengarah dari satu halaman web ke halaman web lainnya. 
    - Focus Keypharse (str)
      Focus keypharse ditujukan untuk mengoptimalkan SEO artikel yang akan digenerate. focus keypharse bekerja pada beberapa unsur, seperti judul artikel, intro artikel, serta backlink. Contoh input focus keypharse: `artificial intelligence`, `chatbot ai`, `whatsapp ai`
    - Request Schema (radio)
      Terdapat dua opsi request chat-gpt untuk melakukan generate artikel, yaitu request versi openai dan versi azure.  
    - Api Key (pwd)
      Jika menggunakan skema openai maka api key yang diinputkan adalah api key openai, begitu pula jika menggunakan skema request menggunakan azure.
    - Azure Endpoint (link)
      Komponen ini hanya diisi ketika user melakukan request menggunakan api key dari azure (opsional)
    - Replicate Key (pwd)
    Setelah semua parameter terisi, user dapat memulai proses dengan menekan Button  `Scrap Article`. Proses ini akan memakan waktu 5-10 menit, kemudian Program akan menampilkan output berupa status generate dan hasil generate feature media untuk artikel.
      
    
    ### Tab Optimize
    Pada tab ini terdapat dua opsi untuk menampilkan output. yaitu versi raw text dan formatted text.
      
    ![Screenshot of a comment on a GitHub issue showing an image, added in the Markdown, of an Octocat smiling and raising a tentacle.](https://i.imgur.com/eBPv9eP.png)
    
    - Tab Raw Text memungkinkan user untuk melakukan pengeditan terhadap artikel yang telah digenerate, user dapat menambahkan isi content, menghapus backlink, mengubah judul, dan mengedit format html seperti `<title>`, `<h2>`, `<h3>`, `<strong>`, `<b>`, `<i>`, `<u>`, serta tag lain yain digunakan untuk melakukan format font.
    - Terdapat button `Save Changes` untuk menyimpan artikel yang diedit.
         
    ![Screenshot of a comment on a GitHub issue showing an image, added in the Markdown, of an Octocat smiling and raising a tentacle.](https://i.imgur.com/HhL46I2.png)
    
    - Tab Formatted text digunakan untuk menampilkan output artikel sesuai dengan format html yang telah diterapkan.
    - Jika sebelumnya user telah melakukan pengeditan pada tab raw text, maka user perlu menekan button `View Change` untuk menampilkan perubahan.
    
    ### Tab Post
    
    ![Screenshot of a comment on a GitHub issue showing an image, added in the Markdown, of an Octocat smiling and raising a tentacle.](https://i.imgur.com/nOTnYw9.png)
     
    Berikut adalah beberapa parameter yang harus diinputkan user.
    - Enpoint Wordpress (link)
    - Endpoint Media (link)
    - Username wordpress (str)
    - Password user (pwd)
    - Category (dropdown)
    - Tags (checkbox)
    - Post Status (radio)
      Terdapat dua opsi untuk melakukan post, yaitu draft dan publish
    Untuk memulai post artikel user perlu menekan button `Post Article`, kemudian program akan menampilkan output request berupa data json

#### Anda dapat melakukan demo program pada link berikut : [Wordpress Article Generator](https://huggingface.co/spaces/Dede16/Article_Gen4)  
