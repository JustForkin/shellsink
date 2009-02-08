# number of lines kept in history
export HISTSIZE=1000
# number of lines saved in the history after logout
export SAVEHIST=1000
# location of history
export HISTFILE=~/.zhistory
# append command to history file once executed
setopt inc_append_history
# execute shellsink before a new command is run
function precmd {         
  /path/to/shellsink-client;
}
