# Learn CI/CD by Deploying a Python App to AWS EC2

A complete, beginner-friendly project. By the end you will understand what CI/CD
really is **and** you will have a working pipeline: every time you push code to
GitHub, it gets tested automatically and deployed to a live server on AWS EC2.

Everything here uses **only free tools**.

---

## Part 1 — Understanding CI/CD (the easy way)

### The problem CI/CD solves

Imagine you wrote some code and you want it running on a server so other people
can use it. The old, manual way looks like this:

1. You finish writing code on your laptop.
2. You manually test it (and sometimes forget to).
3. You log into the server.
4. You copy the new files over.
5. You restart the app.
6. You hope nothing broke.

You do this *every single time* you change something. It is slow, boring, and
easy to make mistakes — like deploying code that has a bug, or forgetting a step.

**CI/CD is a robot that does steps 2 to 6 for you, automatically, every time.**

### What the letters mean

Think of a factory assembly line. Your code goes in one end, and a working,
deployed app comes out the other end. That assembly line is called a **pipeline**.

- **CI = Continuous Integration**
  The "test it" half. Every time you add code, a robot automatically *builds*
  it and *runs your tests*. "Integration" means: your new code is constantly
  being combined with the rest of the project and checked, so problems are
  caught early instead of piling up.

- **CD = Continuous Delivery / Continuous Deployment**
  The "ship it" half.
  - *Continuous Delivery* = the code is automatically prepared and ready to
    release, but a human clicks the final "deploy" button.
  - *Continuous Deployment* = even that final button is automatic. Push code,
    and it goes live with no human needed.
  In this project we build **Continuous Deployment** (fully automatic).

### A simple analogy

CI/CD is like a **dishwasher**. Before, you washed every dish by hand (manual
deployment). Now you just load the dishes and press start. The machine rinses,
washes, and dries automatically (test, build, deploy). You only step in if
something is wrong.

### What is a "pipeline" exactly?

A pipeline is just a **list of steps that run in order, automatically**, when
something triggers it (in our case: pushing code to GitHub). If any step fails,
the pipeline stops — so broken code never reaches your users. Our pipeline has
two big stages:

```
   You push code to GitHub
            |
            v
   +------------------+        +-------------------+
   |   STAGE 1: CI    |        |   STAGE 2: CD     |
   |  (test the code) | -----> |  (deploy to EC2)  |
   |                  | passes |                   |
   | - install deps   |        | - SSH into server |
   | - check style    |        | - pull new code   |
   | - run tests      |        | - restart the app |
   +------------------+        +-------------------+
        |  fails                       |
        v                              v
   STOP. Nothing               App is LIVE on
   gets deployed.              your EC2 server.
```

---

## Part 2 — The tools we use (all free)

| Job in the pipeline      | Tool we use      | Why / cost |
|--------------------------|------------------|------------|
| Write the app            | Python + Flask   | Free, simple web framework |
| Store + version code     | Git + GitHub     | Free |
| Run the pipeline         | GitHub Actions   | Free (2,000 min/month free; unlimited for public repos) |
| The live server          | AWS EC2 (t2.micro / t3.micro) | Free tier for 12 months |
| Production web server    | Gunicorn         | Free |
| Keep app running 24/7    | systemd          | Built into Linux, free |
| Test the code            | pytest           | Free |
| Check code style         | flake8           | Free |

**GitHub Actions** is the robot/engine that runs our pipeline. It is built into
GitHub. You describe your pipeline in a file (`.github/workflows/deploy.yml`) and
GitHub runs it for you on free machines it provides.

---

## Part 3 — The files in this project (what each one does)

```
flask-cicd-ec2/
├── app.py                       # The actual web app
├── test_app.py                  # Tests (the CI stage runs these)
├── requirements.txt             # Python libraries the app needs
├── gunicorn_config.py           # Settings for the production server
├── myapp.service                # Keeps the app running on EC2
├── .gitignore                   # Files Git should ignore
└── .github/
    └── workflows/
        └── deploy.yml           # THE PIPELINE itself
```

The single most important file is **`.github/workflows/deploy.yml`** — that *is*
your CI/CD pipeline. Open it; every line has a comment explaining it.

---

## Part 4 — Step-by-step setup

You need: a free **GitHub account** and a free **AWS account**.

### Step 1: Try the app on your own computer first

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000` in a browser. You should see a JSON message.
Stop it with `Ctrl + C`. Run the tests too:

```bash
pip install pytest flake8
pytest -v
```

Seeing tests pass locally helps you understand what the CI stage will do.

### Step 2: Launch a free EC2 server on AWS

1. Log into the **AWS Console** → search **EC2** → **Launch instance**.
2. Name it (e.g. `cicd-server`).
3. **AMI** (the operating system): choose **Ubuntu** (Server, free-tier eligible).
4. **Instance type**: choose **t2.micro** or **t3.micro** (marked "Free tier eligible").
5. **Key pair**: click **Create new key pair**, name it `cicd-key`, type **RSA**,
   format **.pem**. Download the `.pem` file and keep it safe — you'll need it.
6. **Network settings** → **Edit** → add security group rules to allow:
   - **SSH** (port 22) — so you and GitHub can connect.
   - **Custom TCP**, port **5000** — so the web app is reachable. Source: `0.0.0.0/0`.
7. Click **Launch instance**.
8. After it starts, copy its **Public IPv4 address** (e.g. `13.234.x.x`).

### Step 3: Connect to your EC2 server and prepare it

From your computer's terminal (replace the path and IP):

```bash
chmod 400 cicd-key.pem
ssh -i cicd-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

Now you're inside the server. Install what we need:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

### Step 4: Set up the systemd service on EC2

This makes your app run forever and restart on crash or reboot.
While connected to EC2, create the service file:

```bash
sudo nano /etc/systemd/system/myapp.service
```

Paste the contents of this project's `myapp.service` file, save (Ctrl+O, Enter)
and exit (Ctrl+X). Then turn it on:

```bash
sudo systemctl daemon-reload
sudo systemctl enable myapp
```

It will fail to *start* right now because the code isn't there yet — that's fine.
The pipeline will deliver the code and start it. You can log out of EC2 now
(`exit`).

### Step 5: Put your code on GitHub

On GitHub, create a new empty repository named `flask-cicd-ec2`.
Then from this project folder on your computer:

```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/flask-cicd-ec2.git
git push -u origin main
```

> Important: open `.github/workflows/deploy.yml` and replace `YOUR_USERNAME`
> with your real GitHub username on the `git clone` line.

### Step 6: Give GitHub the keys to your server (Secrets)

The pipeline needs to log into EC2. We store the login details as **encrypted
secrets** so they never appear in your code. On GitHub:

Go to your repo → **Settings** → **Secrets and variables** → **Actions** →
**New repository secret**. Add these three:

| Secret name   | Value |
|---------------|-------|
| `EC2_HOST`    | Your EC2 public IP address |
| `EC2_USER`    | `ubuntu` |
| `EC2_SSH_KEY` | The **entire contents** of your `cicd-key.pem` file (open it in a text editor and copy everything, including the `-----BEGIN...` and `-----END...` lines) |

> Why secrets? If you ever wrote your private key directly in a file in your
> repo, anyone who sees your code could take over your server. Secrets keep it
> encrypted and hidden.

### Step 7: Watch the magic happen

You already pushed code in Step 5, so the pipeline likely already ran once. To
trigger it again, just change something and push:

```bash
git commit --allow-empty -m "trigger pipeline"
git push
```

On GitHub, click the **Actions** tab. You'll see your pipeline running live.
Click it to watch each step turn green:

1. CI job installs Python, lints, and runs tests.
2. If tests pass, the CD job SSHes into EC2 and deploys.

When it finishes, open `http://YOUR_EC2_PUBLIC_IP:5000` in your browser. Your app
is live — and it got there with zero manual deployment steps. 🎉

---

## Part 5 — Deep dive: what actually happens, line by line

When you run `git push`, here is the full chain of events:

1. **Trigger.** GitHub sees a push to `main`. The `on: push: branches: [main]`
   part of `deploy.yml` matches, so it starts the pipeline.

2. **GitHub gives you a free computer.** `runs-on: ubuntu-latest` means GitHub
   spins up a brand-new, clean Linux machine just for this run. It is thrown
   away afterward, so every run is fresh and reproducible.

3. **CI job runs:**
   - `actions/checkout@v4` downloads your code onto that machine.
   - `setup-python` installs Python 3.11.
   - `pip install -r requirements.txt` installs your app's libraries.
   - `flake8` checks your code style. Bad style → pipeline fails here.
   - `pytest` runs your tests. Any failing test → pipeline fails here.
   - **This is the safety gate.** Broken code stops here and never deploys.

4. **CD job runs (only because `needs: test` passed):**
   - `appleboy/ssh-action` is a ready-made tool that opens an SSH connection.
   - It uses your three secrets (`EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`) to log
     into your server securely.
   - The `script:` block runs *on your EC2 server*: it pulls the newest code,
     installs dependencies, and runs `sudo systemctl restart myapp`.

5. **App restarts with new code.** systemd restarts Gunicorn, which serves your
   updated Flask app. Users now see the new version.

### Why each piece exists (so it's not magic)

- **Why Gunicorn and not `python app.py`?** Flask's built-in server is a toy for
  local testing — single-threaded and not secure for the open internet. Gunicorn
  is a real production server that handles many users at once.
- **Why systemd?** If your app crashes at 3 a.m., systemd restarts it instantly.
  If the server reboots, systemd starts your app again automatically. Without it,
  your app would just stay down.
- **Why tests before deploy?** This is the entire point of CI/CD. Automation is
  only safe if there's a gate that blocks bad code. Tests are that gate.

---

## Part 6 — Troubleshooting

| Problem | Likely cause & fix |
|---------|--------------------|
| Pipeline fails at "Run tests" | A test is failing — read the red log, fix the code, push again. Working as intended. |
| Pipeline fails at "Deploy to EC2" with a connection error | Check `EC2_HOST` secret has the right IP, port 22 is open in the security group, and `EC2_SSH_KEY` is the *full* .pem contents. |
| Pipeline passes but website won't load | Port **5000** must be open in the EC2 security group. Also run `sudo systemctl status myapp` on the server to see if the app started. |
| `systemctl restart` fails with "permission denied" | The `ubuntu` user needs sudo (it has it by default on Ubuntu EC2). |
| EC2 IP changed after a stop/start | A stopped instance gets a new public IP. Update the `EC2_HOST` secret, or attach a free **Elastic IP** to keep it fixed. |

Useful commands while SSHed into EC2:

```bash
sudo systemctl status myapp        # is the app running?
sudo journalctl -u myapp -n 50     # see the app's recent logs
```

---

## Part 7 — Where to go next (level up)

Once the basics click, try adding these to deepen your CI/CD knowledge:

1. **Add Nginx** as a reverse proxy so users visit port 80 (normal web port)
   instead of 5000, and you can add a free HTTPS certificate (Let's Encrypt).
2. **Add a "staging" environment** — deploy to a test server first, then to
   production. This teaches the *Delivery vs Deployment* distinction.
3. **Add a manual approval step** in GitHub Actions before production deploy —
   that converts your Continuous Deployment into Continuous Delivery.
4. **Dockerize the app** — package it into a container so "works on my machine"
   becomes "works everywhere." Then deploy the container.
5. **Add notifications** — make the pipeline message you on Slack/email when a
   deploy succeeds or fails.

---

## Quick glossary

- **Repository (repo):** the folder of your code, tracked by Git/GitHub.
- **Commit:** a saved snapshot of your code.
- **Push:** uploading your commits to GitHub.
- **Workflow:** the file describing your pipeline (`deploy.yml`).
- **Job:** a group of steps in a workflow (we have `test` and `deploy`).
- **Step:** a single action inside a job.
- **Runner:** the machine GitHub provides to run your pipeline.
- **Secret:** an encrypted value (like a password) stored safely in GitHub.
- **SSH:** the secure way to remotely log into a server.
- **EC2:** Amazon's rentable virtual servers.
- **AMI:** the operating system image your EC2 server boots from.
```
