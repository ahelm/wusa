# wusa

running a docker container for GitHub Action workflow.

```sh
docker run --rm --name github-runner \
  -e REPO_URL="https://github.com/ahelm/wusa" \
  -e RUNNER_NAME="github-runner" \
  -e RUNNER_TOKEN="AAKKMGTAVI5VYNKFJENUA3274QMCQ" \
  -e RUNNER_WORKDIR="/Users/anton/Documents/Projects/wusa" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /Users/anton/Documents/Projects/wusa:/Users/anton/Documents/Projects/wusa \
  myoung34/github-runner:latest
```
