# project-1 team 9

## How to use (in bash):

### To install dependencies:
"./run install"
Please see milestone 4 with regards to this.  Though this code will need to be run, it will not need to be run individually.

Sample Output (to Stdout):
7 dependencies installed...

### To run tests:
"./run test"

Sample Output (to Stdout):

Total: 10
Passed: 9
Coverage: 90%
9/10 test cases passed. 90% line coverage achieved.

### To run on repositories:
Input a list of github/npm urls to check in a .txt file with each url separated by newlines.
then execute "./run [file path and name].txt"

Sample Command: "./run /Users/myUser/IdeaProjects/files/sample-url-file.txt"
Where the content enclosed in quotation marks is the absolute path to a file containing the list of urls.
A sample file with name "sample-input" is also provided

Sample Output (to Stdout):

URL NET_SCORE RAMP_UP_SCORE CORRECTNESS_SCORE BUS_FACTOR_SCORE RESPONSIVE_MAINTAINER_SCORE LICENSE_SCORE
https://github.com/nullivex/nodist 0.9 0.5 0.7 0.3 0.4 1
https://www.npmjs.com/package/browserify 0.76 0.5 0.7 0.3 0.6 1
https://github.com/cloudinary/cloudinary_npm 0.6 0.5 0.7 0.3 0.2 1
https://github.com/lodash/lodash 0.5 0.5 0.3 0.7 0.6 1
https://www.npmjs.com/package/express 0 0.5 0.7 0.3 0.6 0
