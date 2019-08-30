# Highlights

## Basic bash function

- you can use `cd -n` and `cd n` in `.bash_functions` to navigate through `cd` history. Meanwhile `lcd` helps you print your history

- Tired of `cd ..`? Try `up n`! It will bring you up `n` levels

- `dtsv` and `dcsv` can help you print .tsv and .csv files in a tidy format

- `lr` in `.bash_path` gives you a easy way to store your favorite paths.

## Basic SLURM function (Savio jobs)

- `snode` is a simple way to ask for an interactive node

- `sstatus` helps you check the status of your jobs. By default, it prints the most recent one

- `scheck` can check running jobs or any job with a given id

- `sshow` and `stui` monitor the CPU usage and parameters of the most recent job

- `sview` jumps into the running job. By default, it jumps into the most recent one so you can run bash commands like `top`
