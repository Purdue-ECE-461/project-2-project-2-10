import requests
import re

class connect_npm:
    def __init__(self, url):
        #After this is a useful identifier to plug into REST API:
        api_flag = "package/"
        #Search for index of API flag, and append everything after to API prefix:
        url = "https://api.npms.io/v2/package/" + url[len(api_flag) + url.find(api_flag)::] 

        #Contact REST API, and convert response to string:
        self.http_response = str(requests.get(url).content)
        #I faced some difficulties in converting this response to a parse-able JSON file, so I will be using regex/string manipulation within the response.

        #Get version number:
        self.version = self.get_version()
        
        #Get number of maintainers:
        self.maintainers = self.get_maintainers()

        #Get number of contributors:
        self.contributors = self.get_contributors()

        #Get license:
        self.license = self.get_license()

        #Count dependencies:
        self.dependencies = self.get_dependencies()

        #Count dev dependencies:
        self.dev_dep = self.get_dev_dep()

        #Count releases:
        self.releases = self.get_releases()

        #Check if there is a test script:
        self.test_script = self.check_test_script()

        #Count contributors
        self.commits = self.get_commits()

        #Get total downloads:
        self.downloads = self.get_downloads()

    def get_version(self):
        return re.search(r'"version":"(?P<version>[0-9]*.[0-9]*.[0-9]*)', self.http_response)["version"]

    def get_maintainers(self):
        maintainers = re.search(r'"maintainers":\[(?P<maint>.*)\],"', self.http_response)

        n_maintainers = 0
        for i in range(len(maintainers["maint"])):
            if maintainers["maint"][i] == ']' and maintainers["maint"][i+1] == ",":
                break
            elif maintainers["maint"][i] == '{':
                n_maintainers += 1

        return n_maintainers

    def get_contributors(self):
        contributors = re.search(r'"contributors":\[(?P<cont>.*)\],"', self.http_response)
        n_contributors = 0
        for i in range(len(contributors["cont"])):
            if contributors["cont"][i] == ']' and contributors["cont"][i+1] == ',':
                break
            elif contributors["cont"][i] == '{':
                n_contributors += 1
        return n_contributors

    def get_license(self):
        lice = re.search(r'"license":"(?P<lice>.*)","', self.http_response)
        i = 0
        for i in range(len(lice["lice"])):
            if lice["lice"][i] == "\"":
                break
        return lice["lice"][0:i]

    def get_dependencies(self):
        dependencies = re.search(r'"dependencies":{(?P<dep>.*)},".*', self.http_response)
        dep_count = 0
        for i in range(len(dependencies["dep"])):
            if dependencies["dep"][i] == "}":
                break
            elif dependencies["dep"][i] == ":":
                dep_count += 1

        return dep_count

    def get_dev_dep(self):
        dev_dep = re.search(r'"devDependencies":{(?P<dep>.*)}', self.http_response)
        dev_dep_count = 0
        for i in range(len(dev_dep["dep"])):
            if dev_dep["dep"][i] == "}":
                break
            elif dev_dep["dep"][i] == ":":
                dev_dep_count += 1

        return dev_dep_count

    def get_releases(self):
        releases = re.search(r'"releases":\[(?P<rel>.*)', self.http_response)
        rel_count = 0
        for i in range(len(releases["rel"])):
            if releases["rel"][i] == "]":
                break
            elif releases["rel"][i] == "{":
                rel_count += 1

        return rel_count

    def check_test_script(self):
        test_script = re.search(r'"hasTestScript":(?P<flag>[a-z])', self.http_response)
        test_script = True if test_script["flag"] == "t" else False
        return test_script

    def get_commits(self):
        commit_count = re.findall(r'"commitsCount":(?P<num>[0-9]+)', self.http_response)
        num_commits = sum([int(i) for i in commit_count])
        return num_commits

    def get_downloads(self):
        downloads = re.search(r'"downloadsCount":(?P<num>[0-9]*\.[0-9]*)', self.http_response)
        if downloads == None:
            downloads = re.search(r'"downloadsCount":(?P<num>[0-9]*)', self.http_response) 
        return int(float(downloads["num"]))
    
    def check_attributes(self):
        print(self.version)
        print(self.maintainers)
        print(self.contributors)
        print(self.license)
        print(self.dependencies)
        print(self.dev_dep)
        print(self.releases)
        print(self.test_script)
        print(self.commits)
        print(self.downloads)
