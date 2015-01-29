#Lyratic Resolution

Lyratic Resolution is a blog engine I wrote for two reasons: I wanted more control over [my blog][1]'s appearance and features, and I wanted to learn Python. Mike Shea's [Pueblo][2] really helped me to learn, so I thought I'd stick this up so that other people might learn from it.

The script expects a folder filled with [markdown][3] files and [mustache][4] templates. If you throw [scss][5] files in there too, they'll be processed as well, assuming you have [pyScss][6] installed. Speaking of assumptions: you'll need  recent [Markdown][7] and [Pystache][8] in your path for the script to work at all.

Arbitrary metadata can be included in a [YAML][9] block at the start of each post file: `Title` and `Date`  will be determined from the filename and modification date, but only if they are not found in the file. There is an example post, as well as generic templates and a css file, in the "example input" folder. Find and replace `URL`, `BLOG TITLE` and `AUTHOR`, and you'll have a fully-functioning, [Creative Commons licensed][10] blog.

Have fun!


[1]: https://d.mcni.ch/blog/
[2]: https://github.com/mshea/pueblo
[3]: http://daringfireball.net/projects/markdown/
[4]: http://mustache.github.io/
[5]: http://sass-lang.com/
[6]: https://github.com/Kronuz/pyScss
[7]: https://pypi.python.org/pypi/Markdown
[8]: https://github.com/defunkt/pystache
[9]: http://yaml.org/
[10]: http://creativecommons.org/licenses/by-nc/4.0/
