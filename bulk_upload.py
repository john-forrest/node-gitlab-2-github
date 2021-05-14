#!/usr/bin/env python

import sys
import os
import json

# Utility function from https://stackoverflow.com/questions/2597278/python-load-variables-in-a-dict-into-namespace
class Bunch(object):
  def __init__(self, adict):
    self.__dict__.update(adict)

# repo_table is read from json, should be an array of dicts. Each
# dict is:
#   name           (logical name of the repo - used in tracing)
#   gitlabRepoName (name of repo on gitlab including group)
#   gitlabRepoId   (id of repo - assumed to be correct - no check)
#   githubRepoName (name of repo on github including group)

with open("repo_table.json") as json_file:
    repo_table = json.load(json_file)

# Check for duplications - most likely error in the original
bad = False
for entry in ("name", "gitlabRepoName", "gitlabRepoId", "githubRepoName"):
    entries = [repo[entry] for repo in repo_table]
    for ele in list(set(entries)): # equiv of unique(entries)
        if entries.count(ele) > 1:
            print(f"duplicate {entry} entry found: {ele}")
            bad = True
if bad:
    sys.exit(-1)

with open("template_settings.ts") as template_file:
    template = template_file.read()

# Generate string from repo table to be used as projectmap -
# comma separated pairs of gitlabRepoName:githubRepoName. This
# will be the same for each project.
projectMap = ""
for rep in repo_table:
    repo = Bunch(rep)
    projectMap += f"'{repo.gitlabRepoName}': '{repo.githubRepoName}',\n"

for rep in repo_table:
    repo = Bunch(rep)
    print(f"repo: {repo.name}")

    githubOwner, githubRepo = repo.githubRepoName.split('/') # separate foo/bar into foo and bar

    # Now replace strings in template file
    settings = template.replace("__GITLAB_PROJECT_ID__", str(repo.gitlabRepoId)). \
        replace("__GITHUB_OWNER__", githubOwner). \
        replace("__GITHUB_REPO__", githubRepo). \
        replace("__PROJECT_MAP__", projectMap)

    with open("settings.ts", "w") as settings_file:
        settings_file.write(settings)

    os.system("npm start")


