import requests
from score_npm import *
from connectgithub import *

class Tests:
    def __init__(self):
        self.test_url = "https://api.npms.io/v2/package/express"
        self.cumulative_score = 0
        #First line of test output:
        print("Total: 3")

        #Test http GET (in requests library)
        self.http_get_test()

        if self.http_score == 0:
            print("Passed: 0")
            print("Coverage: 0%")
            print("0/3 test cases passed.  0% coverage achieved.")
            return 

        #Test that the data retrieval
        self.npm_data_test()
        if self.npm_score == 0:
            print("Passed: 1")
            print("Coverage: 33%")
            print("1/3 test cases passed.  33% coverage achieved.")
            return

        self.git_data_test()
        if self.git_score == 0:
            print("Passed: 2")
            print("Coverage: 66%")
            print("2/3 test cases passed.  66% coverage achieved.")
            return

        print("Passed: 3")
        print("Coverage: 100%")
        print("3/3 test cases passed.  100% coverage achieved.")
        return


    def http_get_test(self):
        try:
            requests.get(self.test_url)
        except Exception as e:
            self.http_score = 0
            return self
        
        self.http_score = 1
        return self

    def npm_data_test(self):
        try:
            npm_score(connect_npm("https://www.npmjs.com/package/express"))
        except Exception as e:
            self.npm_score = 0
            return self
        
        self.npm_score = 1
        return self

    def git_data_test(self):
        try:
            scoreGithub("https://github.com/cloudinary/cloudinary_npm")
        except Exception as e:
            self.git_score = 0
            return self

        self.git_score = 1
        return self
