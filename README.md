#Lyratic Resolution

Lyratic Resolution is a blog engine I wrote for two reasons: I wanted more control over my blog's appearance and features, and I wanted to learn Python. I don't think it's very good, but Mike Shea's [Pueblo](https://github.com/mshea/pueblo) really helped me to learn, so I thought I'd stick this up so that other people might learn from it.

The script expects a folder filled with [markdown](http://daringfireball.net/projects/markdown/) files and [mustache](http://mustache.github.io/) templates. If you throw [scss](http://sass-lang.com/) files in there too, they'll be processed as well, assuming you have pyScss installed.

Metadata is included in a [YAML](http://yaml.org/) block at the start of each post file: Title and Date are required keys, Tags and Abstract are optional.

Have fun!