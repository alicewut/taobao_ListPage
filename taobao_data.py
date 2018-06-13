from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
from settings import KeyWord, dbInfo
from lxml import etree
import pymongo
import time



def getOnePage(page):
	"""
	:param page:页码
	:return: 页面源代码，传入解析函数
	"""
	try:
		print('正在爬取第{}页'.format(page))
		url = 'https://s.taobao.com/search?q=' + quote(KeyWord)
		browser.get(url)
		# 访问非第一页需要对页面进行跳转
		if page > 1:
			# 等待页码输入框加载完成
			input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[class="input J_Input"]')))
			# 等待页码提交按钮加载完成
			submit = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span[class="btn J_Submit"]')))
			# 清空页码输入框
			input.clear()
			# 输入当前请求的页码
			input.send_keys(str(page))
			# 点击跳转按钮
			submit.click()
		# 等待加载分页的当前页码与请求的页码一致,否则异常重试
		wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page)))
		# 等待页面的列表加载完成
		wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.grid.g-clearfix')))
		parsePage()
	except Exception as e:
		print(e)
		getOnePage(page)
	
def parsePage():
	# 获取网页源代码
	html = browser.page_source
	html = etree.HTML(html)
	# 匹配每个商品的html代码块此处是div
	itemList = html.xpath('//div[@id="mainsrp-itemlist"]//div[@class="grid g-clearfix"]//div[@class="items"]//div[starts-with(@class, "item")]')
	
	# 遍历获取数据，字典格式
	for item in itemList:
		productInfo = {
			# 商品大图
			'pic': 'http:' + item.xpath('.//div[@class="pic-box-inner"]/div[@class="pic"]//img/@data-src')[0],
			# 价格
			'price': item.xpath('./div[starts-with(@class,"ctx-box")]/div[1]/div[@class="price g_price g_price-highlight"]/strong/text()')[0],
			# 销售量
			'totalorder': item.xpath('./div[starts-with(@class,"ctx-box")]/div[1]/div[@class="deal-cnt"]/text()')[0].split('人')[0],
			# 商品名
			'title': ''.join(item.xpath('./div[starts-with(@class,"ctx-box")]/div[2]/a/text()')).replace(' ', '').strip('\n'),
			# 店铺名
			'shop': item.xpath('./div[starts-with(@class,"ctx-box")]/div[3]/div[@class="shop"]/a/span[2]/text()')[0],
			# 店铺地址
			'addr': item.xpath('./div[starts-with(@class,"ctx-box")]/div[3]/div[@class="location"]/text()')[0],
		}
		# 存储至Mongo
		storage(productInfo)
		
	
	
	


def storage(item):
	try:
		if db[dbInfo['mongoCollection']].insert(item):
			print('插入成功')
	except Exception as e:
		print(e)
		print('数据插入失败')


def main():
	for i in range(1,101):
		getOnePage(i)
	browser.close()
	client.close()
	
	


if __name__ == '__main__':
	# 定义浏览器信息
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--disable-gpu')
	chromedriver = r"F:\脱产学习2017.10.27\兄弟连python\haolong\alice_code\scrapy_spider\spider_env\Scripts\chromedriver.exe"
	browser = webdriver.Chrome(executable_path=chromedriver,chrome_options=options)
	# browser = webdriver.Chrome()
	# browser.set_window_size(1280, 800)
	wait = WebDriverWait(browser, 50)
	
	# 连接mongo数据库
	client = pymongo.MongoClient(dbInfo['mongoUrl'], dbInfo['mongoPort'], username=dbInfo['mongoUser'],password=dbInfo['mongoPasswd'])
	# 切换库
	db = client[dbInfo['mongoDB']]
	
	# 执行主函数
	main()