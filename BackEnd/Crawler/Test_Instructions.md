# Test Instructions



## 1. Getting Started



Once you have cloned the repository locally, you will have a directory named `Crawler`. That directory will include:

- `JOCrawler.py`: Jewel Osco's web crawler

- `TraderJoesCrawler.py`: Trader Joe's web crawler

- `WholeFoodsCrawler.py`: Whole Foods' web crawler

- `test.py`: test code for the crawlers

### Some declarations for the design of test

1. In order to show our crawlers can run successfully, we didn't hide the browser during the web scraping process, which may make you feel dazzled. If so, please forgive us! 

2. We didn't write a test for getting the stores' information, because it only take a few seconds to get those files. Each time you run the test, you can get the csv file of store info in the directory. Please refer to the notification that showed in the test result to get the store info.

3. Testing `TraderJoesCrawler` and `JOCrawler` may take some time and `WholeFoodsCrawler` is the fastest while testing among the three crawlers.

4. Due to the special situation we have recently, the stock of stores are changing rapidly, thus you may not get the desired number of items in the test result. But we can ensure that you can get a small sample of data after running the test code.

5. **Web Scraping** performance highly depends on the network. Please make sure that you have a **good network** before you run the test.

### Prerequisites

Please make sure **you have installed all of the modules mentioned in `requirements.txt`**. 

### Testing code

For testing, please run the following command from the linux command-line:

```shell
$ python3 test.py NUMBER STORE
```

where `NUMBER` is the number of items you want to get for the sample. Due to the consideration of time, please enter a number smaller than 10. 

`STORE` is the store (or the crawler) you want to test, which has three options:

- TJ (stands for testing Trader Joes Crawler)
- WF (stands for testing Whole Foods Crawler)
- JO (stands for testing Jewel Osco Crawler)



## 2. Examples



This is an example of how you may test the crawlers after clone our repository locally. To get a test data sample for each of the three grocery stores (Trader Joe's, Whole Foods and Jewel Osco), you can run `test.py`follow these simple example steps.

### Testing Trader Joe's Crawler

`$ python test.py 3 TJ`

Then you will get a small sample of data that scraped from Trader Joe's website showing on your linux command-line. 

**--Special Notice:--**

1. Regrettably, you can't set the number of testing items that you want to get for this crawler, because `TraderJoesCrawler` was built based on three approaches, each of which can obtain a part of items in this store. You can only set the NUMBER to be as small as possible (like 1 or 2) in order to get a relatively small size of test sample. But you can't limit the number of items you get from the test.

2. You may get some non-food items in the test result, whose detailed information are `NaN`. This is correct because we will clean and drop these data in the subsequent data cleaning process.

### Testing Whole Foods' Crawler

`$ python test.py 3 WF`

Then you will get 3 pieces of sample data.

### Testing Jewel Osco's Crawler

`$ python test.py 3 JO`

After running this code, you will see following web page, which requires you to log in.

![Alt text](https://user-images.githubusercontent.com/54608538/76725932-b664e700-671d-11ea-938c-e6b043ef3e92.png)

Click **log in** to type in the account

![Alt text](https://user-images.githubusercontent.com/54608538/76725966-d0062e80-671d-11ea-970b-227552a0a02a.png)

Here we provide you a testing account for logging in.

- Email Address: mingtao0123@gmail.com
- Password: 123456

Please make sure you successfully log into the account within 30s after the chrome pop up. Otherwise, there will be an error in the test.

Then you will get 3 pieces of sample data in this test.

**--Special Notice:--**

Testing JOCrawler may take some time. This is beacause we need to get the labels for all of the items in the department first and then get the food item information. Please keep patient while testing JOCrawler! :-P



