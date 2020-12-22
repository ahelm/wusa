# wusa

running a docker container for GitHub Action workflow.

```sh
docker run -d --name github-runner \
  -e REPO_URL="https://github.com/ahelm/wusa" \
  -e RUNNER_NAME="foo-runner" \
  -e RUNNER_TOKEN="AAKKMGTUCOO3E4WQT23DFAK73OHJU" \
  -e RUNNER_WORKDIR="/tmp/github-runner-your-repo" \
  -e RUNNER_GROUP="my-group" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp/github-runner-your-repo:/tmp/github-runner-your-repo \
  myoung34/github-runner:latest
```