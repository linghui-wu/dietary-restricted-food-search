import JOCrawler
import TraderJoesCrawler
import WholeFoodsCrawler
import sys

if __name__ == '__main__':
	num = int(sys.argv[1])
	crawler = str(sys.argv[2])
	if crawler == 'TJ':
		print("Test Trader Joe's")
		TraderJoesCrawler.go(True, True, num, 2, False)
		print('Please open TJ_store.csv to see the test sample')
	elif crawler == 'WF':
		print("Test Whole Foods")
		WholeFoodsCrawler.go(True, num)
		print('Please open WF_store.csv to see the store list')
	else:
		print("Test Jewel Osco")
		JOCrawler.go(True, num)
		print('Please open JOSCO_store.csv to see the store list')
	