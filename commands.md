pyenv local 3.14.2

pyenv exec python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

pip install -r requirements-dev.txt

uvicorn blogapi.main:app --reload


-----Tests---
pytest

pytest -v

# shows the fixtures available. It also includes built in fixtures ie from anyio.pytest_plugin 
pytest --fixtures

# shows the fixtures used per test
pytest --fixtures-per-test

# run a specific test file
pytest blogapi/tests/test_security.py
pytest blogapi/tests/routers/test_post.py
pytest blogapi/tests/routers/test_user.py
pytest blogapi/tests/test_tasks.py

# run a specific test function
pytest -k test_register_user

## prvide more deails on the error that has been truncated
pytest -vv blogapi/tests/routers/test_user.py


# Pro-Tip: Generating the file
# If you already have your environment set up and working, don't write the file by hand. Run this command to generate it perfectly based on what's actually installed:
pip freeze > requirements-test.txt

# Link to Git Cheat sheet 
https://education.github.com/git-cheat-sheet-education.pdf

# create new branch
git branch [branch-name]

git fetch

# switch branch
git checkout david/add-link-test-workflow

# delete branch
git branch -D <branch_name>

# list branches
git branch


# Process of merging a feature branch to the main branch
1. Switch to the target branch: Move to main so you can bring the changes into it.
git checkout main

2 Sync with the server: Always pull the latest changes from GitHub/GitLab first to avoid working on an outdated version of main.
git pull

3. Perform the merge: Execute the merge command pointing to your feature branch.
git merge feature-branch-name

Note: Refer to "Merging via Pull Request (The "Industry Standard" Way)" at the bottom

#Syncing your work to the Remote (Pushing)
# 1. Stage the changes
git add .

# 2. Commit with a meaningful message
git commit -m "feat: add validation to user registration"

# 3. Push to the server
git push 

4. Push to the server: The merge happened on your local machine. Now, update the remote repository.
git push origin main


# Merging via Pull Request (The "Industry Standard" Way)
In most modern teams, you actually omit the manual git merge and git push on your local machine entirely. Instead:

You git push your feature branch to the server.

You open a Pull Request (PR) on GitHub.

You click the "Merge" button on the website.

# Tutorials on Building using docker with github actions
# Build CI/CD Pipeline with GitHub Actions | Docker Image to DockerHub
https://www.youtube.com/watch?v=MRBzHJaDRqA