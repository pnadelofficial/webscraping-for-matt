from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
tqdm.pandas() 
import warnings
warnings.filterwarnings("ignore")
from datetime import date

chrome_options = Options()
chrome_options.add_argument("--headless")
wd = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

#la republica
wd.get('https://larepublica.pe/')

headlines = []
headlines.append(wd.find_element(By.CLASS_NAME, 'spotlightPrincipalContentHeadlineFirst'))
for element in wd.find_elements(By.CLASS_NAME, 'spotlightPrincipalContentHeadlineSecond'):
  headlines.append(element)
for element in wd.find_elements(By.CLASS_NAME, 'discover__headline'):
  headlines.append(element)
for element in wd.find_elements(By.XPATH, "//h2[@class='listNotes__headline']/a"):
  headlines.append(element)

hl_dict = {}
for element in headlines: 
  if not isinstance(element.get_attribute('outerHTML'), type(None)):
    soup = BeautifulSoup(element.get_attribute('outerHTML'), features='html.parser') 
    if '/videos/' not in soup.a['href']:
      if 'https://larepublica.pe/' in soup.a['href']: 
        hl_dict[soup.a.text] = soup.a['href'] 
      else:
        hl_dict[soup.a.text] = f"https://larepublica.pe{soup.a['href']}"
larepublica_df = pd.DataFrame.from_dict(hl_dict, orient='index').reset_index().rename(columns={'index':'headline',0:'link'})

def get_text(link):
  article_wd = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

  paragraphs = [] 
  article_wd.get(link)
  for p in article_wd.find_elements(By.TAG_NAME, 'p')[:-2]:
    if (p.text != ''):
      paragraphs.append(p.text)
  return ' '.join(paragraphs) 

larepublica_df['article_text'] = larepublica_df['link'].progress_apply(get_text)
larepublica_df.to_csv(f'raw_data/LR{date.today()}.csv',index=False)