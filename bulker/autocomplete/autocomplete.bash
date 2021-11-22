# begin bulker bash completion
_bulker_autocomplete()
{
   local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    # opts=$(mm -l)
    opts=$(bulker list --simple)
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -o nospace -F _bulker_autocomplete bulker
# end bulker bash completion


_bulker_autocomplete_layer()
{
    local cur prev opts1 opts2
    cur=${COMP_WORDS[COMP_CWORD]}
    prev=${COMP_WORDS[COMP_CWORD-1]}
    opts1=$(bulker --commands)
    opts2=$(bulker list --simple)
    case ${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "${opts1}" -- ${cur}))
            ;;
        2)
            case ${prev} in
                activate)
                    COMPREPLY=($(compgen -W "${opts2}" -- ${cur}))
                    ;;
                *)
                    COMPREPLY=()
                    ;;
            esac
            ;;
        *)
            COMPREPLY=()
            ;;
    esac
}

complete -o bashdefault -o default -F _bulker_autocomplete_layer bulker
