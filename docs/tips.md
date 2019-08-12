# Tips

## How can I prevent bulker activate from creating a new shell?

Add this to your `.bashrc`:

```

bulker-activate() {
  eval "$(bulker activate $1 -e)"
}

```

now use `bulker-activate` instead of `bulker activate`.