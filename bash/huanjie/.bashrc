# .bashrc

# DO NOT echo anything, otherwise scp won't work
# echo ".bashrc is sourced"

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# Source global aliases
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# Source global aliases
if [ -f ~/.bash_functions ]; then
    . ~/.bash_functions
fi

# Source slurm utilities
if [ -f ~/.bash_savio ] & [[ $HOSTNAME != dtn* ]]; then
    . ~/.bash_savio
fi

# Store some useful path to data, code, and misc
if [ -f ~/.bash_path ]; then
    . ~/.bash_path
fi

# Source global environment variables and modules
if [ -f ~/.profile ]; then
    . ~/.profile
fi

# load vim in dtn node
# it's only for data transfer
if [[ $HOSTNAME = dtn* ]]; then
    # echo "only load vim in dtn"
    module use /global/software/sl-7.x86_64/modfiles/langs /global/software/sl-7.x86_64/modfiles/tools /global/software/sl-7.x86_64/modfiles/apps /global/home/groups/consultsw/sl-7.x86_64/modfiles
    module load vim
fi

# added by Miniconda3 installer
# >>> conda init >>>
# !! Contents within this block are managed by 'conda init' !!
 __conda_setup="$(CONDA_REPORT_ERRORS=false '/global/home/users/$USER/miniconda3/bin/conda' shell.bash hook 2> /dev/null)"
 if [ $? -eq 0 ]; then
     \eval "$__conda_setup"
 else
     if [ -f "/global/home/users/$USER/miniconda3/etc/profile.d/conda.sh" ]; then
         . "/global/home/users/$USER/miniconda3/etc/profile.d/conda.sh"
         CONDA_CHANGEPS1=false
         conda activate base
     else
         \export PATH="/global/home/users/$USER/miniconda3/bin:$PATH"
     fi
 fi
 unset __conda_setup

# ssh keys
eval "$(ssh-agent -s)" > /dev/null
ssh-add ~/.ssh/github > /dev/null

# export environment variables
export TMPDIR=~/tmp
export PATH="$PATH:/global/home/users/psudmant/local_modules_sw/sratoolkit/sratoolkit.2.9.6-centos_linux64/bin"

# load global modules
module load git
module load gcc/6.3.0
module load java
# module load gsl
module load rclone
