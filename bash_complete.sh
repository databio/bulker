_bulker_complete() {
  local cur prev

  COMPREPLY=()
  cur=${COMP_WORDS[COMP_CWORD]}
  prev=${COMP_WORDS[COMP_CWORD-1]}

  if [ $COMP_CWORD -eq 1 ]; then
    cmds=`bulker --commands`
    COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
  elif [ $COMP_CWORD -eq 2 ]; then
    case "$prev" in
      "run")
        cmds=`bulker list --simple`
        COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
        ;;
      "activate")
        cmds=`bulker list --simple`
        COMPREPLY=( $(compgen -W "${cmds}"  -- ${cur}) )
        ;;
      *)
        COMPREPLY=()
        ;;
    esac
  fi
  
  return 0
} && complete -F _bulker_complete bulker