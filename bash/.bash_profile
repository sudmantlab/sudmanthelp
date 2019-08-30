# .bash_profile

# echo ".bash_profile is sourced"

# .bash_profile is sourced when you log in to any node
# unlike .bashrc which is not sourced when you log in to dtn node
# to make our life simple, we source .bashrc here.

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi
