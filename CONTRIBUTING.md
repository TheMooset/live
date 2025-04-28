# Contributing to the LastActivity project
We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Fixing a bug
- Discussing the current state of the code
- Proposing new features
- Becoming a maintainer

## We Develop with Gitlab
We use github to host code, to track issues and feature requests, as well as accept pull requests.

## We Use [Github Flow](https://guides.github.com/introduction/flow/index.html), So All Code Changes Happen Through Pull Requests
Pull requests are the best way to propose changes to the codebase (we use [Github Flow](https://guides.github.com/introduction/flow/index.html)). We actively welcome your pull requests:

1. Pull the repo and create your branch from `master`.
2. If you've added code that should be tested, add tests.(We use [pytest](https://docs.pytest.org/en/stable/)) 
3. If you've changed APIs, make sure you follow [fastAPI documentations](https://fastapi.tiangolo.com/tutorial/schema-extra-example/) to update the swagger.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!
7. We use CI/CD for deploying the project, so use the CI/CD section in gitlab for merging the branches
7. After making sure that your code works, merge it with `dev` branch
8. Check if everything is ok in the `dev` branch in [staging](https://basalam.dev/explore)
9. If everything works, merge the `dev` branch in to `master`

## Commit Conventions:
Use this convention to commit changes:
```git commit
type: subject
-- a blank line --
Body
```
#####  Type:
- feat: A new feature
- fix: A bug fix
- docs: Changes in documentations
- style: Style changes, formatting, missing whitespaces
- refactor: Code changes that neither fixes a bug or adds a feature
- perf: Changes that improves performance
- test: Add missing tests
- chore: Changes the build process

#####  Subject:
The subject contains a short description of the applied changes

#####  Body (optional):
Must begin after a blank line after the subject. Can provide additional contextual information.
For breaking changes, the body must start with `"BREAKING CHANGES:"`

## Look for exceptions after deploying
Always check [Explore project in Sentry](https://sentry.basalam.com/organizations/sentry/issues/?project=5) for any exceptions 

## Use a Consistent Coding Style
We use [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/). So make sure you follow it as well.

## License
By contributing, you agree that your contributions will be licensed under Basalam NDA rules.

#### Note
Check `README.md` to get more info and see how things work 
