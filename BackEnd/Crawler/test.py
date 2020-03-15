import JOCrawler
# import tj
import WholeFoodsCrawler
import sys
# from webdriver_manager.chrome import ChromeDriverManager

if __name__ == '__main__':
	num = int(sys.argv[1])
	crawler = int(sys.argv[2])
	if crawler == 1:
		print("Test Trader Joe's")
		tj.go(True, num, 1, False)
		print('Please open TJ_store.csv to see the test sample')
	elif crawler == 2:
		print("Test Whole Foods")
		WholeFoodsCrawler.go(True, num)
		print('Please open WFStores.txt to see the store list')
	else:
		print("Test Jewel Osco")
		JOCrawler.go(True, num)
		print('Please open JOSCO_store.csv to see the store list')
	