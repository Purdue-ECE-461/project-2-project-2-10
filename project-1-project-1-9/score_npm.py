from connect_npm import *
from readEnvironment import *
import re

logFile_ptr = open(LOG_FILE, "w")

class npm_score:
    def __init__(self, npm):
        #Assign npm attribute object to self:
        self.npm = npm

        
        if LOG_LEVEL == "1":
            message = f"Scoring the API accessed by npm"
            logFile_ptr.write(message)
        if LOG_LEVEL == "2":
            message = f"Scoring the API accessed by npm, using urllib.parse package to break down the \nurl and base64 package to convert the package.json file info into a string"
            logFile_ptr.write(message)

        #Score correctness:
        self.cor_score = self.score_correctness()

        #Score rampup:
        self.ramp_score = self.score_rampup()

        #Score busfactor:
        self.bus_score = self.score_busfactor()

        #Score responsiveness:
        self.resp_score = self.score_responsiveness()

        #Score license compatability:
        self.lic_score = self.score_liccompat()

        #Score cumulative:
        self.cumulative = self.score_cumulative()

        #Unscale scores now that cumulative has been calculated:
        self = self.unscale_scores()

    def unscale_scores(self):
        scale_factors = {
            "bus":5, #Bus factor
            "res":4, #responsiveness
            "ram":3, #Ramp up
            "cor":2, #Correctness
            "lic":1 #License
        }

        self.cor_score /= scale_factors["cor"]
        self.ramp_score /= scale_factors["ram"]
        self.bus_score /= scale_factors["bus"]
        self.resp_score /= scale_factors["res"]
        self.lic_score /= scale_factors["lic"]
        return self

    def scale_scores(self, item, score):
        if score > 1:
            score = 1
        elif score < 0:
            score = 0

        scale_factors = {
            "bus":5, #Bus factor
            "res":4, #responsiveness
            "ram":3, #Ramp up
            "cor":2, #Correctness
            "lic":1 #License
        }

        return score * scale_factors[item]

    def score_correctness(self):
        #Error status
        #Major.Minor.Patch

        first_dot = self.npm.version.find(".")
        secont_dot = self.npm.version.rfind(".")
        major = int(self.npm.version[0:first_dot])
        minor = int(self.npm.version[first_dot+1:secont_dot])
        patch = int(self.npm.version[secont_dot+1::])
        denominator = major if major != 0 else 1
        denominator *= minor if major != 0 else 1
        denominator *= patch if major != 0 else 1
        score = 1 - ((major + minor + patch) / (denominator+1))
        if LOG_LEVEL == "1":
            message = "Running scoreCorrectness"
            logFile_ptr.write(message)
        if LOG_LEVEL == "2":
            message = "Running scoreCorrectness and calculating correctness score from scoreCorrectness function using \nthe current version \nof the API and comparing how many versions have been made for the same release "
            logFile_ptr.write(message)
        return self.scale_scores("cor", score)

    def score_rampup(self):
        #Documentation/learnability
        score = self.npm.dev_dep / (self.npm.dependencies+1)
        if LOG_LEVEL == "1":
            message = "Running scoreRampup"
            logFile_ptr.write(message)
        if LOG_LEVEL == "2":
            message = "Running scoreRampup and getting RampUp score from scoreRampup function using devDependencies and \ndependencies of the API "
            logFile_ptr.write(message)
        return self.scale_scores("ram", score)

    def score_busfactor(self):
        #People
        score = self.npm.maintainers / (self.npm.contributors+1)
        if LOG_LEVEL == "1":
            message = "Running scoreBusFactor"
            logFile_ptr.write(message)
        if LOG_LEVEL == "2":
            message = "Running scoreBusFactor and getting BusFactor score from scoreBusFactor function \nby running get_assignees and get_contributors for the API "
            logFile_ptr.write(message)
        return self.scale_scores("bus", score)

    def score_responsiveness(self):
        #Error response
        score = self.npm.releases / (self.npm.commits+1)
        if LOG_LEVEL == "1":
            message = "Running scoreResponsiveness"
            logFile_ptr.write(message)
        if LOG_LEVEL == "2":
            message = "Running scoreResponsiveness and getting RampUp score from scoreResponsiveness function \nusing get_releases and get_commits for the API "
            logFile_ptr.write(message)
        return self.scale_scores("res", score)

    def score_liccompat(self):
        compatible_licenses = [
            "Public Domain",
            "MIT",
            "X11",
            "BSD-new",
            "Apache 2.0",
            "LGPLv2.1",
            "LGPLv2.1+",
            "LGPLv3",
            "LGPLv3+",
        ]
        score = 0
        for i in compatible_licenses:
            if score:
                break
            score = 0 if re.search(i, self.npm.license) == None else 1

        if LOG_LEVEL == "1":
            message = "Getting License compatibility from scoreLicCompat function"
            logFile_ptr.write(message)
        if LOG_LEVEL == "2":
            message = "Comparing a set of pre-chosen licenses to compare with the the license type of current API"
            logFile_ptr.write(message)
        return self.scale_scores("lic", score)

    def score_cumulative(self):
        return (self.cor_score + self.ramp_score + self.bus_score + self.resp_score + self.lic_score) / 15

