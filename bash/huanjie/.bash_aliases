#.bash_aliases

# initialize gitlog
source ~/.git-prompt.sh

# initialize gitlog
alias gitlog='git log --graph --full-history --all --color --pretty=format:"%x1b[31m%h%x09%x1b[32m%d%x1b[0m%x20%s"'

# setup alias
alias scratch="cd /global/scratch/$USER"
alias psudmant="cd /global/home/users/psudmant"
alias pscratch="cd /global/scratch/psudmant"
# Unix alias
# list all hidden files
alias lh="ls -d .?*"
alias ls="ls --color=always"
# list more information including size in MB
alias li="ls -lh --block-size=M"
# always use absolute path tracing down symbolic link
alias pwd="pwd -P"

# git alias, lazy functions
alias gadd="git add -A"
alias gcommit="git commit -m 'lazy commit'"
alias gpush="git push origin master"
alias gpull="git pull origin master"
alias gstatus="git status"
# remove added files
alias grm="git rm --cached"
# sync to the remote
alias gsync="
git fetch --all
git reset --hard origin/mast
git pull origin master
"
# download remote
alias gdown="
git stash
git pull origin master
git stash pop
"
# upload everything to remote
alias gup="
git add .
git commit -m 'lazy commit'
git push origin master
"
