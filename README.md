#Lyratic Resolution

Lyratic Resolution is a blog engine I wrote for two reasons: I wanted more control over my blog's appearance and features, and I wanted to learn Python. Mike Shea's [Pueblo][1] really helped me to learn, so I thought I'd stick this up so that other people might learn from it.

The script expects a folder filled with [markdown][2] files and [mustache][3] templates. If you throw [scss][4] files in there too, they'll be processed as well, assuming you have [pyScss][5] installed. Speaking of assumptions: you'll need  [Markdown][6],  [mdx_smartypants][7] and [Pystache][8] for the script to work at all.

Metadata is included in a [YAML][9] block at the start of each post file: Title and Date are required keys, Tags and Abstract are optional. There is an example post, as well as generic templates and a scss file, in the "example input" folder. Find and replace "www.example.com", "Blog Title" and "author", and you'll have a fully-functioning, [Creative Commons licensed][10] blog.

Have fun!


[1]: https://github.com/mshea/pueblo
[2]: http://daringfireball.net/projects/markdown/
[3]: http://mustache.github.io/
[4]: http://sass-lang.com/
[5]: https://github.com/Kronuz/pyScss
[6]: https://pypi.python.org/pypi/Markdown
[7]: https://bitbucket.org/jeunice/mdx_smartypants
[8]: https://github.com/defunkt/pystache
[9]: http://yaml.org/
[10]: http://creativecommons.org/licenses/by-nc/4.0/
