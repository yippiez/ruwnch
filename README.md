# Ruwnch

ruwnch is a simple program that watches a file or **files** for change and executes a command when that change or changes happens.

## Usage

Using ruwnch is simple, first argument is the file or files to be watched and the second one is the command or command per file to execute.

### Syntax

```bash
$ ruwnch <filepath: string | List[string]> <shellcommand: string | List[string]>
```

### Example Usage

For single file single command
```bash
$ ruwnch generate.py "python3 generate.py"
```

For multiple file single command

```bash
$ ruwnch "[generate.py, util.py]" "python3 generate.py"
```

For multiple file multiple command

```bash
$ ruwnch "[generate.py, util.py]" "[python3 generate.py, python3 util.py]"
```

> In multi to multi mode the number of commands must match the number of files

> Also don't have **,** as anything other than seperator.

## Executing last

ruwnch can also execute the last command if you just type `ruwnch last`. This is cached every run and can be disabled in the config. 

### Example Output

Below is an example of what the output will be. Note that the terminal the command was run has to stay open for the process to stay alive i.e. runch to do it's watching.
```bash
$ ruwnch generate.py "python3 generate.py"
> runwch started...
> checking changes every 60 seconds
> [05/08/2024 21:15] Change deteccted in 'generate.py' running comand.
...
> ERROR when running "python3 generate.py" here is stderr:
...
```

## Errors

if there is an error running the command given ruwnch will display the error but it won't stop executing.

This behaviour can be changed in config to stop the execution if an error occurs.

## Config

There are few options that can be changed in ruwnch runtime. These are done using the config.json provided.

> config.json has to be in the same directory as ruwnch

```json
{
    "checkPeriod": <int> 60 - The time between each file check
    "useColorama": <bool> Use colorama optional dependency
    "enableHashCache": <bool> true - Enables the files hashes to be cached 
    "enableLastCommandCache": <bool> true - Enables the usage "ruwnch last"
    "quitOnError": <bool> false - If set quits when there is an error
}
```

## How does it work?

Given a set of files ruwnch will calculate a hash for each of the files present. At specified (in the config) check periods ruwnch will re-calculate the files hash values and compare them to the last checked value. If the two values don't match ruwnch will simply run the command provided.

> Note that, if specified otherwise in the config, ruwnch will cache the results of previous hash calculations in a file called ruwnch.cache.json. If the program is stopped and re-launched it will find and use these hashes. So if you stop the program and run it after changin the files, ruwnch will **EXECUTE YOUR COMMANDS**. So be carefull.

## Examples

There is an example on basic txt file writing in the `.examples` folder.

## Dependencies

ruwnch doesn't have any required dependencies; only has **[colorama](https://pypi.org/project/colorama/)** as an optional dependency, for terminal formatting. This can be disabled in the configs.
