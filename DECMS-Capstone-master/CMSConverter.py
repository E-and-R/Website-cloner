import urllib.request, urllib.error, urllib.parse
from urllib.parse import urlparse
from scrapy.http import HtmlResponse
from tqdm import tqdm, tqdm_gui #progress bar library
from bs4 import BeautifulSoup
import re, os,time,requests, threading, sys
from requests.exceptions import ConnectionError
from urllib.parse import urljoin
import progressGUI


class CMSConverter:

    def __init__(self,url):
        self.url = url
        try:
            self.response = self.get_websitecontent(self.url)
        except ConnectionError:
            self.invalid_website(self.url)
            
        if(url == start_url):
            self.find_cms(self.response)
            
        self.workflow(self.response)
        super().__init__()

    '''Gets the html from a url '''
    def get_websitecontent(self,url):
        
        headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }
        request_response = requests.get(url, headers=headers)

        if request_response.status_code != 429:
            webcontent_bytes = request_response.content
            webcontent_soup = BeautifulSoup(webcontent_bytes,'html.parser')
            response = HtmlResponse(url=url, body=str(webcontent_soup), encoding='utf-8')
            return response
        else:
            time.sleep(int(request_response.headers["Retry-After"]))
            request_response = requests.get(url, headers=headers)
            webcontent_bytes = request_response.content
            webcontent_soup = BeautifulSoup(webcontent_bytes,'html.parser')
            response = HtmlResponse(url=url, body=str(webcontent_soup), encoding='utf-8')
       
            return response
        
    ''' Stops the current thread for invalid URL '''
    def invalid_website(self,url):
        if url == start_url:
            progress_GUI.progress_update("Website "+start_url+" does not exist")
            progress_GUI.stop_timer()
            sys.exit()
        else:
            sys.exit()
            
    '''our main method '''
    def workflow(self,response): 
        webcontent = str(BeautifulSoup(response.body,'html.parser'))

        if(response.url == start_url):
            self.find_cms(response)
            found_pages.append(response.url)
        atagThread = processingThread(target= self.scrape_a_tags, args=(response,))
        imageThread = processingThread(target= self.scrape_images, args=(response,))
        javascriptThread = processingThread(target= self.scrape_javascript, args=(response,))
        stylesheetThread = processingThread(target= self.scrape_stylesheets, args=(response,))
        other_links_thread = processingThread(target= self.scrape_other_tags,  args=(response,))
        forms_thread = processingThread(target= self.scrape_forms,  args=(response,))

        atagThread.start()
        imageThread.start()  
        javascriptThread.start()
        stylesheetThread.start()
        other_links_thread.start()
        forms_thread.start()
        
        forms = forms_thread.join()
        other_links,other_html_files = other_links_thread.join()
        images = imageThread.join()
        stylesheets = stylesheetThread.join()
        javascripts = javascriptThread.join()
        other_files,html_files = atagThread.join()

        all_links = images+javascripts+stylesheets+other_files+other_links+forms
        html_files = other_html_files + html_files
        
        ''' trying to remove duplicates '''
        html_files = list(set(html_files))
        all_links = list(set(all_links)) 
        
        localise_message = "localising  "+response.url
        
        
        for file in tqdm(html_files,desc=localise_message,file=progress_GUI.progress_output,bar_format='{l_bar}{bar:50}{r_bar}{bar:-10b}'):
            
            ''' Ensures that we do not localise where the is a # at link start, 
                since its same page link also ensuring we do not localise 
                external sites which have not been downloaded '''
            if (self.check_same_page(file) == False and self.allowed_domain(response.urljoin(file)) == True):
                site_name = self.html_file_name(response.urljoin(file))+".html"
                webcontent = self.localise(file,site_name,webcontent)
                
                self.get_page(urljoin(start_url,file),start_url)
        
        download_message = "Downloading content of : "+response.url
        for link in tqdm(all_links,desc=download_message,file=progress_GUI.progress_output, bar_format='{l_bar}{bar:50}{r_bar}{bar:-10b}'):
            name = self.file_name(link)
            webcontent = self.localise(link,name,webcontent)
            if (self.check_if_downloaded(response.urljoin(link)) == False and self.allowed_domain(response.urljoin(link)) == True):
                downloadingThread(response.urljoin(link),name).start()
                pass
        
        progress_GUI.update_num_downloaded_contents(len(downloaded_links))
        self.save_file(self.html_file_name(response.url),webcontent,path)
        
        
        number_of_threads = self.number_of_executing_threads()
        if(number_of_threads!=0):
            progress_GUI.update_num_active_pages(number_of_threads)
        else:
            progress_GUI.progress_update("Done converting "+start_url+" to static website")
            progress_GUI.update_num_active_pages(number_of_threads)
            progress_GUI.stop_timer()

    ''' calls the class which starts a new page thread where necessary '''
    def get_page(self,url,start_url):
        if found_pages.count(url) == 0 and self.allowed_domain(url)  == True and self.check_same_page(url) == False:
            found_pages.append(url)
            page_thread = individualPageThread(urljoin(start_url,url))
            page_thread.name = urljoin(start_url,url)
            if threading.activeCount() <= 500:
                page_thread.start()
            else:
                time.sleep(20)
                page_thread.start()

    ''' Counts the number of threads running in parallel'''
    def number_of_executing_threads(self):
        number_of_threads = 0
        for thread in threading.enumerate():    
            if (thread.name.startswith('Thread') == False and thread.name != 'MainThread'):
                number_of_threads +=1
        '''less the current thread'''
        number_of_threads = number_of_threads -1

        return number_of_threads

    ''' Update the number of threads running in parallel '''
    def update_gui_thread_count(self,number_of_threads):
        progress_GUI.update(number_of_threads)


    '''Checking if domain is of allowed domain or not'''
    def allowed_domain(self,url):
        try:
            domain = url.split("://")[1].split("/")[0]
            '''if http://wwww.docs.gooogle.com/something/else/here
                the answer == www.docs.google.com'''
            if(urljoin(start_url,url).split("://")[1].split("/")[0] in allowed_domains): 
                return True
            else:
                return False
        except IndexError:
            return False

    '''checks if the link is of the same website or not'''
    def check_same_site(self,url,start_url): 
        if (urljoin(start_url,url).startswith(start_url)): 
            return True 
        else: 
            return False 

    '''Ensuring we do not localise link which points to a different section within a the same page'''
    def check_same_page(self,url): 
        if (url[0]  == '#'):
            return True
        else:
            return False

    '''finding out which CMS was used to build the website'''
    def find_cms(self,response):
        generators = response.xpath('//meta[@name="Generator"]/@content | //meta[@name="generator"]/@content').getall()
        progress_GUI.set_cms(generators)
        
    '''setting the name of the of the file'''
    def file_name(self,response_url):
        parsed_name = urlparse(response_url) 
        name = os.path.basename(parsed_name.path)
        return name


    '''setting the name of the html_file'''
    def html_file_name(self,response_url):
        if (response_url[-1] =="/"): #AVOIDING _.HTML type of scenario
            response_url = response_url[0:-1]

        name = response_url.replace("://", "_").replace(".", "_").replace("/", "_").replace("?","_")
        return name
        
    '''scraping all tags that may contain javascript links'''
    def scrape_javascript(self,response):
        javascripts = response.css('script').xpath('@src').getall()
        return javascripts

    '''scraping all tags that may contain stylesheets links'''
    def scrape_stylesheets(self,response):
        css_urls = []
        styles = response.xpath('//style[@type="text/css"][contains(text(),"url")]/text() | //style[@media]/text()').getall()
        styles = styles + response.css('link::attr(href)').getall()
        for style in styles:
            style = style.split()
            for url in style:
                if url.find('http') != -1:
                    url = url.strip('url")(;')
                    css_urls.append(url)
                elif url.find('.css') != -1:
                    css_urls.append(url)
        return css_urls

    '''scraping all the <a> tags'''
    def scrape_a_tags(self,response):
        other_files = []
        html_files = []
        for file in response.css('a::attr(href)').getall():
            extension =  self.get_file_extension(response.urljoin(file))
            otherFileBoolean = self.html_or_other(extension) 
            if (otherFileBoolean==False):
                other_files.append(file)
            else:
                ''' here we have html content inside of a tag instead of other file '''
                if str(file).strip() != '':
                    html_files.append(file) 
    
        return other_files,html_files

    ''' scraping all tags that may contain images links '''
    def scrape_images(self,response):
        images = response.css('img::attr(src)').getall()
        return images

    ''' scraping all other tags e.g PDF, .etc '''
    def scrape_other_tags(self,response):
        other_files = []
        html_files = []  
        other_links_list = response.css('option::attr(value)').getall()
        for file in other_links_list:
            extension =  self.get_file_extension(response.urljoin(file))
            otherFileBoolean = self.html_or_other(extension) 
            if (otherFileBoolean==False):
                    other_files.append(file)
            else:
                if str(file).strip() != '':
                    html_files.append(file) 
                
        return other_files,html_files

    def scrape_forms(self,response):
        forms = response.css('form::attr(action)').getall()
        return forms

    

    '''Get extension from the link'''
    def get_file_extension(self,url):
        try:
            extension = requests.head(url)
            extension = dict(extension.headers).get('Content-Type')
            extension = extension.split('/')[1]
            return extension
        except Exception as error:
            #did this to deal with links such as #main-content
            return 'html; charset=UTF-8'

    '''Determines if extension is of html or any other extension'''
    def html_or_other(self,extension):
        extension = extension
        normal = html_file_extensions.count(extension)
        if (normal ==0):
            return False
        else:
            return True

    '''localise the links in the website'''
    def localise(self,old_link,name,webcontent):
        new_link = './'+name
        return webcontent.replace('"'+old_link+'"','"'+name+'"')

    '''checking if the link has already been downloaded or not'''
    def check_if_downloaded(self,url):
        exists = list(filter(lambda x: 1 if url in x else 0, downloaded_links))
        if (len(exists) ==0):
            return False
        else:
            return True

    '''saving the html file'''
    def save_file(self,nameOfFile,webcontent,path):
        progress_GUI.update_pages(1)
        filename = nameOfFile+".html"
        Html_file = open(path+"/"+filename,"w") 
        Html_file.write(webcontent)
        Html_file.close()

        
    '''Ensuring we do not localise link which points to a different section within the same page'''
    def check_same_page(self,url): #urlFormating
        if (url[0]  == '#'):
            return True
        else:
            return False
  
   

class processingThread(threading.Thread):  
    def __init__(self, *init_args, **init_kwargs):  
        threading.Thread.__init__(self, *init_args, **init_kwargs)  
        self._return = None  
    def run(self):  
        self._return = self._target(*self._args, **self._kwargs)  
    def join(self):  
        threading.Thread.join(self)  
        return self._return 

class downloadingThread(threading.Thread):
    def __init__(self,download_link,file_name):
        threading.Thread.__init__(self)
        self.download_link = download_link
        self.file_name = file_name

    '''Downloading content from links'''
    def download(self,link):
        try: 
            downloaded_links.append(urljoin(start_url,link))
            ''' overcoming being denied access by websites which block bots and https websites '''
            headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }
            link_content = requests.get(urljoin(start_url,link), headers=headers).content
            myfile_name = path+"/"+self.file_name
            
            with open(myfile_name, 'wb') as file:
                file.write(link_content)
        
        except Exception as e:
            self.write_failed_links(urljoin(start_url,link),e)
        
    '''write failed links and reasons to a file'''
    def write_failed_links(self,url,error):
        file_name = 'failedLinks.txt'
        failed_file = open(path+"/"+file_name,"a") 
        failed_file.write(url+" <-----Due to error----> "+str(error)+"\n")
        failed_file.close()
        
    ''' Starts the thread '''
    def run(self):
        self.download(self.download_link)
    
    
class individualPageThread(threading.Thread):
    def __init__(self,url):
        threading.Thread.__init__(self)
        self.url = url
    def run(self):
        CMSConverter(self.url)
        


'''Global variables'''
downloaded_links = []
found_pages = []
allowed_domains = [] 
html_file_extensions = ['html; charset=UTF-8','html; charset=utf-8','html']
start_url = '' 

path = None
progress_GUI = None


class startProceedings:
    def __init__(self,website_url,domains,directory):
        global start_url
        global allowed_domains
        global path
        global progress_GUI
        start_url = website_url
        allowed_domains = domains
        path = directory

        progress_GUI = progressGUI.progressGUI()
        progress_GUI.show()
        progress_GUI.start_timer()
        # 1 thread since its just the main page being converted
        progress_GUI.update_num_active_pages(1)
        
        Thread = individualPageThread(start_url)
        Thread.name = start_url
        Thread.start() 

        self.strip_allowed_domains()
        
        super().__init__()
    
    
    def strip_allowed_domains(self):
        if len(allowed_domains) !=1 and allowed_domains[0]==' ':
            number_iterations = 0
            allowed_domains.insert(0,start_url)
            for domain in allowed_domains:
                striped_domain = domain.split("://")[1].split("/")[0]
                position = allowed_domains.index(domain)
                allowed_domains.remove(domain)
                allowed_domains.insert(position,striped_domain)
    
        else:
            allowed_domains.append(start_url.split("://")[1].split("/")[0])
    
