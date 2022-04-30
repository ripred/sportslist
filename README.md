# Description

This python3 script will retrieve today's MLB or NHL games and
display them ordered by start time, in your local time.  
This is written using [my other nhl api repo](https://github.com/ripred/nhlapi)

You can edit the file to set your favorite teams and rivals in
order to see them highlighted in color in the output.

This script is very useful in combination with GeekTool or Conky!

# Running the script

Invoke the script using:

#### `python3 sports.py [i k t c h b]`

## Options:
- i = Use Bright Colors to hightlight favorite or rival teams
- k = Use black background
- t = color the time bright white
- c = use ANSI color in output (required for any other color related options)
- n = stop using ANSI color in output
- h = include hockey games in output
- b = include baseball games in output

*Note that the option flags are evaluated in order and affect only the output
specified (h or b) that comes after them.  This allows you to turn on and off
output decorations while outputting the list.*

## Example Use:

#### `python3 sports.py c t h`

